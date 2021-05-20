from imposm.parser import OSMParser
import json


# simple class that handles the parsed OSM data.
class OSMCounter(object):
    relationDic = {} #{osmid:(tag, refs)}
    coordDic = {} #{osmid:(lat, lon)}
    crossing_nodes = {} #{osmid:(tag, coordinary)}
    nodeDic = {} #{osmid:(tag, coordinary)}
    highwayDic = {}  # {osmid:(tag, refs)}
    wayDic = {} #{osmid:(tag, refs)}

    def ways(self, ways):
        # callback method for ways
        for osmid, tags, refs in ways:
            if 'highway' in tags:
                self.highwayDic[osmid] = (tags, refs)
            self.wayDic[osmid] = (tags, refs)

    def nodes(self, nodes):
        # callback method for nodes
        for osmid, tags, coordinary in nodes:
            if 'highway' in tags:
                if 'crossing' == tags['highway']:
                    self.crossing_nodes[osmid] = (tags, coordinary)
            self.nodeDic[osmid] = (tags, coordinary)

    def coords(self, coords):
        # callback method for coords
        for osmid, lat, lon in coords:
            self.coordDic[osmid] = (lat, lon)

    def relations(self, relations):
        # callback method for relations
        for osmid, tags, refs in relations:
            self.relationDic[osmid] = (tags, refs)


# instantiate counter and parser and start parsing Proto ways
counter = OSMCounter()
p = OSMParser(concurrency=4, ways_callback=counter.ways, nodes_callback=counter.nodes,
              coords_callback=counter.coords, relations_callback=counter.relations)
p.parse('sanfrancisco/dataset/SanFrancisco.osm.pbf')

# write the intersection nodes result to file
f_nodes_intersection_json = open(r'sanfrancisco/dataset/nodes_intersection.json', 'w+')
f_nodes_intersection_data2 = open(r'sanfrancisco/dataset/nodes_intersection2.data', 'w+')
f_nodes_intersection_data3 = open(r'sanfrancisco/dataset/nodes_intersection3.data', 'w+')
f_nodes_intersection_data4 = open(r'sanfrancisco/dataset/nodes_intersection4.data', 'w+')
f_nodes_intersection_data5 = open(r'sanfrancisco/dataset/nodes_intersection5.data', 'w+')

node_way_map = {}  # {node_osmid:(way_osmid, ...)}
for osmid, (tags, refs) in counter.wayDic.items():
    for node_osmid in refs:
        if node_osmid in counter.nodeDic:
            node_info = counter.nodeDic[node_osmid]
        else:
            node_info = counter.coordDic[node_osmid]
        if node_osmid not in node_way_map:
            node_way_map[node_osmid] = (node_info, [osmid, ])
        else:
            node_way_map[node_osmid][1].append(osmid)

intersection_nodes = {} # {2:{osmid_node:(node_info,[osmid_way,...])},3:{},4{}}
for osmid, (node_info, ways_list) in node_way_map.items():
    # f_nodes_statistic.write(item.__str__() + '\n')
    intersect_num = len(set(ways_list))
    if 1 < intersect_num:
        if intersect_num not in intersection_nodes:
            intersection_nodes[intersect_num] = {}
        intersection_nodes[intersect_num][osmid] = node_info
for key, value in intersection_nodes.items():
    print(str(key)+" : " + str(len(value.keys())))
for item in intersection_nodes[2].items():
    f_nodes_intersection_data2.write(item.__str__() + '\n')

for item in intersection_nodes[3].items():
    f_nodes_intersection_data3.write(item.__str__() + '\n')

for item in intersection_nodes[4].items():
    f_nodes_intersection_data4.write(item.__str__() + '\n')

for item in intersection_nodes[5].items():
    f_nodes_intersection_data5.write(item.__str__() + '\n')

f_nodes_intersection_json.write(json.dumps(intersection_nodes))
f_nodes_intersection_json.close()


# write the crossing nodes result to file
f_nodes_crossing_json = open(r'sanfrancisco/dataset/nodes_crossing.json', 'w+')
f_nodes_crossing_data = open(r'sanfrancisco/dataset/nodes_crossing.data', 'w+')

f_nodes_crossing_json.write(json.dumps(counter.crossing_nodes))
f_nodes_crossing_json.close()


for item in counter.crossing_nodes.items():
    f_nodes_crossing_data.write(item.__str__() + '\n')
f_nodes_crossing_data.close()