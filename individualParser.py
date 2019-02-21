import glob
import time
import csv
import os
import sys
import ntpath
import multiprocessing
import pandas as pd
from rake_nltk import Rake

processCount = 16
parentDirectory = 'C:/Users/Rollie/Google Drive/School/Grad School/2019 Spring/Scholarship Seminar/Research Project (Scholarship Seminar)/LiveData2'
keywordDirectory = 'C:/Users/Rollie/Google Drive/School/Grad School/2019 Spring/Scholarship Seminar/Research Project (Scholarship Seminar)/KeywordData1'
file = 0

def extractKeywords(filename, number, city, query):
    try:
        r = Rake()
        data = list(csv.reader(open(filename, encoding='utf-8'), delimiter=","))

        description = ''

        for row in data:
            description += str(row[11])

        r.extract_keywords_from_text(description)
        keywords = r.get_ranked_phrases_with_scores()

        df = pd.DataFrame(columns = ['rank', 'keyword_set'])
        num = 0

        for pair in keywords:
            num = (len(df) + 1)
            df.loc[num] = pair


        dirtitle =  number + '_' + city + '_' + query + '.csv'
        if not os.path.exists(keywordDirectory):
            os.mkdir(keywordDirectory)

        filenamelocation = os.path.join(keywordDirectory, dirtitle)

        try:
            #print("Creating keyword file for " + city + " with query " + query)

            df.to_csv(filenamelocation, encoding='utf-8')
        except:
            print('Failed on ' + filenamelocation)

        print('.', end='')
        sys.stdout.flush()

    except Exception as e:
        print(e)

if __name__ == '__main__':

    filenames = []

    for filename in glob.glob(os.path.join(parentDirectory, '*.csv')):
        print(filename)
        filenames.append(filename)

    fileIndex = 0

    for filename in filenames[::processCount]:
        filePool = multiprocessing.Pool(processes=processCount)
        fileManager = multiprocessing.Manager()
        #fileQueue = fileManager.Queue()

        print("Processing file " + str(fileIndex) + " of " + str(len(filenames)))

        for i in range(processCount):
            if fileIndex < len(filenames):
                name = ntpath.basename(filenames[fileIndex]).split('_')

                filePool.apply_async(extractKeywords, (filenames[fileIndex], name[0], name[1], name[2].split('.')[0]))
                fileIndex += 1

        filePool.close()
        filePool.join()

        print("")
