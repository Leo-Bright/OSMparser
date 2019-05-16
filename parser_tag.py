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
            print("selected nodes count:", len(objDict.keys()))
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
def extract_way_tag_info(output):
    f_ways_tags = open(r'sanfrancisco/tag/ways.tag', 'w+')
    counter.count_tags(f_ways_tags, type='way', output='formal', order=True)
    f_ways_tags.close()


# write the highway's tag to file
def extract_highway_tag_info():
    f_highway_tags = open(r'sanfrancisco/tag/highway.tag', 'w+')
    counter.count_tags(f_highway_tags, type='highway', output='formal', order=True)
    f_highway_tags.close()


# write the node's tag to file
def extract_node_tag_info():
    f_nodes_tags = open(r'sanfrancisco/tag/nodes.tag', 'w+')
    counter.count_tags(f_nodes_tags, type='node', output='formal', order=True)
    f_nodes_tags.close()


# write the selected_node's tag to file
def extract_network_node_tag_info():
    f_selected_nodes_tag = open(r'sanfrancisco/tag/selected_nodes_onlyNode.tag', 'w+')
    counter.count_tags(f_selected_nodes_tag, type='selected_node', output='formal', order=True, selected_node_path = 'sanfrancisco/network/selected_nodes_onlyNode.json')
    f_selected_nodes_tag.close()


def extract_road_segment_tag_info(road_segments_file, output):
    way_count = {}
    with open(road_segments_file) as f:
        road_segments = json.loads(f.readline())
    for segment in road_segments:
        osm_id = segment['osm_id']
        if osm_id not in way_count:
            way_count[osm_id] = 1
        else:
            way_count[osm_id] += 1

    tags_dict = {}
    with open(output, 'w+') as f:
        for osmid, tags_and_others in counter.wayDic.items():
            tags = tags_and_others[0]
            coefficient = way_count[osmid]
            for k, v in tags.items():
                if k not in tags_dict:
                    tags_dict[k] = {}
                if v not in tags_dict[k]:
                    tags_dict[k][v] = coefficient
                else:
                    tags_dict[k][v] += coefficient


if __name__ == '__main__':
    # extract_way_tag_info(output='sanfrancisco/tag/ways.tag')
    extract_road_segment_tag_info(road_segments_file='sanfrancisco/dataset/all_road_segments_dict.sanfrancisco',
                                  output='sanfrancisco/tag/road_segment.tag')

