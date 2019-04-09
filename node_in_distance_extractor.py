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

cities = ['porto/dataset/Porto.osm.pbf',
          ]


for city in cities:
    p.parse(city)
    node_coordinate = {}
    # write the multi node tag to json file
    path, _ = city.rsplit('/', 1)
    output = path + '/node_coordinate.json'
    with open(output, 'w+') as _file:
        all_node = counter.nodeDic
        for key in all_node:
            node_coordinate[str(key)] = {}
            _, co = all_node[key]
            node_coordinate[str(key)] = co
        all_coord = counter.coordDic
        for key in all_coord:
            node_coordinate[str(key)] = all_coord[key]
        _file.write(json.dumps(node_coordinate))


def get_index_from_list(array, start, end, value, axis=0,):
    if start == end:
        return start
    if start < 0:
        return 0
    if end > len(array):
        return len(array)-1
    size = end - start
    index = size // 2 + start
    x = array[index][1][axis]
    if x - value < 0.00001:
        return index
    elif x < value:
        return get_index_from_list(array, index + 1, end, value, axis)
    else:
        return get_index_from_list(array, start, index - 1, value, axis)


def get_range_from_list(array, lat, accuracy, axis=0,):
    acc = accuracy / 110
    start = get_index_from_list(array, 0, len(array), lat - acc, axis=axis)
    end = get_index_from_list(array, 0, len(array), lat + acc, axis=axis)
    return (start, end)


def get_distance(lng1,lat1,lng2,lat2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon=lng2-lng1
    dlat=lat2-lat1
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    dis=2*asin(sqrt(a))*6371*1000
    return dis


for city in cities:
    print city
    ct, _ = city.split('/', 1)
    network_file = ct + '/network/' + ct + '.network'
    path, _ = city.rsplit('/', 1)
    coordinate_file = path + '/node_coordinate.json'
    with open(coordinate_file, 'r') as f:
        node_to_coords = json.loads(f.readline())

    # output_file = path + '/node_with_' + tag_class[0] + '.tag'
    # with open(output_file, 'w+') as output:

    node_coordinate = []
    node_read = set()
    with open(network_file, 'r') as f:
        for line in f:
            for node in line.strip().split(' '):
                if node in node_read:
                    continue
                node_read.add(node)
                coordinate = node_to_coords[node]
                node_coordinate.append((node, coordinate))

    with open(path + '/node_coordinate.txt', 'w+') as coordinate_file:
        for node in node_coordinate:
            (node_id, [node_lat, node_lon]) = node
            coordinate_file.write(node_id + ' ' + str(node_lat) + ' ' + str(node_lon) + '\n')

    # node_coordinate_lat = copy.copy(node_coordinate)
    # node_coordinate_lon = copy.copy(node_coordinate)
    # node_coordinate_lat.sort(key=lambda ele: ele[1][0])
    # node_coordinate_lon.sort(key=lambda ele: ele[1][1])
    #
    # with open(path + '/node_coordinate.txt', 'w+') as coordinate_file:
    #     for node in node_coordinate:
    #         neighbour = set()
    #         (node_id, [node_lat, node_lon]) = node
    #         neighbour.add(node_id)
    #         (lat_start, lat_end) = get_range_from_list(node_coordinate_lat, node_lat, 0.5, axis=0)
    #         (lon_start, lon_end) = get_range_from_list(node_coordinate_lon, node_lon, 0.5, axis=1)
    #         _neighbour_lat = node_coordinate_lat[lat_start:lat_end]
    #         _neighbour_lon = node_coordinate_lon[lon_start:lon_end]
    #         for no in _neighbour_lat:
    #             if no[0] not in neighbour:
    #                 (lat, lon) = no[1]
    #                 dis = get_distance(lon, lat, node_lon, node_lat)
    #                 if dis <= 0.5:
    #                     neighbour.add(no[0])
    #         for no in _neighbour_lon:
    #             if no[0] not in neighbour:
    #                 (lat, lon) = no[1]
    #                 dis = get_distance(lon, lat, node_lon, node_lat)
    #                 if dis <= 0.5:
    #                     neighbour.add(no[0])
    #         neighbour.discard(node_id)
    #         coordinate_file.write(node_id + ' ')
    #         for n in neighbour:
    #             coordinate_file.write(n + ' ')
    #         coordinate_file.write('\n')








