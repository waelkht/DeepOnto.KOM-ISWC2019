import hearstPatterns
import pickle

def main():
    h = hearstPatterns.HearstPatterns()
    folderpath="AI"
    stopWord = "stopwords.txt"
    hyponyms, sentences = h.find_hyponyms(folderpath,stopWord)
    if len(hyponyms) > 0:
        print(hyponyms)  # line)
    print("total number of relations: ",len(hyponyms))

    #export data
    with open('hyponyms.csv', 'w',encoding="UTF-8") as f:
        for s in hyponyms:
            f.write(str(s[0])+ ',' +str(s[1]) + '\n')

    with open('sentences.txt', 'w',encoding="UTF-8") as f:
        for s in sentences:
            f.write(s+ '\n')

if __name__ == "__main__":
    main()