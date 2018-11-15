from imposm.parser import OSMParser
import json


# simple class that handles the parsed OSM data.
class OSMCounter(object):
    relationDic = {} #{osmid:(tags, refs)}
    coordDic = {} #{osmid:(lat, lon)}
    nodeDic = {} #{osmid:(tags, coordinary)}
    wayDic = {} #{osmid:(tags, refs)}

    def get_node_coord(self, osmid):
        node = self.nodeDic.get(osmid)
        if node:
            node_coord = node[1]
            node_lant = node_coord[0]
            node_lon = node_coord[1]
        else:
            node = self.coordDic.get(osmid)
            if not node:
                pass
            else:
                node_lant = node[0]
                node_lon = node[1]
        return node_lant, node_lon

    # osmid : do write the way's osmid to the result file ?
    # tag : do write the tag to the result  ?
    # refs_index: select the index of refs you want
    # coordinate: write the coordinate of the refs to result file or only the refs ?
    def print_ways_result(self, output_file, osmid=False, tag=False, refs_index=[0, -1], coordinate=False):

        for item in self.wayDic.items():
            refs = item[1][-1]

            # filter the way that don't match the condition
            if len(refs) < len(refs_index):
                continue

            nodes = []
            for index in refs_index:
                nodes.append(refs[index])
            if osmid:
                output_file.write(str(item[0]) + ' ')
            if tag:
                output_file.write(str(item[1][0]) + ' ')
            if coordinate:
                for node in nodes:
                    node_lant, node_lon = self.get_node_coord(node)
                    output_file.write(str((node_lant, node_lon)) + ' ')
                output_file.write('\n')

            else:
                for node in nodes:
                    output_file.write(str(node) + ' ')
                output_file.write('\n')

    def count_tags(self, output_file, type='way', output='formal', order=True):
        tagsDict = {} #{key:{value:count}}
        tagsCountList = [] #[(key,value,count)]
        if type=='way':
            objDict = self.wayDic
        if type=='node':
            objDict = self.nodeDic
        for osmid, tags_and_others in objDict.items():
            tags = tags_and_others[0]
            for k, v in tags.items():
                if k not in tagsDict:
                    tagsDict[k] = {}
                if v not in tagsDict[k]:
                    tagsDict[k][v] = 1
                else:
                    tagsDict[k][v] += 1
        if output=='json':
            output_file.write(json.dumps(tagsDict))
        else:
            for key, value_count in tagsDict.items():
                for value, count in value_count.items():
                    tagsCountList.append((key, value, count))
            if order:
                tagsCountList.sort(key=lambda x: x[-1], reverse=True)
            for key, value, count in tagsCountList:
                try:
                    output_file.write(str(key) + '\t\t' + str(value) + '\t\t' + str(count) + '\n')
                except:
                    if not isinstance(key, int):
                        key = key.encode('utf8')
                    if not isinstance(value, int):
                        value = value.encode('utf8')
                    output_file.write(str(key) + '\t\t' + str(value) + '\t\t' + str(count) + '\n')

    def ways(self, ways):
        # callback method for ways
        for osmid, tags, refs in ways:
            # if 'highway' in tags:
                # self.wayDic[osmid] = (tags, refs)
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
# f_ways = open(r'ways.result', 'w+')
f_ways_tags = open(r'ways_tags.result', 'w+')
# f_nodes = open(r'nodes.result', 'w+')
f_nodes_tags = open(r'nodes_tags.result', 'w+')
f_coords = open(r'coords.result', 'w+')
f_relations = open(r'relations.result', 'w+')

# whats data you want to write.
# counter.print_ways_result(f_ways, osmid=False, tag=True, coordinate=False)
counter.count_tags(f_ways_tags, type='way', output='formal', order=False)
counter.count_tags(f_nodes_tags, type='node', output='json', order=True)

# for item in counter.nodeDic.items():
    # print(item)
    # f_nodes.write(item.__str__() + '\n')

for item in counter.coordDic.items():
    # print(item)
    f_coords.write(item.__str__() + '\n')

for item in counter.relationDic.items():
    # print(item)
    f_relations.write(item.__str__() + '\n')

# close the file resource.
# f_ways.close()
f_ways_tags.close()
# f_nodes.close()
f_nodes_tags.close()
f_coords.close()
f_relations.close()
