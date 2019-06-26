
from bs4 import BeautifulSoup
from lxml import html
import json, urllib2
import re
import time
import pydot
import itertools



#STEP 1 FETCH HTML PAGE AND SAVE IT AS 'step1.html'
def get_page():
    url = "http://www.imdb.com/search/title?at=0&sort=num_votes&count=100"
    page = urllib2.urlopen(url)
    html_doc = page.read().decode('utf-8')
    html_file = open(r'step1.html', 'w+')
    html_file.write(html_doc.encode('utf-8'))
    html_file.close()
    return html_doc

#STEP 2
def parse_data(html_doc):
    soup = BeautifulSoup(html_doc)
    table = soup.find('table', {'class': 'results'})
    a = table.find_all('a')
    IMDB_IDs = []
    ranks = []
    titles = []
    notTitles = [None, 'Register or login to rate this title', 'Delete']
    #IDs and titles
    for link in a:
        IDString = link.get('href')
        titleString = link.get('title')
        if (re.findall(r'tt[0-9]*', IDString) != []):
            IMDB_IDs.append(re.findall(r'tt[0-9]*', IDString))
        if (titleString not in notTitles):
            titles.append(titleString)
    #get rid of duplicates
    IMDB_IDs_nodups = []
    for e in IMDB_IDs:
        if e[0] not in  IMDB_IDs_nodups:
            IMDB_IDs_nodups.append(e[0])
    #ranks
    td = table.find_all('td', {'class': 'number'})
    for f in td:
        string = f.string
        string = string[:-1] #remove '.'
        ranks.append(string)
    return IMDB_IDs_nodups, ranks, titles

def write_to_txt(IMDB_IDs, ranks, titles):
    file = open(r'step2.txt', 'w+')
    for i in range(0,100):
        file.write('%s\t%s\t%s\n' % (IMDB_IDs[i].encode('utf-8'), ranks[i].encode('utf-8'), titles[i].encode('utf-8'))),
    file.close()

#STEP 3
def json_pull(IMDB_IDs):
    with open(r'step3.txt', 'w+') as file:
        for i in range(0,100):
            OMDbData = json.load(urllib2.urlopen('http://www.omdbapi.com/?i=%s' % IMDB_IDs[i]))
            time.sleep(5)
            file.write(json.dumps(OMDbData, ensure_ascii=False).encode('utf-8'))
            file.write('\n')

#STEP 4
def step4():
    data = []
    with open('step3.txt') as file:
        for line in file:
            data.append(json.loads(line))
    titles = []
    actors = []
    for i in range(0,100):
        titles.append(data[i]['Title'])
        actors.append(data[i]['Actors'])
    file = open(r'step4.txt', 'w+')
    # GOTTA GET QUOTATIONS AROUND NAMES
    #some unicode stuff got rekt
    for i in range(0,100):
        x = actors[i].split(',')
        item = []
        for d in x:
            d = d.strip()
            item.append(d.encode('utf-8'))
        item = '[%s%s%s]' % ('"', '", "'.join(item), '"')
        file.write('%s\t%s\n' % (titles[i].encode('utf-8'), item))
    file.close()

def step5():
    data = []
    actorList = []
    file = open('step4.txt', 'rU')
    for line in file:
        actors = re.findall(r'(?<=")[^.",]+(?=")', line)
        data.append(actors)
    file.close()
    graph = pydot.Dot(graph_type='graph')
    for sublist in data:
        for item in list(itertools.combinations(sublist, 2)):
            edge = pydot.Edge(item[0], item[1])
            graph.add_edge(edge)
    graph.write_dot('actors_graph_output.dot')


def main():
  #page = get_page()
  #IMDB, ranks, titles = parse_data(page)
  #write_to_txt(IMDB, ranks, titles)
  #json_pull(IMDB)
  step4()
  step5()

# This is boilerplate python code: it tells the interpreter to execute main() only
# if this module is being run as the main script by the interpreter, and
# not being imported as a module.
if __name__ == '__main__':
    main()