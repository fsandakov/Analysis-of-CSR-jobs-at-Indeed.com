# CSR jobs at Indeed.com
CSR jobs at Indeed.com


Purpose of the analysis: 
The original purpose of the project was to analyze the offer of jobs from the corporate and social responsibility jobs at Indeed.com. During the project, the inconsistencies at the website's code (such as, for example, with salary posting) and the complexity of parsing data in general as oposed to using API, the purpose of the project shifted to creating a script that could help people make databases with information on available postings in their field of interest so that they would understand what really is on offer without having to go through the tiresome process of going through the search results and different queries. Using the result database, a person can see the information in a structured way and filter the positions in the way they want.

Input data:
The input data is the list of queries that is required from user to collect hob postings of interest.

Output:
The output is an Excel file "jobs.xsls" with field-specific current job postings database including 17 variables: title, location, city, state, remote (are remote/hybrid modes available), jobtype (full-time, part-time, contract), organization, orglink, rating (of the organization), rating_count (number of people who voted), salary_text (what was written in the according fields), salary (min and max if available), salary_av (average), description, posted (how many days ago was the job posted), joblink.

Script functions:
The script 'parsingdata.py' serves to parse the job offerings data from Indeed.com. The script is has a lot of comments, so it that it would be easy to use and adapt if needed.
The main parts of the code include:
1) Creation of links based on user's queries.
2) Parsing of the list of links to the search pages.
3) Parsing of the links to the job pages from the search results pages.
4) Parsing of data from the job posting pages and the creation of a database.
5) Quick analysis of the received data (offer of jobs by organization, city, and state).

Results:
The updated project idea was successfully implemented, and a database of 719 job postings in the area of CSR was created, among other datasets.
I find some of my coding solutions fantastic, as sometimes after several mig solutions I would find replacements for them that would only take one line of code and make everything pretty and concise. I used a lot of regex and became profficient in it, along with parsing. Idea-wise, I think my solution with putting all positions form different searches in one database is great, as sometimes searches overlap by up to 700 job postings, and time is too valuable to waste on looking at positions one has already considered.
The main problems included inconsistency in the way Indeed.com is coded, which caused a lot of errors and script adaptation on my side, and the fact that after several parsing efforts I had to start using a new VPN connection for each 100 of search results, as the searches would start to show void due to Indeed.com protection system.
As for results of my quick analysis, look below.
Counts by organization:

                            organization  counts
    257                   Neiman Marcus      41
    200       JPMorgan Chase Bank, N.A.      21
    199                             JLL      21
    20          Amazon.com Services LLC      14
    206                            KPMG      10
    ..                              ...     ...
    164                        Goby Inc       1
    163           Geosyntec Consultants       1
    162                Genomatica, Inc.       1
    161                 Genomatica, Inc       1
    430  thyssenkrupp Materials NA Inc.       1
    
So, there are 431 organizations in my dataset, and Neiman Marcus is the one that is developing the most actively in the field in terms of hiring new people at the moment. Most of the top organizations here belong to big tech of are financial organizations.



By city comparisson:

              city  counts
84        New York      71
141     Washington      25
117  San Francisco      15
24         Chicago      14
..             ...     ...
1          Allegan       1
34   Daytona Beach       1
72        Melville       1
71          McLean       1
147         Woburn       1

There are 148 cities in the search results, and NYC and Washington are expectedly occupying the first two rows. The next two most popular cities right now are San Francisco, and Chicago, which I did not initially expect, as I was not looking for jobs in Chicago before.



By state comparisson:

23    NY      82
3     CA      56
6     DC      25
10    IL      23
14    MA      18
33    WA      15
30    TX      15

Apparently, there are a lot of jobs in California in places other  than San Francisco, as the state climbed on the second spot in the by state summary table.
