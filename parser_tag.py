from imposm.parser import OSMParser
import pickle as pkl
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


def count_tags(counter_obj, output_file, type='way', output='formal', order=True, selected_node_path = 'porto/network/selected_nodes.json'):
    tagsDict = {}  # {key:{value:count}}
    tagsCountList = []  # [(key,value,count)]
    if type == 'way':
        objDict = counter_obj.wayDic
    if type == 'highway':
        objDict = counter_obj.highwayDic
    if type == 'node':
        objDict = counter_obj.nodeDic
    if type == 'selected_node':
        try:
            with open(selected_node_path, 'r') as f_selected_nodes:
                objDict = json.loads(f_selected_nodes.readline())
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


# write the way's tag to file
def extract_way_tag_info(counter_obj, output):
    with open(output, 'w+') as f_ways_tags:
        count_tags(counter_obj, f_ways_tags, type='way', output='formal', order=True)


# write the highway's tag to file
def extract_highway_tag_info(counter_obj):
    with open(r'sanfrancisco/tag/highway.tag', 'w+') as f_highway_tags:
        count_tags(counter_obj, f_highway_tags, type='highway', output='formal', order=True)


# write the node's tag to file
def extract_node_tag_info(counter_obj):
    with open(r'sanfrancisco/tag/nodes.tag', 'w+') as f_nodes_tags:
        count_tags(counter_obj, f_nodes_tags, type='node', output='formal', order=True)


# write the selected_node's tag to file
def extract_network_node_tag_info(counter_obj):
    with open(r'sanfrancisco/tag/selected_nodes_onlyNode.tag', 'w+') as f_selected_nodes_tag:
        count_tags(counter_obj, f_selected_nodes_tag, type='selected_node', output='formal', order=True, selected_node_path = 'sanfrancisco/network/selected_nodes_onlyNode.json')


def extract_road_segment_tag_info(counter_obj, road_segments_file, output, key=None):
    way_count = {}
    with open(road_segments_file) as f:
        road_segments = json.loads(f.readline())
    for segment in road_segments:
        osm_id = str(road_segments[segment]['osm_id'])
        if osm_id not in way_count:
            way_count[osm_id] = 1
        else:
            way_count[osm_id] += 1

    tags_dict = {}
    tags_dict[key] = {}
    with open(output, 'w+') as f:
        for osmid, tags_and_others in counter_obj.highwayDic.items():
            tags = tags_and_others[0]
            if str(osmid) in way_count:
                coefficient = way_count[str(osmid)]
            else:
                continue
            if key is None:
                for k, v in tags.items():
                    if k not in tags_dict:
                        tags_dict[k] = {}
                    if v not in tags_dict[k]:
                        tags_dict[k][v] = coefficient
                    else:
                        tags_dict[k][v] += coefficient
            elif key not in tags:
                continue
            else:
                v = tags[key]
                if v not in tags_dict[key]:
                    tags_dict[key][v] = coefficient
                else:
                    tags_dict[key][v] += coefficient

        tags_count_list = []
        for key, value_count in tags_dict.items():
            for value, count in value_count.items():
                tags_count_list.append((key, value, count))

        tags_count_list.sort(key=lambda x: x[-1], reverse=True)

        for key, value, count in tags_count_list:
            try:
                f.write(str(key) + '\t\t' + str(value) + '\t\t' + str(count) + '\n')
            except:
                if not isinstance(key, int):
                    key = key.encode('utf8')
                if not isinstance(value, int):
                    value = value.encode('utf8')
                f.write(str(key) + '\t\t' + str(value) + '\t\t' + str(count) + '\n')


def statistical_road_segment_class_id(road_segments_file):
    class_count = {}
    with open(road_segments_file) as f:
        road_segments = json.loads(f.readline())
    print('this city has segments num: ', len(road_segments.keys()))
    for segment in road_segments:
        class_id = road_segments[segment]['class_id']
        if class_id not in class_count:
            class_count[class_id] = 1
        else:
            class_count[class_id] += 1

    class_count_list = []
    for key, value in class_count.items():
        class_count_list.append((key, value))

    class_count_list.sort(key=lambda x: x[-1], reverse=True)

    with open('dataset/road-types.json') as f:
        road_types = json.load(f)

    road_type_info = {}
    for road_type in road_types['tags'][0]['values']:
        type_name = road_type['name']
        type_id = road_type['id']
        road_type_info[type_id] = type_name

    for key, value in class_count_list:
        type_name = road_type_info[key]
        print(str(key) + '\t' + type_name + '\t' + str(value))


def extract_highway_tag_file(counter_obj, output):
    with open(output, 'w+') as f:
        result = {}
        for osmid, tags_and_others in counter_obj.highwayDic.items():
            tags = tags_and_others[0]
            result[osmid] = tags
        f.write(json.dumps(result))


if __name__ == '__main__':

    city_name = 'london'
    with open(city_name + '/dataset/london_parsed_obj.pkl', 'rb') as f:
        parsed_obj = pkl.load(f)

    # extract_way_tag_info(parsed_obj, output=city_name + '/tag/' + city_name + 'ways.tag')

    # extract_road_segment_tag_info(parsed_obj, road_segments_file='porto/dataset/all_road_segments_dict.porto',
    #                               output='porto/tag/road_segment_tag_info.porto',
    #                               key='tiger:name_base',)

    extract_highway_tag_file(parsed_obj, output=city_name + '/tag/' + city_name + 'road_segment_tag.json')

    # statistical_road_segment_class_id(road_segments_file='porto/dataset/all_road_segments_dict.porto')

