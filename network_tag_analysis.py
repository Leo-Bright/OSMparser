from imposm.parser import OSMParser
import json


# simple class that handles the parsed OSM data.
class OSMCounter(object):
    relationDic = {} #{osmid:(tag, refs)}
    coordDic = {} #{osmid:(lat, lon)}
    nodeDic = {} #{osmid:(tag, coordinary)}
    highwayDic = {} #{osmid:(tag, refs)}
    wayDic = {} #{osmid:(tag, refs)}

    def count_tags(self, road_segments, output_type='formal', order=True, output_path='selected_nodes.tag'):
        tagsDict = {}  # {key:{value:count}}
        tagsCountList = []  # [(key,value,count)]
        nodes_count = set()
        for road_segment in road_segments:
            gid, osm_id, source, target, reverse, priority = road_segment
            nodes_count.add(source)
            nodes_count.add(target)
            if source in self.nodeDic:
                (tags, coordinary) = self.nodeDic[source]
                for k, v in tags.items():
                    if k not in tagsDict:
                        tagsDict[k] = {}
                    if v not in tagsDict[k]:
                        tagsDict[k][v] = 1
                    else:
                        tagsDict[k][v] += 1
            if target in self.nodeDic:
                (tags, coordinary) = self.nodeDic[target]
                for k, v in tags.items():
                    if k not in tagsDict:
                        tagsDict[k] = {}
                    if v not in tagsDict[k]:
                        tagsDict[k][v] = 1
                    else:
                        tagsDict[k][v] += 1
        with open(output_path, 'w+') as output_file:
            if output_type=='json':
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
        print("have nodes: ", len(nodes_count))
        print("have roads: ", len(road_segments))

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

# write the selected_node's tag to file
with open(r'sanfrancisco/dataset/sanfrancisco_road_segment.json', 'r') as f_selected_nodes_tag:
    road_segments = json.loads(f_selected_nodes_tag.readline())
    counter.count_tags(road_segments, output_type='formal', order=True, output_path='sanfrancisco/tag/selected_nodes.tag')
