from imposm.parser import OSMParser
from math import radians, cos, sin, asin, sqrt
import json
import copy


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

cities = ['sanfrancisco/dataset/SanFrancisco.osm.pbf',
          'porto/dataset/Porto.osm.pbf',
          'tokyo/dataset/Tokyo.osm.pbf'
          ]


# generate node tags file and node_coordinate file
#
# for city in cities:
#     p.parse(city)
#     node_tags = {}
#     # write the multi node tag to json file
#     path, _ = city.rsplit('/', 1)
#     output_tags = path + '/node_tags.json'
#     all_node = counter.nodeDic
#     for key in all_node:
#         node_tags[str(key)] = {}
#         tags, co = all_node[key]
#         for tag in tags:
#             node_tags[str(key)][tag] = tags[tag]
#     all_coord = counter.coordDic
#     with open(output_tags, 'w+') as _file:
#         _file.write(json.dumps(node_tags))

def get_index_from_list(array, start, end, lat):           #
    mid_index = (end - start)//2 + start        #
    if start <= end:
        if array[mid_index][1][1] < lat:
            return get_index_from_list(array, mid_index+1, end, lat)
        elif array[mid_index] > lat:
            return get_index_from_list(array, start, mid_index-1, lat)
        else:
            return mid_index
    else:
        return end if end > 0 else start


def get_nodes_from_list(array, lat):
    acc = 0.0005
    start = get_index_from_list(array, 0, len(array), lat - acc)
    end = get_index_from_list(array, 0, len(array), lat + acc)
    return array[start:end]


def get_distance(lng1, lat1, lng2, lat2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon = lng2-lng1
    dlat = lat2-lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    dis = 2*asin(sqrt(a))*6371*1000
    return dis


# generate city's lat/lon file
#
# for city in cities:
#     print city
#     ct, _ = city.split('/', 1)
#     network_file = ct + '/network/' + ct + '.network'
#     path, _ = city.rsplit('/', 1)
#     coordinate_file = path + '/node_coordinate.json'
#     with open(coordinate_file, 'r') as f:
#         node_to_coords = json.loads(f.readline())
#
#     # output_file = path + '/node_with_' + tag_class[0] + '.tag'
#     # with open(output_file, 'w+') as output:
#
#     node_coordinate = []
#     node_read = set()
#     with open(network_file, 'r') as f:
#         for line in f:
#             for node in line.strip().split(' '):
#                 if node in node_read:
#                     continue
#                 node_read.add(node)
#                 coordinate = node_to_coords[node]
#                 node_coordinate.append((node, coordinate))
#
#     with open(path + '/node_coordinate_lat.txt', 'w+') as lat_file:
#         for node in node_coordinate:
#             (node_id, [node_lat, node_lon]) = node
#             lat_file.write(node_id + ' ' + str(node_lat) + '\n')
#
#     with open(path + '/node_coordinate_lon.txt', 'w+') as lon_file:
#         for node in node_coordinate:
#             (node_id, [node_lat, node_lon]) = node
#             lon_file.write(node_id + ' ' + str(node_lon) + '\n')

city = cities[0]
ct, _ = cities[0].split('/', 1)
network_file = ct + '/network/' + ct + '.network'
path, _ = city.rsplit('/', 1)
coordinate_file = path + '/node_coordinate.json'
tags_file = path + '/node_tags.json'
node_tags_in_network = {}

with open(coordinate_file, 'r') as f:
    node_to_coords = json.loads(f.readline())

with open(tags_file, 'r') as f:
    node_to_tags = json.loads(f.readline())

node_coordinate = []
node_read = set()
with open(network_file, 'r') as f:
    for line in f:
        for node in line.strip().split(' '):
            if node in node_read: continue
            node_tags_in_network[node] = {}
            if node not in node_to_tags or 'highway' not in node_to_tags[node]:
                continue
            else:
                node_tags_in_network[node]['highway'] = node_to_tags[node]['highway']

            if node in node_read:
                continue
            node_read.add(node)
            coordinate = node_to_coords[node]
            coordinate = [float(coordinate[0]), float(coordinate[1])]
            node_coordinate.append((node, coordinate))

node_coordinate_lat = copy.copy(node_coordinate)
node_coordinate_lat.sort(key=lambda ele: ele[1][1])

mta_signals_file = path + '/MTA.signals_data.csv'
mta_stops_file = path + '/MTA.stopsigns_data.csv'
node_coordinate_mta_signals = []
with open(mta_stops_file, 'r') as f:
    first_flag = True
    for line in f:
        if first_flag:
            first_flag = False
            continue
        point, _ = line.strip().split(',', 1)
        _coords = point[7:-1]
        try:
            lon, lat = _coords.strip().split(" ")
            lon, lat = float(lon), float(lat)
            node_coordinate_mta_signals.append((lon, lat))
        except:
            continue


for _coords in node_coordinate_mta_signals:
    (_lon, _lat) = _coords
    _nodes = get_nodes_from_list(node_coordinate_lat, _lat)
    min_distance = float('inf')
    min_node = None
    for _node in _nodes:
        (node_lon, node_lat) = _node[1]
        dis = get_distance(_lon, _lat, node_lon, node_lat)
        if dis <= min_distance:
            min_distance = dis
            min_node = _node[0]
    if min_distance < 100 and 'highway' not in node_tags_in_network[min_node]:
        print 'insert traffic signals to ', min_node
        node_tags_in_network[min_node]['highway'] = 'stop'




# output_file = path + '/node_with_' + tag_class[0] + '.tag'
# with open(output_file, 'w+') as output:

# generate lat/lon files
#
# node_coordinate = []
# node_read = set()
# with open(network_file, 'r') as f:
#     for line in f:
#         for node in line.strip().split(' '):
#             if node in node_read:
#                 continue
#             node_read.add(node)
#             coordinate = node_to_coords[node]
#             node_coordinate.append((node, coordinate))
#
# with open(path + '/node_coordinate_lat.txt', 'w+') as lat_file:
#     for node in node_coordinate:
#         (node_id, [node_lat, node_lon]) = node
#         lat_file.write(node_id + ' ' + str(node_lat) + '\n')
#
# with open(path + '/node_coordinate_lon.txt', 'w+') as lon_file:
#     for node in node_coordinate:
#         (node_id, [node_lat, node_lon]) = node
#         lon_file.write(node_id + ' ' + str(node_lon) + '\n')












