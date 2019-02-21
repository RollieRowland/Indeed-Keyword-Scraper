import glob
import time
import csv
import os
import sys
import ntpath
import multiprocessing
import pandas as pd
from rake_nltk import Rake

processCount = 64
keywordDirectory = 'C:/Users/Rollie/Google Drive/School/Grad School/2019 Spring/Scholarship Seminar/Research Project (Scholarship Seminar)/KeywordData1'
totalKeywordDirectory = 'C:/Users/Rollie/Google Drive/School/Grad School/2019 Spring/Scholarship Seminar/Research Project (Scholarship Seminar)/TotalKeywordData'
file = 0

def parseCSV(q, filename, query):
    try:
        data = list(csv.reader(open(filename, encoding='utf-8'), delimiter=","))

        description = ''

        for row in data:
            description += str(row[2])

        q.put([query, description])

        print('.', end='')
        sys.stdout.flush()

    except Exception as e:
        print(e)

def extractKeywords(description, query):
    try:
        r = Rake()

        print("Extracting keywords from joined sequence with query: " + query)

        r.extract_keywords_from_text(description)

        print("Keywords extracted from text with query: " + query)

        keywords = r.get_ranked_phrases_with_scores()

        print("Extraction finished for query: " + query + " writing to file")

        df = pd.DataFrame(columns = ['rank', 'keyword_set'])

        for pair in keywords:
            num = (len(df) + 1)
            df.loc[num] = pair

        dirtitle =  query + '.csv'
        if not os.path.exists(totalKeywordDirectory):
            os.mkdir(totalKeywordDirectory)

        filenamelocation = os.path.join(totalKeywordDirectory, dirtitle)

        df.to_csv(filenamelocation, encoding='utf-8')

        print("File created for query: " + query)

    except Exception as e:
        print(e)

if __name__ == '__main__':

    filenames = []

    for filename in glob.glob(os.path.join(keywordDirectory, '*.csv')):
        print(filename)
        filenames.append(filename)

    fileIndex = 0
    description1 = ''
    description2 = ''
    description3 = ''
    description4 = ''

    for filename in filenames[0:256:processCount]:
        filePool = multiprocessing.Pool(processes=processCount)
        fileManager = multiprocessing.Manager()
        fileQueue = fileManager.Queue()

        print("Processing file " + str(fileIndex) + " of " + str(len(filenames)))

        for i in range(processCount):
            if fileIndex < len(filenames):
                name = ntpath.basename(filenames[fileIndex]).split('_')

                filePool.apply_async(parseCSV, (fileQueue, filenames[fileIndex], name[2].split('.')[0]))
                fileIndex += 1

        filePool.close()
        filePool.join()

        print("")

        while not fileQueue.empty():
            pair = fileQueue.get()
            if pair[0] == "InformationSystems":
                description1 += pair[1]
            elif pair[0] == "ManagementInformationSystems":
                description2 += pair[1]
            elif pair[0] == "BusinessInformationSystems":
                description3 += pair[1]
            elif pair[0] == "ComputerInformationSystems":
                description4 += pair[1]
            else:
                print("String comparison failure")


    print("Processing descriptions for each query")

    parsePool = multiprocessing.Pool(processes=4)
    parseManager = multiprocessing.Manager()

    parsePool.apply_async(extractKeywords, (description1, "InformationSystems"))
    parsePool.apply_async(extractKeywords, (description2, "ManagementInformationSystems"))
    parsePool.apply_async(extractKeywords, (description3, "BusinessInformationSystems"))
    parsePool.apply_async(extractKeywords, (description4, "ComputerInformationSystems"))

    parsePool.close()
    parsePool.join()
