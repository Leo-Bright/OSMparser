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

city_name = 'london'
with open(city_name + '/dataset/london_parsed_obj.pkl', 'rb') as f:
    parsed_obj = pkl.load(f)

# write the highway info to file
with open(city_name + '/info/highway.info', 'w+') as f_highway_info:
    for item in parsed_obj.highwayDic.items():
        f_highway_info.write(item.__str__() + '\n')

# write the all ways info to file
with open(city_name + '/info/ways.info', 'w+') as f_ways_info:
    for item in parsed_obj.wayDic.items():
        f_ways_info.write(item.__str__() + '\n')

# write the all nodes info to file
with open(city_name + '/info/nodes.info', 'w+') as f_nodes_info:
    for item in parsed_obj.nodeDic.items():
        f_nodes_info.write(item.__str__() + '\n')

# write the all traffic info to file
key = 'crossing'
value = 'zebra'
with open(city_name + '/info/' + value + '.json', 'w+') as f_info:
    crossing = {'lat': [], 'lon': []}
    for node_id in parsed_obj.nodeDic:
        (tags, coordinary) = parsed_obj.nodeDic[node_id]
        if key not in tags:
            continue
        if value in tags[key]:
            crossing['lon'].append(str(coordinary[0]))
            crossing['lat'].append(str(coordinary[1]))
    f_info.write(json.dumps(crossing) + '\n')


# write the all coords info to file
with open(city_name + '/info/coords.info', 'w+') as f_coords_info:
    for item in parsed_obj.coordDic.items():
        f_coords_info.write(item.__str__() + '\n')


# write the relation info to file
f_relations_info = open(r'sanfrancisco/info/relations.info', 'w+')
for item in parsed_obj.relationDic.items():
    f_relations_info.write(item.__str__() + '\n')
f_relations_info.close()