# parsingdata.py

import requests
from bs4 import BeautifulSoup
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
querylist=[('corporate responsibility','')
           ,('corporate social responsibility','')
           ,('corporate philantropy','')
           ,('ESG','')]
           #add location in the second quotation marks if you have preference:
           #,('corporate responsibility', 'New York, NY')
           
URLS=[]
for position, location in querylist:
    URL = make_url(position, location)
    URLS.append(URL)
    
print('The list of initial search links:\n', URLS)

# create the list of links to the search pages
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
    # if you want to include ads change the last part to ('/pagead/' in x or '/rc/' in x)
    pages=["https://www.indeed.com"+x for x in links if x is not None and '/rc/' in x]
    jobpages = jobpages + pages
    

# here code for all search queries to go through all the search pages to get 
# all the job links     
print('Number of relevant job postings: \n', len(jobpages))
jobpages = list(set(jobpages))
print('Number of relevant job postings without duplicates: \n', len(jobpages))
    
# print(jobpages)

# Now here is the part that extracts all the data from the job pages
# needed variablees
title = ''
organization = ''
orglink = ''
var = ''
remote=''
location=''
city = ''
state = ''
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
df = pd.DataFrame(columns=['title', 'location', 'city', 'state', 'remote', 'jobtype', 'organization'
                           , 'orglink', 'rating', 'rating_count', 'salary_text', 'salary','salary_av'
                           , 'description', 'posted', 'joblink'])   
    
salary_pattern = re.compile(r'[0-9]+(?:[,][0-9]+)*[.]?[0-9]*') 
num_pattern = re.compile(r'\d+') 
stars_pattern = re.compile(r"\d+\.?\d*")
salaryKpattern = re.compile(r'(?:[0-9]+(?:[,][0-9]+)*[.]?[0-9]*[Kk])')
extrasymbolspattern = re.compile(r'((?<=-\s\s))?.*')
city_pattern = re.compile(r'.*(?=,)')
state_pattern = re.compile(r'(?<=,)\s+[A-Z]+')
not_parsed_jobs=[]

for url in jobpages:
    
    joblink = url
    
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    
    try:
        title = soup.find(attrs = {'class':'icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title'}).text
    except:
        # there are links to other websites sometimes, and this code in only suitable for indeed.com
        not_parsed_jobs.append(url)
        continue 
    
    try:
        var = soup.find(attrs = {'class':'icl-u-xs-mt--xs icl-u-textColor--secondary jobsearch-JobInfoHeader-subtitle jobsearch-DesktopStickyContainer-subtitle'})
        varloc = var.find_all('div', attrs = {'class':''})
        remote = varloc[-1].text
        location = varloc[-3].text
    except:
        remote = ''
        location = ''
    
    try:
        city = city_pattern.search(location).group()
        state = state_pattern.search(location).group()
    except:
        city = None
        state = None
        
    if location == "Remote":
        remote = location
    
    # job type    
    if soup.find('span',attrs={'class':'jobsearch-JobMetadataHeader-item icl-u-xs-mt--xs'})!=None:
        jobtype = soup.find('span',attrs={'class':'jobsearch-JobMetadataHeader-item icl-u-xs-mt--xs'}).text
        if "-  " in jobtype:
            jobtype = re.findall(extrasymbolspattern,jobtype)[0]

    
    varorg = var.find_all(attrs = {'class':'icl-u-lg-mr--sm icl-u-xs-mr--xs'})
    organization = varorg[-1].text
    try:
        orglink = varorg[-1].find('a').get('href')
    except:
        orglink = None

    #rating
    try:
        rating = float(soup.find('meta', attrs={'itemprop':'ratingValue'}).get('content'))
        rating_count = int(soup.find('meta', attrs={'itemprop':'ratingCount'}).get('content'))
    except:
        rating = None
        rating_count = None
    
    #salary
    if soup.find(attrs = {'class':'icl-u-xs-mr--xs attribute_snippet'})!=None:
        salary_text = soup.find(attrs = {'class':'icl-u-xs-mr--xs attribute_snippet'}).text
        
        ##### The rest of the salary part does not work as planned,
        ##### so I leave the text field as a variable in the df
        salary = re.findall(salary_pattern, salary_text)
        #get rid of commas
        salary = [float(i.replace(',','')) for i in salary]

        # if salary is per month
        if 'month' in salary_text:
            salary = [int(i * 12) for i in salary]
        #if salary is given per week (assumption: 52 weeks)
        if 'week' in salary_text:
            salary = [int(i * 52) for i in salary]
        #if hourly wage given (assumption: 40 hrs per week)
        if 'hour' in salary_text:
            salary= [int(i *40 *52) for i in salary]
                        
        # if salary is not given and there is a salary guide
    elif soup.find(attrs={'id':'salaryGuide'})!=None:
        salary_text = soup.find(attrs={'id':'salaryGuide'}).text
        salary = re.findall(salary_pattern, salary_text)
        salary = [float(i.replace(',','')) for i in salary]
        
        # salary is given in thousands
        if re.findall(salaryKpattern, salary_text)!=None:
            salary = [int(i * 1000) for i in salary]

     
        
    # create a variable with average salary        
    try:
        salary_av = sum(salary)/len(salary)
    except:
        salary_av=None

    
    # job description    
    try:
        description = soup.find(attrs = {'id':'jobDescriptionText'}).text.strip()
    except:
        description = ''
    
    
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
    
    
    # How many days ago the job posting was made:
    var = soup.find(attrs = {'class':'jobsearch-JobMetadataFooter'})
    varloc = var.find_all('div', attrs = {'class':''})
    
    if "Just" in varloc[0].text or "Today" in varloc[0].text:
        posted = 0
    elif "30+" in varloc[0].text:
        posted = 31 # = 31 if more than 30 days
    else:
        posted = num_pattern.findall(varloc[0].text)[0]

    # create a df with data on the new job
    appended_df = pd.DataFrame([[title, location, city, state, remote, jobtype, organization
                               , orglink, rating, rating_count, salary_text, salary, salary_av
                               , description, posted, joblink]], 
                               columns=['title', 'location',  'city', 'state', 'remote', 'jobtype', 'organization'
                                        , 'orglink', 'rating', 'rating_count', 'salary_text', 'salary','salary_av'
                                        , 'description', 'posted', 'joblink'])     
    
    # add data to the main df
    df = pd.concat([appended_df, df], axis=0, ignore_index=True) 
    
    salary_text = None
    salary=[]
    salary_av = None
    city = ''
    state = ''

print("The number of jobs that were not parsed because the link led to a different website:", len(not_parsed_jobs))
          
df.head()
df.to_excel("jobs.xlsx")

    
    
# Some Analysis

byorg=df.groupby(['organization']).size().reset_index(name='counts')
byorg.sort_values(['counts'],ascending=False).groupby('organization').head()

#                             organization  counts
#     257                   Neiman Marcus      41
#     200       JPMorgan Chase Bank, N.A.      21
#     199                             JLL      21
#     20          Amazon.com Services LLC      14
#     206                            KPMG      10
#     ..                              ...     ...
#     164                        Goby Inc       1
#     163           Geosyntec Consultants       1
#     162                Genomatica, Inc.       1
#     161                 Genomatica, Inc       1
#     430  thyssenkrupp Materials NA Inc.       1
    
# So, there are 431 organizations in my dataset, and Neiman Marcus is the one 
# that is developing the most actively in the field in terms of hiring new people at the moment.
# Most of the top organizations here belong to big tech of are financial organizations.

bycity=df.groupby(['city']).size().reset_index(name='counts')
bycity.sort_values(['counts'],ascending=False).groupby('city').head()

#               city  counts
# 84        New York      71
# 141     Washington      25
# 117  San Francisco      15
# 24         Chicago      14
# ..             ...     ...
# 1          Allegan       1
# 34   Daytona Beach       1
# 72        Melville       1
# 71          McLean       1
# 147         Woburn       1

# So, there are 148 cities in the search results, and NYC and Washington are 
# expectedly occupying the first two rows. The next two most popular cities right now
# are San Francisco, and Chicago, which I did not initially expect, as I was not 
# looking for jobs in Chicago before.


bystate=df.groupby(['state']).size().reset_index(name='counts')
bystate.sort_values(['counts'],ascending=False).groupby('state').head()
    
# 23    NY      82
# 3     CA      56
# 6     DC      25
# 10    IL      23
# 14    MA      18
# 33    WA      15
# 30    TX      15

# Apparently, there are a lot of jobs in California in places other  than San Francisco,
# as the state climbed on the second spot in the by state summary table.


    