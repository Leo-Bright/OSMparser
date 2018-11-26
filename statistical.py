from imposm.parser import OSMParser
import json


# simple class that handles the parsed OSM data.
class OSMCounter(object):
    relationDic = {} #{osmid:(tags, refs)}
    coordDic = {} #{osmid:(lat, lon)}
    nodeDic = {} #{osmid:(tags, coordinary)}
    wayDic = {} #{osmid:(tags, refs)}

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
f_nodes_statistic = open(r'dataset/nodes_crossing_statistic.result', 'w+')
node_way_map = {}  # {node_osmid:(way_osmid, ...)}
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

for item in node_way_map.items():
    f_nodes_statistic.write(item.__str__() + '\n')
f_nodes_statistic.close()


