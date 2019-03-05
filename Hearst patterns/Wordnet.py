from nltk.corpus import wordnet as wn
import networkx as nx
import sys
import matplotlib.pyplot as plt
from nltk.corpus.reader import NOUN
def main():
#http://parrotprediction.com/dive-into-wordnet-with-nltk/


    sys.setrecursionlimit(10000000)
    word = wn.synset('entity.n.01')

    # get all hyponyms in a subtree of wordnet
    hyponyms = get_synset_hyponym(word,[])
    hyponyms.sort()
    print "Hyponyms:",len(hyponyms) ,hyponyms
    # export data
    with open('WordnetHyponym.csv', 'wb') as f:
        for s in hyponyms:
            f.write(s[0] + ',' + s[1] + '\n')


    # get all hypernyms in a subtree of wordnet
    hypernyms = get_hypernyms(word)
    print "Hypernyms:",len(hypernyms), hypernyms

    # get all get_synsets in a subtree of wordnet
    synonyms = get_synset_synonyms(word,[])
    print "synonyms:",len(synonyms), synonyms
    # export data
    with open('synonyms.csv', 'wb') as f:
         for s in synonyms:
            f.write(s[0] + ',' + s[1] + '\n')


    # get all meronyms in a subtree of wordnet
    part_meronyms = get_synset_part_meronyms(word,[])
    print "Part_meronyms:",len(part_meronyms), part_meronyms
    # export data
    with open('Wordnet_part_meronyms.csv', 'wb') as f:
         for s in part_meronyms:
            f.write(s[0] + ',' + s[1] + '\n')

    # get all meronyms in a subtree of wordnet

    substance_meronyms = get_synset_substance_meronyms(word, [])
    print "Substance_meronyms:", len(part_meronyms), part_meronyms
    # export data
    with open('Wordnet_substance_meronyms.csv', 'wb') as f:
         for s in substance_meronyms:
              f.write(s[0] + ',' + s[1] + '\n')

# get all hyponyms in a subtree of wogive surdnet, their synonyms and myronyms
def get_synset_hyponym(synset, replicate):
    print 'hyponym',synset
    hyponyms = []
    for syn in wn.synsets(synset.lemma_names()[0]):
        for hyponym in syn.hyponyms():
            for synslemama in syn.lemma_names():
                for hyplemama in hyponym.lemma_names():
                    hyponyms.append((synslemama, hyplemama))

        if syn not in replicate:
            replicate.append(syn)
            for hyponym in syn.hyponyms():
                hyponyms.extend(get_synset_hyponym(hyponym,replicate))
    return hyponyms

def get_synset_part_meronyms(synset, replicate):
    print 'part meronyms', synset
    part_meronyms = []
    for syn in wn.synsets(synset.lemma_names()[0]):
        for part_meronym in syn.part_meronyms():
            for synslemama in syn.lemma_names():
                for partlemama in part_meronym.lemma_names():
                    part_meronyms.append((synslemama, partlemama))

        if syn not in replicate:
            replicate.append(syn)
            for part_meronym in syn.part_meronyms():
                part_meronyms.extend(get_synset_part_meronyms(part_meronym,replicate))
            for hyponym in syn.hyponyms():
                part_meronyms.extend(get_synset_part_meronyms(hyponym, replicate))
    return part_meronyms

def get_synset_substance_meronyms(synset, replicate):
    print 'substance meronym', synset
    substance_meronyms = []
    for syn in wn.synsets(synset.lemma_names()[0]):
        for substance_meronym in syn.substance_meronyms():
            for synslemama in syn.lemma_names():
                for partlemama in substance_meronym.lemma_names():
                    substance_meronyms.append((synslemama, partlemama))

        if syn not in replicate:
            replicate.append(syn)
            for substance_meronym in syn.substance_meronyms():
                substance_meronyms.extend(get_synset_substance_meronyms(substance_meronym,replicate))
            for hyponym in syn.hyponyms():
                substance_meronyms.extend(get_synset_substance_meronyms(hyponym, replicate))
    return substance_meronyms

def get_synset_synonyms(synset, replicate):
    print 'Synonyms', synset
    synonyms = []
    for syn in wn.synsets(synset.lemma_names()[0]):
        for synslemama in syn.lemma_names():
            if syn.lemma_names()[0] != synslemama:
                synonyms.append((syn.lemma_names()[0],synslemama))

        if syn not in replicate:
            replicate.append(syn)
            for synonym in syn.part_meronyms():
                synonyms.extend(get_synset_synonyms(synonym,replicate))
            for hyponym in syn.hyponyms():
                synonyms.extend(get_synset_synonyms(hyponym, replicate))
    return synonyms


# get all hypernyms in a subtree of wordnet
def get_hypernyms(synset):
    hypernyms = set()
    for hypernym in synset.hypernyms():
        hypernyms |= set(get_hypernyms(hypernym))
    return hypernyms | set(synset.hypernyms())

# remove duplicates in hyonym list
    def remove_duplicates(self, seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]


if __name__ == "__main__":
    main()

