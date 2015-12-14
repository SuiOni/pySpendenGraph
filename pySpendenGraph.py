import json
from pprint import pprint
from tkinter import filedialog
from enum import Enum
from igraph import *
import cairocffi as cairo

class Party(Enum):
    SPD='red'
    FPD='yellow'
    CDU='black'
    GRÜNE='green'
    NPD='brown'
    AFD='orange'
    CSU='blue'


class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


# Open File Dialog
file_path = filedialog.askopenfilename(filetypes=[("JSON file", "*.json"),
                                                  ("GraphML file", "*.graphml"),
                                                  ("All files", "*.*")])
# load JSON file into data
with open(file_path) as data_file:
    data = json.load(data_file)

# globalvariable
gddr = []
gbrd = []
gGraphDict = defaultdict(Graph)  # create a dict of key(bucketis exp citys):Graph pairs
gDictDict = AutoVivification()  # create a dict of key(person):dict(key(bucketis exp citys):Graph) pairs
gListDict = defaultdict(list)
gGen = UniqueIdGenerator()  # creates a unique integer id for a string similar to dict

for i in data:
    gGen[i['name']]


def createGraphBucketYear(bucketIs='city', sty=2000, endy=2014,value=0.00, graphDict=gGraphDict, dictDict=gDictDict,
                          listDict=gListDict, set=data, ):
    # if (type(dictDict).__name__ == type(graphDict).__name__ == type(listDict).__name__ == 'defaultdict'):


    # append enities of same buckettype value into the same bucketKey list
    for i in set:
        listDict[i[bucketIs]].append(i)

        # take all entities of the same city and same year and put them into a list of list of graphs for each year (actually dict of graphs) connect everyone in the same city -> amount of graph = amount of different cities * different year

    for bucketKey in listDict.keys():
        peopleofbucket = listDict[bucketKey]

        # creates graph with everyone in the list (same city) and same party and same year connected for every year
        # graphDict.clear()

        for year in range(sty, endy + 1):
            g = Graph(directed=False)
            idGen = UniqueIdGenerator()
            for person1 in peopleofbucket:
                for person2 in peopleofbucket:
                    if person1['year'] == year and person2['year'] == year and person1['party'] == person2['party'] and  person1['val']>=value and person2['val']>=value and not person1['name'] == person2['name']:

                        try:
                            v1 = g.vs.find(idGen[person1['name']])
                        except:
                            g.add_vertex(name=person1['name'], label=person1['name'], id=idGen[person1['name']],
                                         year=person1['year'], party=person1['party']) #, color=Party[person1['party']]
                            v1 = g.vs.find(idGen[person1['name']])

                        try:
                            v2 = g.vs.find(idGen[person2['name']])
                        except:
                            g.add_vertex(name=person2['name'], label=person2['name'], id=idGen[person2['name']],
                                         year=person2['year'], party=person2['party'])
                            v2 = g.vs.find(idGen[person2['name']])
                        if (g.es.select(_source=idGen[person2['name']], _target=idGen[person1['name']]).__len__() == 0) :  # assert idGen[person2['name']] is same as vertex number
                            g.add_edge(v1, v2)



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

createGraphBucketYear('city', 1994, 2014,value=50000.00)
print(gDictDict.keys())
for i in range(1994, 2015):
    gra = gDictDict['Köln'][i]
    if gra: plot(gra)

print(gGen['Zorn, Gerhard'])
