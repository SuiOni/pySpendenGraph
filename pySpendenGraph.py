# -*- coding: utf-8 -*-

import json
import cProfile
from pprint import pprint
import csv
from tkinter import filedialog
from math import log
from enum import Enum
from igraph import *
import cairocffi as cairo


pr = cProfile.Profile()


color_dict = {
    'SPD': 'darkred',
    'FDP': 'yellow',
    'CDU': 'darkgrey',
    'GRÜNE': 'green',
    'NPD': 'darkbrown',
    'AFD': 'brown',
    'CSU': 'blue',
    'DIE PARTEI': 'orange',
    'MLPD': 'red',
    'ÖDP': 'pink',
    'WASG': 'green',
    'PDS': 'pink',
    'FW': 'grey',
    'SSW': 'white',
    'LINKE': 'red',
    'PRO D': 'brown',
    'PRO NRW': 'brown',

}


class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


# Open File Dialog for Spenden
file_path = filedialog.askopenfilename(filetypes=[("JSON file", "*.json"),
                                                  ("GraphML file", "*.graphml"),
                                                  ("All files", "*.*")])
# load JSON file into data
with open(file_path) as data_file:
    data = json.load(data_file)

# Open File Dialog for plz data
file_path_plz = filedialog.askopenfilename(filetypes=[("JSON file", "*.json"),
                                                      ("All files", "*.*")])

with open(file_path_plz) as file_path_plz:
    plzbund = json.load(file_path_plz)

# globalvariable
bundDdr = ['Brandenburg', 'Mechlenburg-Vorpommern', 'Sachen', 'Sachsen-Anhalt', 'Thüringen', 'Berlin']
gddr = []
gbrd = []
gGraphDict = defaultdict(Graph)  # create a dict of key(bucketis exp citys):Graph pairs
gDictDict = AutoVivification()  # create a dict of key(person):dict(key(bucketis exp citys):Graph) pairs
gListDict = defaultdict(list)
gListDict2 = defaultdict(list)
gGen = UniqueIdGenerator()  # creates a unique integer id for a string similar to dict

plzDict = gListDict2

for i in plzbund:
   # plzDict[i['plz']].append(i['bund'])
   plzDict[i['plz']]=i['bund']

'''try:
       print(str(plzDict[int(i['plz'])]))
   except:
       print()'''

'''for i in data:
    print(plzDict[i['plz']])'''

# Add Bundesland to all entries in data
for i in data:
    try:

        bund = plzDict[int(i['plz'])]
        if bund!=[]: i['bund'] = bund
        else: i['bund']="NA"

        #if bund subset of bundDDR
        if bund in set(bundDdr):
            i['ost'] = True
        else:
            i['ost'] = False

    except:

        if i['plz']!=[]: i['bund']=i['plz']
        else: i['bund']="NA"
        i['ost'] = False
        print(str(i['ost'])+', '+str(i['bund'])+', '+i['plz']+', '+i['name'])




# create UniqueID for every name in data (Spenden.json)
for i in data:
    gGen[i['name']]


def createGraphBucketYear(bucketIs='city', sty=2000, endy=2014, value=0.00, scale=1000, graphDict=gGraphDict,
                          dictDict=gDictDict,
                          listDict=gListDict, set=data):
    # if (type(dictDict).__name__ == type(graphDict).__name__ == type(listDict).__name__ == 'defaultdict'):


    # append enities of same buckettype  into the same bucketKey list
    for i in set:

        listDict[i[bucketIs]].append(i)

    # take all entities of the same buckettype (exp. city) and same year and put them into a list of list of graphs for each year (actually dict of graphs) connect everyone in the same city -> amount of graph = amount of different cities * different year
    # for all keys of buckettype (exp buckettype=city keys=Cologne, Hamburg ...) calculate the graph
    for bucketKey in listDict.keys():
        peopleofbucket = listDict[bucketKey]

        # creates graph with everyone in the list (same city) and same party and same year connected for every year

        # greate graph for every year
        for year in range(sty, endy + 1):
            g = Graph(directed=False)
            idGen = UniqueIdGenerator()
            for person1 in peopleofbucket:
                for person2 in peopleofbucket:
                    if person1['year'] == year and person2['year'] == year and \
                                    person1['party'] == person2['party'] and \
                                    person1['val'] >= value and person2['val'] >= value and not person1['name'] == \
                            person2['name']:

                        try:
                            #time critical
                            v1 = g.vs.find(idGen[person1['name']])
                            v1['color']=(255, 128, 0)
                        except:
                            g.add_vertex(name=person1['name'], label=person1['name'], id=idGen[person1['name']],
                                         year=person1['year'], party=person1['party'],ost=person1['ost'],
                                         color=color_dict[person1['party']],
                                         size=5)
                            v1 = g.vs.find(idGen[person1['name']])

                        try:
                            #time critical
                            v2 = g.vs.find(idGen[person2['name']])
                        except:
                            g.add_vertex(name=person2['name'], label=person2['name'], id=idGen[person2['name']],
                                         year=person2['year'], party=person2['party'],ost=person2['ost'],
                                         color=color_dict[person2['party']],
                                         size=5)
                            v2 = g.vs.find(idGen[person2['name']])
                        if (g.es.select(_source=idGen[person2['name']], _target=idGen[
                            person1['name']]).__len__() == 0):  # assert idGen[person2['name']] is same as vertex number
                            v1['size'] = int((v1['size'] + person1['val']) / scale)
                            v2['size'] = int((v2['size'] + person2['val']) / scale)
                            g.add_edge(v1, v2, color=color_dict[person1['party']])





                            # edges=[(idGen[person1['name'], person1['party'], person1['val'] ), g.add_vertex(person1['name'])) for person1 in peopleofbucket for person2 in peopleofbucket if (person1['year'] == year and person2['year'] == year and person1['party'] == person2['party'] and person1['name'] == person2['name'])]

            if g.vcount() > 0:
                # g=Graph(edges,directed=False)

                dictDict[bucketKey][year] = g.as_undirected()

                # print(id(g))
                # take all entities of the same city and put them into a graph connect everyone in the same city -> amount of graph = amount of different cities

                # else:
                #     print('Error vgybuckets or vgbucketstypes or vbuckets  is not defaultdict')
                #     return 1;


# filter data only enities within range of year
# data2=[elem for elem in data if elem['year'] in range(2000,2014)]





def createPersonListDdrBrd(set=data, lddr=gddr, lbrd=gbrd, lon=11.252747, lat=50.341078, ):
    # erstelle listen für spenden aus ost und west
    print('Load BRD and DDR')
    for i in set:
        try:
            if float(i['lon']) > lon and float(
                    i['lat']) > lat:  # wenn innerhalb dieser zone dann ist es in der ehem. ddr
                lddr.append(i)
            else:
                lbrd.append(i)
        except:  # manche einträge haben keinen lon bzw lat eintrag
            print(i['city'], "no lon or lat found")

    return;


'''createPersonListDdrBrd()

for i in gbrd:
    print([i['city']])

print("---------------------------------------------")
for i in gddr:
    print([i['city']])'''

'''
createGraphBucketYear('city', 1994, 2014,)
print(gDictDict.keys())
for i in range(1994, 2015):
    gra = gDictDict['Dortmund'][i]
    if gra: plot(gra,directed=False);

print(gGen['Zorn, Gerhard'])'''

'''
createGraphBucketYear('year', 1994, 1994,)
for i in range(1994, 1994):
    gra = gDictDict[i][i]
    if gra: plot(gra,directed=False);'''





#cProfile.runctx("""createGraphBucketYear('year', 1994, 2013,50000.00)""",globals(), locals(), filename="profileNew.profile")
bucketIs='year'
targetIs='Köln'
createGraphBucketYear(bucketIs, 2014, 2014)
for i in range(2014, 2015):
    print(gDictDict[i][i])

    gra = gDictDict[i][i]
    if gra:




        #layout = gra.layout_lgl()
        visual_style = {}
        visual_style["edge_curved"]=True
        visual_style["vertex_label_size"]=20
        #visual_style["vertex_order"]=gra.vs["size"]
        visual_style["vertex_size"] = gra.vs["size"]
        visual_style["vertex_color"] = gra.vs["color"]
        logValues=[1/log(float(i))*10 for i in gra.degree()]
        print(logValues)
        visual_style["vertex_label"] = gra.vs["name"]
        visual_style["edge_width"] = logValues
        #visual_style["layout"] = layout
        visual_style["bbox"] = (1500, 1500)
        visual_style["margin"] = 100

        title=str(i)+"_"+  str(targetIs) +"_"+   str(bucketIs)+".svg"
        plot(gra,title, **visual_style)


