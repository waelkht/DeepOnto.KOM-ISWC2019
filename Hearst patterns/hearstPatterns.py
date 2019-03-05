import re
import nltk
import os
import codecs
from nltk.tag.perceptron import PerceptronTagger



# Refined version form hearst patterns extraction https://github.com/mmichelsonIF/hearst_patterns_python
# supporting mult word terms and filtering suth , other as adjectives for the noun phrases
# cleaning the list of hyponyms from stopwords, duplicates, siguralization,......
from textblob.en.inflect import singularize


class HearstPatterns(object):
    def __init__(self):
        self.__chunk_patterns = r""" #  helps us find noun phrase chunks
         				NP: {<DT|PP\$>?<JJ>*<NN>+}
 					{<NNP>+}
 					{<NNS>+}
        		"""
        self.__np_chunker = nltk.RegexpParser(self.__chunk_patterns)  # create a chunk parser

        # now define the Hearst patterns
        # format is <hearst-pattern>, <general-term>
        # so, what this means is that if you apply the first pattern, the firsr Noun Phrase (NP)
        # is the general one, and the rest are specific NPs
        self.__hearst_patterns = [
            ("(NP_\w+ (, )?such as (NP_\w+ ? (, )?((and |or )NP_\w+)?)+)", "first"),  #
            ("(such NP_\w+ (, )?as (NP_\w+ ?(, )?(and |or )?)+)", "first"),
            ("((NP_\w+ ?(, )?)+(and |or )?other NP_\w+)", "last"),
            ("(NP_\w+ (, )?including (NP_\w+ ?(, )?(and |or )?)+)", "first"),
            ("(NP_\w+ (, )?especially (NP_\w+ ?(, )?(and |or )?)+)", "first"),
        ]

        self.__pos_tagger = PerceptronTagger()

    # divid text into sentences, tokenze the setnences and add par of speech tagging
    def prepare(self, rawtext):
        sentences = nltk.sent_tokenize(rawtext.strip())  # NLTK default sentence segmenter
        sentences = [nltk.word_tokenize(sent) for sent in sentences]  # NLTK word tokenizer
        sentences = [self.__pos_tagger.tag(sent) for sent in sentences]  # NLTK POS tagger

        return sentences

    # apply chunking step on the setences using the defined grammer for extracting nounphrases
    def chunk(self, rawtext):
        sentences = self.prepare(rawtext.strip())

        all_chunks = []
        for sentence in sentences:
            chunks = self.__np_chunker.parse(sentence)  # parse the example sentence
            all_chunks.append(self.prepare_chunks(chunks))
        return all_chunks

    # annotate the np with a prefiy NP_ also exclude the other and such from NP to be used in the patterns
    def prepare_chunks(self, chunks):
        # basically, if the chunk is NP, keep it as a string that starts w/ NP and replace " " with _
        # otherwise, keep the word.
        # remove punct
        # this is all done to make it super easy to apply the Hearst patterns...

        terms = []
        for chunk in chunks:
            label = None
            try:  # gross hack to see if the chunk is simply a word or a NP, as we want. But non-NP fail on this method call
                label = chunk.label()
            except:
                pass

            if label is None:  # means one word...
                token = chunk[0]
                pos = chunk[1]
                if pos in ['.', ':', '-', '_']:
                    continue
                terms.append(token)
            else:
                if chunk[0][0]=='such':
                    np = "such NP_" + "_".join([a[0] for a in chunk[1:]])
                elif chunk[0][0]=='other':
                    np = "other NP_" + "_".join([a[0] for a in chunk[1:]])
                else:
                    np = "NP_" + "_".join([a[0] for a in chunk])  # This makes it easy to apply the Hearst patterns later
                terms.append(np)
        return ' '.join(terms)

    # main method for extracting hyponym relations based on hearst patterns
    def find_hyponyms(self, folderpath,stopWord):
        all_sentences=list()
        hyponyms = []

        filelist = os.listdir(folderpath)
        for filePath in filelist:
            print ("processing file ","........................",filePath)
            file = codecs.open(folderpath + "//" + filePath, "r", encoding='utf-8', errors='ignore')
            lines = file.readlines()
            rawtext=(''.join(lines))
            rawtext=rawtext.lower()
            np_tagged_sentences = self.chunk(rawtext)
            for raw_sentence in np_tagged_sentences:
                # two or more NPs next to each other should be merged into a single NP, it's a chunk error
                # find any N consecutive NP_ and merge them into one...
                # So, something like: "NP_foo NP_bar blah blah" becomes "NP_foo_bar blah blah"
                sentence = re.sub(r"(NP_\w+ NP_\w+)+", lambda m: m.expand(r'\1').replace(" NP_", "_"), raw_sentence)
                # print  sentence
                for (hearst_pattern, parser) in self.__hearst_patterns:
                    matches = re.search(hearst_pattern, sentence)

                    if matches:
                        match_str = matches.group(1)
                        nps = [a for a in match_str.split() if a.startswith("NP_")]
                        if parser == "first":
                            general = nps[0]
                            specifics = nps[1:]
                        else:
                            general = nps[-1]
                            specifics = nps[:-1]
                        for i in range(len(specifics)):
                            if i==0:
                                e2=general.replace("NP_", "").replace("_", " ")
                                e1=specifics[0].replace("NP_", "").replace("_", " ")
                                clean_sen=sentence.replace("NP_", "").replace("_", " ")
                                clean_sen=clean_sen.replace(e1,"<e1>"+e1+"</e1>").replace(e2,"<e2>"+e2+"</e2>")
                                all_sentences.append(clean_sen.replace("NP_", "").replace("_", " "))
                                #print(clean_sen)
                            #print(general, specifics[i])
                            hyponyms.append(( self.clean_hyponym_term(general),self.clean_hyponym_term(specifics[i])))
            file.close()

        return self.refine_hyponym_term(hyponyms,stopWord),all_sentences

    def clean_hyponym_term(self, term):
        return term.replace("NP_", "").replace("_", " ")

    # remove stopwprds and sniguralize specfic and general concepts
    def refine_hyponym_term(self,hyponyms,stopWord):
        cleanedHyponyms=[]
        with open(stopWord) as f:
            stopWords = f.read().splitlines()

        for hyponym in hyponyms:
            #print(hyponym)
            specific = ' '.join([i for i in hyponym[1].split(' ') if not any(w == i.lower() for w in stopWords)])
            general = ' '.join([i for i in hyponym[0].split(' ') if not any(w == i.lower() for w in stopWords)])
            if specific == '' or general=='':
                print ('skipped relation: ', hyponym[1], 'is a ', hyponym[0])
                continue
            cleanedHyponyms.append((singularize(general) ,singularize(specific)))

        cleanedHyponyms.sort()
        return self.remove_duplicates(cleanedHyponyms)

    # remove duplicates in hyonym list
    def remove_duplicates(self, seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

