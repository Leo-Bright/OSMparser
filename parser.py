from imposm.parser import OSMParser

# simple class that handles the parsed OSM data.
class OSMCounter(object):
    relationDic = {}
    coordDic = {}
    nodeDic = {}
    wayDic = {}
    wayCount = 0

    def ways(self, ways):
        # callback method for ways
        for osmid, tags, refs in ways:
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
p.parse('Porto.osm.pbf')

# write the counter result to file
f_ways = open(r'ways.result', 'w+')
f_nodes = open(r'nodes.result', 'w+')
f_coords = open(r'coords.result', 'w+')
f_relations = open(r'relations.result', 'w+')

# for item in counter.wayDic.items():
#     refs = item[-1][-1]
#     start_node = refs[0]
#     end_node = refs[-1]
#     # nodes = str(refs[0]) + " " + str(refs[-1])
#     # nodes = str(osmid) + " " + str(tags) + " " + str(refs)
#     start_node_coord = counter.nodeDic.get(start_node)
#     end_node_coord = counter.nodeDic.get(end_node)
#     if not start_node_coord:
#         start_node_coord = counter.coordDic.get(start_node)
#     else:
#         start_node_coord = start_node_coord[-1]
#     if not end_node_coord:
#         end_node_coord = counter.coordDic.get(start_node)
#     else:
#         end_node_coord = end_node_coord[-1]
#     f_ways.write(str(start_node_coord) + ' ' + str(end_node_coord) + '\n')

for item in counter.wayDic.items():
    refs = item[-1][-1]
    start_node = refs[0]
    end_node = refs[-1]
    f_ways.write(str(start_node) + ' ' + str(end_node) + '\n')

for item in counter.nodeDic.items():
    # print(item)
    f_nodes.write(item.__str__() + '\n')

for item in counter.coordDic.items():
    # print(item)
    f_coords.write(item.__str__() + '\n')

for item in counter.relationDic.items():
    # print(item)
    f_relations.write(item.__str__() + '\n')

f_ways.close()
f_nodes.close()
f_coords.close()
f_relations.close()

# instantiate counter and parser and start parsing Proto nodes

