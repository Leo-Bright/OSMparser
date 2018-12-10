from imposm.parser import OSMParser
import json


# simple class that handles the parsed OSM data.
class OSMCounter(object):
    relationDic = {} #{osmid:(tag, refs)}
    coordDic = {} #{osmid:(lat, lon)}
    nodeDic = {} #{osmid:(tag, coordinary)}
    highwayDic = {} #{osmid:(tag, refs)}
    wayDic = {} #{osmid:(tag, refs)}

    def count_tags(self, output_file, type='way', output='formal', order=True, selected_node_path = 'porto/network/selected_nodes.json'):
        tagsDict = {}  # {key:{value:count}}
        tagsCountList = []  # [(key,value,count)]
        if type == 'way':
            objDict = self.wayDic
        if type == 'highway':
            objDict = self.highwayDic
        if type == 'node':
            objDict = self.nodeDic
        if type == 'selected_node':
            try:
                f_selected_nodes = open(selected_node_path, 'r')
                objDict = json.loads(f_selected_nodes.readline())
                f_selected_nodes.close()
            except:
                objDict = {}
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
p.parse('sanfrancisco/dataset/SanFrancisco.osm.pbf')

# write the way's tag to file
f_ways_tags = open(r'sanfrancisco/tag/ways.tag', 'w+')
counter.count_tags(f_ways_tags, type='way', output='formal', order=True)
f_ways_tags.close()

# write the highway's tag to file
f_highway_tags = open(r'sanfrancisco/tag/highway.tag', 'w+')
counter.count_tags(f_highway_tags, type='highway', output='formal', order=True)
f_highway_tags.close()

# write the node's tag to file
f_nodes_tags = open(r'sanfrancisco/tag/nodes.tag', 'w+')
counter.count_tags(f_nodes_tags, type='node', output='formal', order=True)
f_nodes_tags.close()

# write the selected_node's tag to file
f_selected_nodes_tag = open(r'sanfrancisco/tag/selected_nodes.tag', 'w+')
counter.count_tags(f_selected_nodes_tag, type='selected_node', output='formal', order=True, selected_node_path = 'sanfrancisco/network/selected_nodes.json')
f_selected_nodes_tag.close()
