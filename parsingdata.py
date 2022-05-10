# parsingdata.py

import requests
from bs4 import BeautifulSoup
import csv
import re
import pandas as pd

# Function that creates a URL based on a query
def make_url(position, location=''):
    template = 'https://www.indeed.com/jobs?q={}&l={}&limit=50' 
    #limit = number of pages per search; set to 50 to make parsing faster
    position = position.replace(' ', '%20')
    location = location.replace(' ', '%20')
    location = location.replace(',', '%2C')
    URL = template.format(position, location)
    return URL

# give query list and build search links based on queries
querylist=[('corporate responsibility', 'New York, NY')
            ,('corporate responsibility','')
            ,('corporate social responsibility','')
            ,('CSR','')]
URLS=[]
for position, location in querylist:
    URL = make_url(position, location)
    URLS.append(URL)
    
print('The list of initial search links:\n', URLS)

# create the list of search page links for the search
all_search_pages=[]
for URL in URLS:
    nextpage = URL
    while True:
        try:
            # getting code of the page        
            html = requests.get(nextpage)
            soup = BeautifulSoup(html.text, 'html.parser')
            # finding next page link
            nextpage = 'https://www.indeed.com' + soup.find('a', {'aria-label': 'Next'}).get('href')
            # appending it to the list of page links
            all_search_pages.append(nextpage)
        except AttributeError:
            break

print('The number of page links for the searches:\n', len(all_search_pages))


#### Parsing job page links
jobpages = []
for url in all_search_pages:
    
    links = []  
    
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    
    # gather all links to outside sources
    for alink in soup.find_all('a'):
        links.append(alink.get('href'))
    
    #create a list of relevant job pages
    pages=["https://www.indeed.com"+x for x in links if x is not None and ('/pagead/' in x or '/rc/' in x)]
    jobpages = jobpages + pages
    

# here code for all search queries to go through all the search pages to get 
# all the job links     
print('Number of relevant job postings: \n', len(jobpages))
jobpages = list(set(jobpages))
print('Number of relevant job postings without duplicates: \n', len(jobpages))
    
print(jobpages)

# Now here is the part that extracts all the data from the job pages
title = ''
organization = ''
orglink = ''
var = ''
remote=''
location=''
rating=None
rating_count=None
salary_text=''
salary=None
salary_av = None
jobtype=''
description=''
# benefits=[]
posted=''
joblink = ''
#the df that we are going to fill
df = pd.DataFrame(columns=['title', 'location', 'remote', 'jobtype', 'organization'
                           , 'orglink', 'rating', 'rating_count', 'salary_text'#, 'salary','salary_av'
                           , 'description', 'posted', 'joblink'])   

salary_pattern = re.compile(r'\d+(\,?\d+)*(\.?\d+)*') 
#the pattern above has an error, so I'm trying to find the correct one
num_pattern = re.compile(r'\d+') 
stars_pattern = re.compile(r"\d+\.?\d*")
permonth_pattern = re.compile(r'month')
perhour_pattern = re.compile(r'hour')
salaryKpattern = re.compile(r'(\d+,?\d+)+\.?\d*K')

#change the brackets to get all links' data parsed
for url in jobpages[:10]:
    
    joblink = url
    
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    
    title = soup.find(attrs = {'class':'icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title'}).text
    
    var = soup.find(attrs = {'class':'icl-u-xs-mt--xs icl-u-textColor--secondary jobsearch-JobInfoHeader-subtitle jobsearch-DesktopStickyContainer-subtitle'})
    varloc = var.find_all('div', attrs = {'class':''})
    remote = varloc[-1].text
    location = varloc[-3].text

    try:
        jobtype = soup.find(attrs = {'class':'jobsearch-JobMetadataHeader-item  icl-u-xs-mt--xs'}).text
    except:
        jobtype = ''
        
    varorg = var.find_all(attrs = {'class':'icl-u-lg-mr--sm icl-u-xs-mr--xs'})
    organization = varorg[-1].text
    try:
        orglink = varorg[-1].find('a').get('href')
    except:
        orglink = None

    #rating
    try:
        rating = "{:.2f}".format(float(stars_pattern.findall(soup.find(attrs={'class':'icl-Ratings-starsFilled'}).get('style'))[0]) / 9) #divide to get out of 10 rating
        rating_count = int(num_pattern.findall(soup.find(attrs={'class':'icl-Ratings-count'}).text.replace(',',''))[0])
    except:
        rating = None
        rating_count = None
    
    #salary
    try:
        salary_text = soup.find(attrs = {'class':'icl-u-xs-mr--xs attribute_snippet'}).text
        
        ##### The rest of the salary part does not work as planned,
        ##### so I leave the text field as a variable in the df
        salary = re.findall(salary_pattern, salary_text)
        for i in salary:
            i=i.replace(',','')
        # print(salary)
        # if salary is in thousands
        if re.findall(salaryKpattern, salary_text)!=None:
            for i in salary:
                salary[i] = float(salary[i])*1000
        # if salary is per month
        if re.findall(permonth_pattern, salary_text)!=None:
            for i in salary:
                salary[i] = float(salary[i])*12
        #if hourly wage given (assumption: 40 hrs per wek)
        if re.findall(perhour_pattern, salary_text)!=None:
            for i in salary:
                salary[i] = float(salary[i])*40*52
                
        # if salary is not given and there is a salary guide
        if soup.find(attrs={'id':'salaryGuide'})!=None:
            salary_text = soup.find(attrs={'id':'salaryGuide'}).text
            salary = re.findall(salary_pattern, salary_text)
            for i in salary:
                i=i.replace(',','')
            if re.findall(salaryKpattern, salary_text)!=None:
                for i in salary:
                    salary[i] = int(float(salary[i])*1000)
        
        # create a variable with average salary        
        salary_av = sum(salary)/len(salary)
    except:
        salary=[]
        salary_av = None
        
    # job description    
    description = soup.find(attrs = {'id':'jobDescriptionText'}).text.strip()
    
    ##### the list of benefits
    ##### this part would work but the website updates several seconds after 
    ##### you visit the page, so I delete theis variable form the df
    # try:
    #     var = soup.find_all('div', attrs = {'class':'mpci-tvvxwd ecydgvn1'})
    #     print(benefits)
    #     for i in benefits:
    #         benefits[i]=benefits[i].text
    # except:
    #     benefits=[]
       
    var = soup.find(attrs = {'class':'jobsearch-JobMetadataFooter'})
    varloc = var.find_all('div', attrs = {'class':''})
    posted = num_pattern.findall(varloc[0].text)[0]
    
    
    # create a df with data on the new job
    appended_df = pd.DataFrame([[title, location, remote, jobtype, organization
                               , orglink, rating, rating_count, salary_text#, salary, salary_av
                               , description, posted, joblink]], 
                               columns=['title', 'location', 'remote', 'jobtype', 'organization'
                                        , 'orglink', 'rating', 'rating_count', 'salary_text'#, 'salary','salary_av'
                                        , 'description', 'posted', 'joblink'])     
    
    # add data to the main df
    df = pd.concat([appended_df, df], axis=0, ignore_index=True)                 
df.head()
df.to_csv('jobs.csv', index=False, encoding='utf-8')

    ## Some Analysis
#biggest provider
df.groupby(['organization']).size()
#most highly rated org
df.sort_values(by=['rating'])

    
    
    
    
    
    
    
    
    
    
    
    
    
    