from imposm.parser import OSMParser
import json


# simple class that handles the parsed OSM data.
class OSMCounter(object):
    relationDic = {} #{osmid:(tag, refs)}
    coordDic = {} #{osmid:(lat, lon)}
    nodeDic = {} #{osmid:(tag, coordinary)}
    wayDic = {} #{osmid:(tag, refs)}

    def ways(self, ways):
        # callback method for ways
        for osmid, tags, refs in ways:
            if 'highway' in tags:
                self.wayDic[osmid] = (tags, refs)

    def nodes(self, nodes):
        # callback method for nodes
        for osmid, tags, coordinary in nodes:
            if 'highway' in tags:
                if 'crossing' == tags['highway']:
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
p.parse('Porto.osm.pbf')

#### write the nodes result to file
f_nodes_statistic = open(r'dataset/nodes_intersection.json', 'w+')
node_way_map = {}  # {node_osmid:(way_osmid, ...)}
intersection_nodes = {} # {2:{osmid_node:(node_info,[osmid_way,...])},3:{},4{}}
for osmid,(tags, refs) in counter.wayDic.items():
    for node_osmid in refs:
        if node_osmid in counter.nodeDic:
            node_info = counter.nodeDic[node_osmid]
        else:
            node_info = counter.coordDic[node_osmid]
        if node_osmid not in node_way_map:
            node_way_map[node_osmid] = (node_info, [osmid,])
        else:
            node_way_map[node_osmid][1].append(osmid)

for osmid, (node_info,ways_list) in node_way_map.items():
    # f_nodes_statistic.write(item.__str__() + '\n')
    intersect_num = len(ways_list)
    if 1 < intersect_num < 5:
        if intersect_num not in intersection_nodes:
            intersection_nodes[intersect_num] = {}
        intersection_nodes[intersect_num][osmid] = (node_info, ways_list)

# for item in intersection_nodes.items():
#     f_nodes_statistic.write(item.__str__() + '\n')

f_nodes_statistic.write(json.dumps(intersection_nodes))

f_nodes_statistic.close()