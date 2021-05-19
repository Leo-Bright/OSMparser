from parser import OSMCounter
import pickle as pkl
import json

city_name = 'NewYork'
with open(city_name + '/dataset/' + city_name + '_parsed_obj.pkl', 'rb') as f:
    parsed_obj = pkl.load(f)

# write the highway info to file
with open(city_name + '/info/' + city_name + '_highway.info', 'w+') as f_highway_info:
    for item in parsed_obj.highwayDic.items():
        f_highway_info.write(item.__str__() + '\n')

# write the all ways info to file
with open(city_name + '/info/' + city_name + '_ways.info', 'w+') as f_ways_info:
    for item in parsed_obj.wayDic.items():
        f_ways_info.write(item.__str__() + '\n')

# write the all nodes info to file
with open(city_name + '/info/' + city_name + '_nodes.info', 'w+') as f_nodes_info:
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
with open(city_name + '/info/' + city_name + '_coords.info', 'w+') as f_coords_info:
    for item in parsed_obj.coordDic.items():
        f_coords_info.write(item.__str__() + '\n')


# write the relation info to file
with open(city_name + '/info/' + city_name + '_relations.info', 'w+') as f_relations_info:
    for item in parsed_obj.relationDic.items():
        f_relations_info.write(item.__str__() + '\n')