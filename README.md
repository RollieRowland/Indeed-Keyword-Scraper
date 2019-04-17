# Multiprocessing Indeed Job Scraper and Keyword Analysis

Indeed Job Scraper for multiple cities and job roles. This is an updated version of code presented by Michael Salmon in https://medium.com/@msalmon00/web-scraping-job-postings-from-indeed-96bd588dcb4b with added functionality of fetching full text from job source.

This fork of the code adds functionality for running multiple http requests concurrently and for processing the job descriptions for searching for keywords and key phrases on a per query basis per city. This also includes functionality for generating the keywords and key phrases for all collected keywords and phrases.

US Population per state found on https://datamarket.com/data/set/4m86/us-population-by-state-and-county

## Requirements
Keyword analysis is completed through using RAKE (Rapid Automatic Keyword Extraction) by csurfer based on [Automatic keyword extraction from individual documents by Stuart Rose, Dave Engel, Nick Cramer and Wendy Cowley](https://www.researchgate.net/profile/Stuart_Rose/publication/227988510_Automatic_Keyword_Extraction_from_Individual_Documents/links/55071c570cf27e990e04c8bb.pdf)
rake-nltk: https://github.com/csurfer/rake-nltk

> pip3 install rake-nltk
> pip3 install pandas


## Running
---File cleanup and generalization isn't complete yet, so directories will need to be set directly in the code for now.

Running this takes three separate processes. First the main.py is ran to pull the data for each job listing and stores it in a csv, which is done via:
>python3 main.py

The second process individually parses each job query per city, then extracts keywords and key phrases. This data is then stored in a csv file on a per query and city basis done via:
>python3 individualParser.py

The third process reads and combines all of the data produced in process two then extracts the keywords and phrases per query. Which will generate a csv for each query, this is done with:
>python3 multiParser.py


## Logs

Logs will be gerenated in **log.txt** file. Install watch to keep a track while running scraper in background.

> watch tail -n 30 log.txt

## Output

Files with prefix jobs_[num].csv would be generated, where **num** represent the index of the two loops running for fetchign data.
