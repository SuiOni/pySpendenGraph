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
    'SPD': '#FF4060',
    'FDP': 'Yellow',
    'CDU': 'Light Slate Gray',
    'GRÜNE': 'Lime Green',
    'NPD': 'Saddle Brown',
    'AFD': 'Royal Blue',
    'CSU': 'Sky Blue',
    'DIE PARTEI': 'Cyan',
    'MLPD': 'Dark Red',
    'ÖDP': 'Orange',
    'WASG': 'Deep Pink',
    'PDS': 'Purple',
    'FW': 'Fuchsia',
    'SSW': 'Chartreuse',
    'LINKE': 'Red',
    'PRO D': 'Sienna',
    'PRO NRW': 'Peru',

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
        # print(str(i['ost'])+', '+str(i['bund'])+', '+i['plz']+', '+i['name'])




# create UniqueID for every name in data (Spenden.json)
for i in data:
    gGen[i['name']]

def mixColor (fg,bg,fgOp=0.5,bgOp=0.5):

    if fgOp > 1.0:
        fgOp=1.0
       # print("fgOP>1.0")
    if bgOp > 1.0:
        bgOp=1.0
        #print("bgOP>1.0")
    if fgOp < 0.1:
        fgOp=0.01
       # print("fgOP<0.1")
    if bgOp < 0.1:
        bgOp=0.1
       # print("bgOP<0.1")
    color1=(fg[0],fg[1],fg[2],fgOp)
    color2=(bg[0],bg[1],bg[2],bgOp)


    alpha= 1-(1-color1[3]) * (1-color2[3])
    if alpha <= 0:
        print(" alpha <=0 ")
        return mixColor(fg,bf)
    red = (color1[0] * color1[3]+color2[0] * color2[3]*(1-color1[3]))/alpha
    green = (color1[1] * color1[3]+color2[1] * color2[3]*(1-color1[3]))/alpha
    blue = (color1[2] * color1[3]+color2[2] * color2[3]*(1-color1[3]))/alpha


    return (red, green, blue, alpha)


def createGraphBucketYear(bucketIs='city', sty=2000, endy=2014, stmoney=0.00, endmoney=10000000.00, scale=1000, graphDict=gGraphDict,
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
                                    person1['val'] >= stmoney and person2['val'] >= stmoney and \
                                    person1['val'] <= endmoney and person2['val']  <= endmoney and not \
                                    person1['name'] == person2['name']:

                        try:
                            #time critical
                            v1 = g.vs.find(idGen[person1['name']])
                            v1['parties'].add(person1['party'])
                            #if v1.degree()>1:


                        except:
                            g.add_vertex(name=person1['name'], label=person1['name'], id=idGen[person1['name']],
                                         year=person1['year'], parties={person1['party']},ost=person1['ost'],
                                         color=(1.0, 1.0, 1.0, 0.2),
                                         size=5,persPrEast='',persPrWest='',persPageRank='')
                            v1 = g.vs.find(idGen[person1['name']])

                        try:
                            #time critical
                            v2 = g.vs.find(idGen[person2['name']])
                            v2['parties'].add(person2['party'])




                        except:
                            g.add_vertex(name=person2['name'], label=person2['name'], id=idGen[person2['name']],
                                         year=person2['year'], parties={person2['party']},ost=person2['ost'],
                                         color=(1.0, 1.0, 1.0, 0.2),
                                         size=5,persPrEast='',persPrWest='',persPageRank='')
                            v2 = g.vs.find(idGen[person2['name']])
                        if (g.es.select(_source=idGen[person2['name']], _target=idGen[
                            person1['name']]).__len__() == 0):  # assert idGen[person2['name']] is same as vertex number
                            v1['size'] = log(int((v1['size'] + person1['val']) / scale))*14
                            v2['size'] = log(int((v2['size'] + person2['val']) / scale))*14
                            if v1.degree() <= 4 : g.add_edge(v1, v2, color=color_dict[person1['party']],label= person1['party'],label_size=1)
                            g.add_edge(v1, v2, color=color_dict[person1['party']])


                        fg=color_name_to_rgba(color_dict[person1['party']])
                        bg1=color_name_to_rgba(v2['color'])
                        bg2=color_name_to_rgba(v2['color'])
                        opacity1=log(pow(person1['val'],2))/26
                        opacity2=log(pow(person2['val'],2))/26
                        v1['color']=   mixColor(fg,bg1,opacity1,1-opacity1)
                        v2['color']=   mixColor(fg,bg2,opacity2,1-opacity2)







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



def drawGraph(graph,year,bucketIs,csvFile,saveCSV,personalPagerank=False,euclidDist=False,layoutAlgo="kk",panelSize=(1500,1500)):



    reset_vertices_ost= []
    reset_vertices_west=[]
    persPageRankOst=[]
    persPageRankWest=[]
    persPageRankRatio=[]
    normalPagerank=[]
    shapeOst=[]
    euclidXY=[]

    if personalPagerank:
        for o,v in zip(gra.vs["ost"],gra.vs):
            if o==True:
                reset_vertices_ost.append(v)
                shapeOst.append('square')
            elif o==False:
                reset_vertices_west.append(v)
                shapeOst.append('circle')


    if reset_vertices_ost:
        persPageRankOst=graph.personalized_pagerank(directed=False,reset_vertices=reset_vertices_ost)
        print('Ost-----------------------------------')
        print([ i["name"]for i in reset_vertices_ost])
        print(persPageRankOst)
    if reset_vertices_west:
        persPageRankWest=graph.personalized_pagerank(directed=False,reset_vertices=reset_vertices_west)
        print('West-----------------------------------')
        print([ i["name"]for i in reset_vertices_west])
        print(persPageRankWest)

    if reset_vertices_ost and reset_vertices_west:
        persPageRankRatio = [ po/pw for po,pw in zip(persPageRankOst,persPageRankWest)]

    if not personalPagerank:
        print('calculate normal pagerank-----------------------------------')
        normalPagerank=graph.pagerank(directed=False)

    print("vertex list")
    print(len(graph.vs))

    print("ost list")
    print(len(persPageRankOst))


    print("west list")
    print(len(persPageRankWest))

    print("------------------")


    if euclidDist and personalPagerank:

        #euclidXY=[[ver for ver in range(len(graph.vs)) ] for xy in range(2)]


        for xy in range(len(graph.vs)):
            #print(xy)
            try:
                x=persPageRankOst[xy]*100
            except:
                x=0

            try:
                y=persPageRankWest[xy]*100
            except:
                y=0

            euclidXY.append((x,y))

        layoutEuclid=Layout(euclidXY)
        layoutEuclid.scale((5,2))

    partyPersonalPageRankMedian ={}
    if personalPagerank and saveCSV:
        print("partyPersonalPageRankMedian   if")
        print("persPageRankOst:",len(persPageRankOst)," persPageRankWest:", len(persPageRankWest), " gra:",len(gra.vs["parties"]))

        for prOst,prWest,parties in zip(persPageRankOst,persPageRankWest,gra.vs["parties"]):
            print(str(prOst)+', '+str(prWest)+', '+str(parties))
            for party in parties:
                newEntry=[prOst,prWest,1]
                try:
                    partyPersonalPageRankMedian[party]=[x + y for x, y in zip(partyPersonalPageRankMedian[party], newEntry)]
                except:
                    partyPersonalPageRankMedian[party]=newEntry
        print(partyPersonalPageRankMedian)

        partyPersonalPageRankMedian={key: x+[x[0]/x[2],x[1]/x[2],x[0]/x[1],x[0]/x[1]/x[2],year] for key, x in partyPersonalPageRankMedian.items()}
        print(partyPersonalPageRankMedian)
        # [persPageRankOst,persPageRanKWest,Amount, median spersPageRankOst,median pageRankEast/ median pageRankWest. median persPageRanKWes, median persPageRankOst/persPageRanKWest,year]

        with open(csvFile,'a') as out_csv:
            wr=csv.writer(out_csv,dialect='excel')
            wr.writerows([key]+x for key, x in partyPersonalPageRankMedian.items())









    visual_style = {}
    visual_style["edge_curved"]=True
    visual_style["vertex_color"] = gra.vs["color"]
    visual_style["vertex_size"] = gra.vs["size"]
    #logValues=[1/log(float(i+1))*10 for i in gra.degree()]
    #logValues=[log(pow(float(i),2))/3 for i in gra.vs["size"]]
    sizeEdge=[i/70 for i in gra.vs["size"]]
    sizeFont=[log(i)*3 for i in gra.vs["size"]]

    if persPageRankRatio and persPageRankOst and persPageRankWest:
        pageRank=[str("{:.5f}".format(pr))[0:6]+", "+str("{:.5f}".format(po))[0:6]+ ", "+str("{:.5f}".format(pw))[0:6] for pr,po,pw in zip(persPageRankRatio,persPageRankOst,persPageRankWest)]
    elif persPageRankOst:
        pageRank=[str("{:.5f}".format(pr))[0:6]+", " for pr in persPageRankOst]
    elif persPageRankWest:
        pageRank=[str("{:.5f}".format(pr))[0:6]+", " for pr in persPageRankWest]
    elif normalPagerank:
        pageRank=[str("{:.5f}".format(pr))[0:6]+", " for pr in normalPagerank]

    labelList= [str(p)[0:22]+ ", " + n for p, n in zip(pageRank,gra.vs["name"])]
    visual_style["vertex_label"] =[i[0:40] for i in labelList]
    visual_style["edge_width"] = sizeEdge
    if not euclidDist:
        visual_style["layout"] = gra.layout(layoutAlgo)
    elif euclidDist:
        visual_style["xlab"]='Pagerank from East'
        visual_style["ylab"]='Pagerank from West'
        visual_style["layout"]=layoutEuclid
    visual_style["bbox"] = panelSize
    visual_style["margin"] = max(gra.vs["size"])
    visual_style["keep_aspect_ratio"]=True
    #visual_style["palette"]=palettes['gray']
    visual_style["vertex_label_size"]=sizeFont
    if shapeOst: visual_style["vertex_shape"]=shapeOst



    title=str(year)+"_"+  str(i) +"_"+   str(bucketIs)+ '50000-unendlich-noeuclid' +".svg"
    plot(graph,title, **visual_style)




#cProfile.runctx("""createGraphBucketYear('year', 1994, 2013,50000.00)""",globals(), locals(), filename="profileNew.profile")
bucketIs='year'
targetIs= 'year'
fromYear=1995
toYear=1995
createGraphBucketYear(bucketIs, fromYear, toYear, 50000)
csvFile=str(fromYear)+'-'+str(toYear)+'_'+'bucketIs_'+bucketIs+'.csv'

with open(csvFile,'w') as out_csv:
    wr=csv.writer(out_csv,dialect='excel')
    wr.writerow(["Party","PersonalPageRankEast","PersonalPageRankWest","Amount of Nodes","PersonalPageRankEast/Amount of Nodes", "PersonalPageRankWest/Amount of Nodes","PersonalPageRankEast/PersonalPageRankWest", "PersonalPageRankEast/PersonalPageRankWest/Amount of Nodes","Year"])

for i in range(fromYear, toYear+1):
    #print(gDictDict[i][i])
    gra=[]
    gra = gDictDict[i][i]
    if gra:
        #print(gra.pagerank())
        print(i)
        drawGraph(gra,year=i,bucketIs=bucketIs,csvFile=csvFile,saveCSV=True,personalPagerank=True,euclidDist=False,layoutAlgo="kk")



"""
Method name	Short name	Algorithm description
layout_circle	circle, circular	Deterministic layout that places the vertices on a circle
layout_drl	drl	The Distributed Recursive Layout algorithm for large graphs
layout_fruchterman_reingold	fr	Fruchterman-Reingold force-directed algorithm
layout_fruchterman_reingold_3d	fr3d, fr_3d	Fruchterman-Reingold force-directed algorithm in three dimensions
layout_grid_fruchterman_reingold	grid_fr	Fruchterman-Reingold force-directed algorithm with grid heuristics for large graphs
layout_kamada_kawai	kk	Kamada-Kawai force-directed algorithm
layout_kamada_kawai_3d	kk3d, kk_3d	Kamada-Kawai force-directed algorithm in three dimensions
layout_lgl	large, lgl, large_graph	The Large Graph Layout algorithm for large graphs
layout_random	random	Places the vertices completely randomly
layout_random_3d	random_3d	Places the vertices completely randomly in 3D
layout_reingold_tilford	rt, tree	Reingold-Tilford tree layout, useful for (almost) tree-like graphs
layout_reingold_tilford_circular
rt_circular

tree

Reingold-Tilford tree layout with a polar coordinate post-transformation, useful for (almost) tree-like graphs
layout_sphere	sphere, spherical, circular, circular_3d	Deterministic layout that places the vertices evenly on the surface of a sphere
"""
