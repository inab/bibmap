# -*- coding: utf-8 -*-

import csv
import sys
import MySQLdb
import re
import unidecode
import string
import pickle

import json, requests, pprint

# Open database connection
db = MySQLdb.connect("","","","", charset = 'utf8' )

# Ferran Casals, Miguel Vazquez, Martin Krallinger, Salvador Capella, JL Gelpi (inx4)
# UPF, BSC, BSC, BSC, BSC+UB
orcids = ["0000-0002-8941-0369","0000-0002-5713-1058","0000-0002-2646-8782","0000-0002-0309-604X","0000-0002-0566-7723"]
affiltexts = ["Universitat Pompeu Fabra (UPF)", "Barcelona Supercomputing Center (BSC-CNS)", "Barcelona Supercomputing Center (BSC-CNS)", "Barcelona Supercomputing Center (BSC-CNS)", "Barcelona Supercomputing Center (BSC-CNS)"]
#print(row)

#sys.exit(1)
orcid = orcids[4]
nameaffiliation = affiltexts[4]
url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=AUTHORID%3A%22' + orcid + '%22&resultType=core&cursorMark=*&pageSize=1000&format=json'
#doi = row[3]
#source = "X"
data = requests.get(url=url).text

binary = json.loads(data)

#print(binary)

dois = []
citedby = []
titles = []
ids = []
years = []
authors = []
affiliations = []
inbOrNot = []

result = binary['resultList']['result']

for inx, element in enumerate(result):
    try:
        if element['doi'] == "doi":
            continue
        if(not element['doi']):
            continue
        if(not element['affiliation']):
            continue
    
        print(element)
        print(element['id'])
        dois.append(element['doi'])
        #sys.exit(1)
        
        citedby.append(element['citedByCount'])
        
        titles.append(element['title'])
        
        ids.append(element['id'])
        
        years.append(element['pubYear'])
        
            
        #affiliations.append(element['affiliation'])
        affiliationsPre = []
        affPrePre = []
        for author in element['authorList']['author']:
            try:
            #print(author['firstName'] + " " + author['lastName'])
                affiliationsPre.append(author['firstName'] + " " + author['lastName'])
                affPrePre.append(author['affiliation'])
            except Exception as e:
                print(e)
                continue
            
        affiliations.append("//".join(affPrePre))
        authors.append(", ".join(affiliationsPre))
        
        # Check for INB grant
        urlINBcheck = "https://www.ebi.ac.uk/europepmc/webservices/rest/" + element['id'] + "/fullTextXML"
        dataCheck = requests.get(url=urlINBcheck).text
        
        if "Spanish National Bioinformatics" in dataCheck or "(INB" in dataCheck or "[INB" in dataCheck or "Instituto Nacional" in dataCheck or "[PT1" in dataCheck:
            inbOrNot.append("Si")
            print("Si")
        else:
            print("No")
            inbOrNot.append("No")                    
        
    except Exception as e:
        print(e)
        continue
    
for inx, elem in enumerate(dois):
    try:
        cursor = db.cursor()
        
        dupQuery = "SELECT COUNT(*) FROM articles_bib_project WHERE title = \"";
        dupQuery += str(titles[inx]) + "\"";
        cursor.execute(dupQuery)
        result=cursor.fetchone()
        number_of_rows=result[0]

        if number_of_rows > 0:
            print("Duplicated!!!!!!!!!!!!")
            continue                    
        
        cursor.execute ("INSERT INTO articles_bib_project (nameaffiliation,title,doi,year,citations,authors,inb_grant) VALUES (%s,%s,%s,%s,%s,%s,%s)", (
            str(nameaffiliation),str(titles[inx]),str(dois[inx]),str(years[inx]),str(citedby[inx]),str(authors[inx]),str(inbOrNot[inx])))
        db.commit()
        
        cursor.execute ("INSERT INTO articles_bib_project (nameaffiliation,title,doi,year,citations,authors,inb_grant) VALUES (%s,%s,%s,%s,%s,%s,%s)", (
            "Universitat de Barcelona (UB)",str(titles[inx]),str(dois[inx]),str(years[inx]),str(citedby[inx]),str(authors[inx]),str(inbOrNot[inx])))
        db.commit()
    except Exception as e:
        print(e)
        continue
        
# disconnect from server
db.close()