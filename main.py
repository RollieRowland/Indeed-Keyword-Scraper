# import packages
import requests
import pandas as pd
import time
import csv
import os
import sys
import multiprocessing

from functions import *

def getRequest(integ, q, id, city, job_qry, job_title, company, location, summary, salary, link, date):
    job_post = []

    #append unique id
    job_post.append(id)

    #append city name
    job_post.append(city)

    #append job qry
    job_post.append(job_qry)

    #grabbing job title
    job_post.append(job_title)

    #grabbing company
    job_post.append(company)

    #grabbing location name
    job_post.append(location)

    #grabbing summary text
    job_post.append(summary)

    #grabbing salary
    job_post.append(salary)

    #grabbing link
    job_post.append(link)

    #grabbing date
    job_post.append(date)

    #grabbing full_text
    job_post.append(extract_fulltext(link))

    q.put(job_post)
    #print("Process " + str(integ) + " finished.")
    print('.', end='')
    sys.stdout.flush()

def getPage(q,job_qry,city,start):
    q.put(requests.get('http://www.indeed.com/jobs?q=' + job_qry +'&l=' + str(city) + '&start=' + str(start)))

    print('.', end='')
    sys.stdout.flush()

if __name__ == '__main__':
    # limit per city
    max_results_per_city = 100

    # db of city
    #city_set = ['New+York','Toronto','Las+Vegas','San+Franciso','Portland','Pittsburgh','Philadelphia','Vancouver','London','Chicago','Houston','Pheonix','San+Antonio','San+Diego','Dallas','San+Jose']
    data = csv.reader(open('cities.csv'), delimiter=",", quotechar='|')
    city_set = []

    for row in data:
        correctedString = row[1].replace(" ", "+")
        city_set.append(correctedString)

    # job roles
    job_set = ['Information+Systems','Management+Information+Systems','Business+Information+Systems','Computer+Information+Systems']

    # file num
    file = 1

    jobCount = 0

    # from where to skip
    SKIPPER = 0

    # loop on all cities
    for city in city_set:

        # for each job role
        for job_qry in job_set:

            # count
            cnt = 0
            startTime = time.time()

            # skipper
            if(file > SKIPPER):

                # dataframe
                df = pd.DataFrame(columns = ['unique_id', 'city', 'job_qry','job_title', 'company_name', 'location', 'summary', 'salary', 'link', 'date', 'full_text'])

                try:
                    pages = []
                    pagePool = multiprocessing.Pool(processes=24)
                    pageManager = multiprocessing.Manager()
                    pageQueue = pageManager.Queue()

                    print("Fetching links for " + job_qry + " in " + city + ".")

                    # for results
                    for start in range(0, max_results_per_city, 10):
                        pagePool.apply_async(getPage, (pageQueue,job_qry,city,start))
                        #page = requests.get('http://www.indeed.com/jobs?q=' + job_qry +'&l=' + str(city) + '&start=' + str(start))

                    pagePool.close()
                    pagePool.join()

                    while not pageQueue.empty():
                        pages.append(pageQueue.get())


                    divsArray = []

                    for page in pages:
                        #fetch data
                        soup = get_soup(page.text)
                        divs = soup.find_all(name="div", attrs={"class":"row"})

                        for div in divs:
                            divsArray.append(div)

                        # if results exist
                        if(len(divs) == 0):
                            break

                    if(len(divsArray) == 0):
                        break
                except:
                    print("Skipping city")

                try:
                    job_postings = []

                    processPool = multiprocessing.Pool(processes=24)
                    processManager = multiprocessing.Manager()
                    processQueue = processManager.Queue()

                    integ = 0

                    print("")
                    print("Processing job listings for " + job_qry + " in " + city + ".")
                    # for all jobs on a page
                    for div in divsArray:
                        integ += 1
                        processPool.apply_async(getRequest, (integ,processQueue,div['id'],city,job_qry,extract_job_title(div),extract_company(div),extract_location(div),extract_summary(div),extract_salary(div),extract_link(div),extract_date(div)))# getRequest(city, job_qry, job_title, company, location, summary, salary, link, date)

                    #print("Waiting on Join")
                    processPool.close()
                    processPool.join()

                    print("\r")

                    while not processQueue.empty():
                        job_postings.append(processQueue.get())

                    #print("Join finished " + str(len(job_postings)))

                    #print("Queue emptied")

                    for job_post in job_postings:
                        #specifying row num for index of job posting in dataframe
                        num = (len(df) + 1)
                        cnt = cnt + 1

                        jobCount = jobCount + 1

                        #appending list of job post info to dataframe at index num
                        df.loc[num] = job_post

                        print("File: " + str(file) + " Count: " + str(cnt) + " Total Job Count: " + str(jobCount) + "                    ", end='\r')
                        sys.stdout.flush()

                    print("")

                    #debug add
                    write_logs(('Completed =>') + '\t' + city  + '\t' + job_qry + '\t' + str(cnt) + '\t' + str(start) + '\t' + str(time.time() - startTime) + '\t' + ('file_' + str(file)))



                    outdir = 'C:/Users/Rollie/Google Drive/School/Grad School/2019 Spring/Scholarship Seminar/Research Project (Scholarship Seminar)/LiveData2'
                    dirtitle =  str(file) + '_' + city.replace("+", "") + '_' + job_qry.replace("+", "") + '.csv'
                    if not os.path.exists(outdir):
                        os.mkdir(outdir)

                    filenamelocation = os.path.join(outdir, dirtitle)

                    try:
                        #saving df as a local csv file
                        df.to_csv(filenamelocation, encoding='utf-8')
                    except:
                        write_logs('Failed on ' + filenamelocation)
                except:
                    print("Skipping result in city")

            else:
                #debug add
                write_logs(('Skipped =>') + '\t' + city  + '\t' + job_qry + '\t' + str(-1) + '\t' + str(-1) + '\t' + str(time.time() - startTime) + '\t' + ('file_' + str(file)))

            # increment file
            file = file + 1
