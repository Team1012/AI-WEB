
import random
from ast import literal_eval

import requests


def validate_enrich_query(querytype, query):
    keywords = ['machine learning','Natural language Processing','Artificial neural networks', 'knowledge representation and reasoning','computer vision','Deep learning', 'Artificial intelligence', 'smart robotics','reinforcement learning']
    if querytype == 'Researchers':
        query = 'author:' + query
    # if querytype == 'Institutions':
    #     query = 'institution:' + query
    #     for x in (random.choices(keywords, k=1)):
    #         query = query+" "+ x
    # if querytype == 'publications':
    #     query = 'publication:' + query
    #     for x in (random.choices(keywords, k=1)):
    #         query = query+" "+ x
    # for x in keywords:
    #     query=query+x+' or '
    print(query)
    return query

def query_url(query):
    url = "https://serpapi.com/search?engine=google_scholar&q=" + query + "&apikey=74e03c8524cbfd71a776b9d13bc9d0f0d201b1897211a7f4812e906833bf94d5"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    # print(response.text)
    return response


def handle_query(querytype,query):
    query=validate_enrich_query(querytype,query)
    results = literal_eval(query_url(query).text)
    print(querytype)
    m = f"<table> <caption>Search Results</caption><th>Number</th><th>Title of the Paper</th><th>Author</th> <th>Institution</th>"
    # print(len(response['response']['docs']))
    r = 1;
    for searchResult in results['organic_results']:
        title = str(searchResult['title'])
        authors=" "
        if(querytype=='Researchers'):
            authors=querytype
        for attribute in searchResult['publication_info']:
            if attribute == 'authors':
                authors = str(searchResult['publication_info']['authors'])
        instution = "University of Cape Town "
        if (querytype == 'Institutions'):
            instution = querytype
        m = m + f"<tr><td style=\"background-color:#DC143C;\">{r}</td> <td style=\"background-color:powderblue;\">{title} </td> <td style=\"background-color:#42DBDE;\">{authors}</td> </td> <td style=\"background-color:#42DBDE;\">{instution}</td> </td> </tr>"
        r += 1
    m += "</table>"

    print(m)
    return f"<p>{m}</p>"