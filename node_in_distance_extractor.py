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
        for osmid, lon, lat in coords:
            self.coordDic[osmid] = (lon, lat)

    def relations(self, relations):
        # callback method for relations
        for osmid, tags, refs in relations:
            self.relationDic[osmid] = (tags, refs)


counter = OSMCounter()
# instantiate counter and parser and start parsing Proto ways
p = OSMParser(concurrency=4, ways_callback=counter.ways, nodes_callback=counter.nodes,
              coords_callback=counter.coords, relations_callback=counter.relations)


def generate_node_tags_file(city):

    p.parse(city)
    node_tags = {}
    # write the multi node tag to json file
    path, _ = city.rsplit('/', 1)
    output_tags = path + '/node_tags.json'
    all_node = counter.nodeDic
    for key in all_node:
        node_tags[str(key)] = {}
        tags, co = all_node[key]
        for tag in tags:
            node_tags[str(key)][tag] = tags[tag]
    with open(output_tags, 'w+') as _file:
        _file.write(json.dumps(node_tags))
    return node_tags


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
    acc = 0.0002
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
def generate_city_coordinate_file(cities):
    for city in cities:
        print city
        p.parse(city)
        ct, _ = city.split('/', 1)
        network_file = ct + '/network/' + ct + '.network'
        path, _ = city.rsplit('/', 1)
        node_to_coords = {}
        for osm_id in counter.nodeDic:
            node_to_coords[str(osm_id)] = counter.nodeDic[osm_id][1]
        for osm_id in counter.coordDic:
            node_to_coords[str(osm_id)] = counter.coordDic[osm_id]
        coordinate_file = path + '/node_coordinate.json'
        with open(coordinate_file, 'w+') as f:
            f.write(json.dumps(node_to_coords))

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

        with open(path + '/node_coordinate_lat.txt', 'w+') as lat_file:
            for node in node_coordinate:
                (node_id, [node_lon, node_lat]) = node
                lat_file.write(node_id + ' ' + str(node_lat) + '\n')

        with open(path + '/node_coordinate_lon.txt', 'w+') as lon_file:
            for node in node_coordinate:
                (node_id, [node_lon, node_lat]) = node
                lon_file.write(node_id + ' ' + str(node_lon) + '\n')


def gen_node_to_tags_in_network(city, node_to_tags, mta_file):
    ct, _ = city.split('/', 1)
    network_file = ct + '/network/' + ct + '.network'
    path, _ = city.rsplit('/', 1)
    coordinate_file = path + '/node_coordinate.json'
    node_tags_in_network = {}

    with open(coordinate_file, 'r') as f:
        node_to_coords = json.loads(f.readline())

    node_coordinate = []
    node_read = set()
    with open(network_file, 'r') as f:
        for line in f:
            for node in line.strip().split(' '):

                if node in node_read:
                    continue

                if node in node_to_tags and 'highway' in node_to_tags[node]:
                    node_tags_in_network[node] = {'highway': node_to_tags[node]['highway']}

                node_read.add(node)
                coordinate = node_to_coords[node]
                coordinate = [float(coordinate[0]), float(coordinate[1])]
                node_coordinate.append((node, coordinate))

    node_coordinate_lat = copy.copy(node_coordinate)
    node_coordinate_lat.sort(key=lambda ele: ele[1][1])

    node_coordinate_mta_stop = []
    with open(mta_file, 'r') as f:
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
                node_coordinate_mta_stop.append((lon, lat))
            except:
                continue

    available = 0
    for _coords in node_coordinate_mta_stop:
        have_availables = False
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
            if min_distance > 10 or (min_node in node_tags_in_network and 'highway' in node_tags_in_network[min_node]):
                continue
            else:
                if min_node not in node_tags_in_network:
                    node_tags_in_network[min_node] = {}
                node_tags_in_network[min_node]['highway'] = 'stop'
                have_availables = True

                node_tags_in_network[min_node]['highway'] = 'stop'
        if have_availables:
            available += 1
    print "availables: ", available
    return node_tags_in_network


def statistics(city, node_to_tags, tag):
    stat_count = 0
    ct, _ = city.split('/', 1)
    network_file = ct + '/network/' + ct + '.network'
    with open(network_file, 'r') as f:
        for line in f:
            for node in line.strip().split(' '):

                if node not in node_to_tags:
                    continue

                if 'highway' in node_to_tags[node] and node_to_tags[node]['highway'] == tag:
                    stat_count += 1

    return stat_count


def statistics_distance(cities):
    for city in cities:
        print("start statistic for ", city)
        roadsegment = 0
        total_dis = 0
        ct, _ = city.split('/', 1)
        path, _ = city.rsplit('/', 1)
        network_file = ct + '/network/' + ct + '.network'
        coordinate_file = path + '/node_coordinate.json'
        with open(coordinate_file, 'r') as f:
            node_to_coords = json.loads(f.readline())
        with open(network_file, 'r') as f:
            for line in f:
                roadsegment += 1
                node1, node2 = line.strip().split(' ')
                _lon1, _lat1 = node_to_coords[node1]
                _lon2, _lat2 = node_to_coords[node2]
                dis = get_distance(_lon1, _lat1, _lon2, _lat2)
                total_dis += dis

        print("average distance is ", total_dis/roadsegment)


def run(city, node_to_tags_in_network):

    tag_without_crossing = ['turning_loop', 'give_way', 'bus_stop', 'turning_circle', 'traffic_signals', 'stop',
                            'speed_camera', 'motorway_junction', 'mini_roundabout']
    tag_without_traffic = ['turning_loop', 'give_way', 'bus_stop', 'turning_circle', 'crossing', 'stop', 'speed_camera',
                           'motorway_junction', 'mini_roundabout']
    tag_classes = [tag_without_crossing, tag_without_traffic]

    for tag_class in tag_classes:
        # write the multi node tag to json file
        path, _ = city.rsplit('/', 1)
        ct, _ = city.split('/', 1)
        network_file = ct + '/network/' + ct + '.network'
        output_file = path + '/node_with_' + tag_class[4] + '_increament_stop.tag'
        with open(output_file, 'w+') as output:
            with open(network_file, 'r') as f:
                for line in f:
                    for node in line.strip().split(' '):
                        if node not in node_to_tags_in_network or 'highway' not in node_to_tags_in_network[node]:
                            output.write(node + ' 0\n')
                        else:
                            tags = node_to_tags_in_network[node]
                            highway_tag = tags['highway']
                            try:
                                node_tag_index = tag_class.index(highway_tag)
                            except ValueError:
                                node_tag_index = -1
                            output.write(node + ' ' + str(node_tag_index + 1) + '\n')


if __name__ == '__main__':

    mta_signals_file = 'sanfrancisco/dataset/MTA.signals_data.csv'
    mta_stops_file = 'sanfrancisco/dataset/MTA.stopsigns_data.csv'

    cities = ['sanfrancisco/dataset/SanFrancisco.osm.pbf',
              'porto/dataset/Porto.osm.pbf',
              'tokyo/dataset/Tokyo.osm.pbf'
              ]

    # node_to_tags = generate_node_tags_file(cities[0])

    # generate_city_coordinate_file(cities)

    # node_to_tags_in_network = gen_node_to_tags_in_network(cities[0], node_to_tags, mta_stops_file)

    # run(cities[0], node_to_tags_in_network)

    # print statistics(cities[0], node_to_tags, 'traffic_signals')

    statistics_distance(cities)

