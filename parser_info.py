from imposm.parser import OSMParser
import json


# simple class that handles the parsed OSM data.
class OSMCounter(object):
    relationDic = {} #{osmid:(tag, refs)}
    coordDic = {} #{osmid:(lat, lon)}
    nodeDic = {} #{osmid:(tag, coordinary)}
    highwayDic = {} #{osmid:(tag, refs)}
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
p.parse('dataset/Porto.osm.pbf')

# write the highway info to file
f_highway_info = open(r'info/highway.info', 'w+')
for item in counter.highwayDic.items():
    f_highway_info.write(item.__str__() + '\n')
f_highway_info.close()

# write the all ways info to file
f_ways_info = open(r'info/ways.info', 'w+')
for item in counter.wayDic.items():
    f_ways_info.write(item.__str__() + '\n')
f_ways_info.close()

# write the all nodes info to file
f_nodes_info = open(r'info/nodes.info', 'w+')
for item in counter.nodeDic.items():
    f_nodes_info.write(item.__str__() + '\n')
f_nodes_info.close()


# write the all coords info to file
f_coords_info = open(r'info/coords.result', 'w+')
for item in counter.coordDic.items():
    f_coords_info.write(item.__str__() + '\n')
f_coords_info.close()


# write the relation info to file
f_relations_info = open(r'info/relations.info', 'w+')
for item in counter.relationDic.items():
    f_relations_info.write(item.__str__() + '\n')
f_relations_info.close()