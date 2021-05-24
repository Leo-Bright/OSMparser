from math import radians, cos, sin, asin, sqrt
import json, copy, pickle as pkl
import csv


def get_parent_dir(path):
    parent_dir, _ = path.split('/', 1)
    return parent_dir


def get_up_layer_path(path):
    path, _ = path.rsplit('/', 1)
    return path


def gen_node_tags_json(city_path, parsed_obj_path):

    print 'generate node2tag json file for ', city_path

    with open(parsed_obj_path, 'rb') as f:
        parsed_obj = pkl.load(f)
    node_tags = {}

    # write the multi node tag to json file
    path = get_up_layer_path(city_path)
    output_tags = path + '/node2tags.json'
    all_node = parsed_obj.nodeDic
    for key in all_node:
        node_tags[str(key)] = {}
        tags, co = all_node[key]
        for tag in tags:
            node_tags[str(key)][tag] = tags[tag]
    with open(output_tags, 'w+') as _file:
        _file.write(json.dumps(node_tags))
    return node_tags


def gen_node_way_json(city_path, parsed_obj_path):

    print 'generate node2way json file for ', city_path

    with open(parsed_obj_path, 'rb') as f:
        parsed_obj = pkl.load(f)
    node2way = {}

    # write the node2way relation to json file
    path = get_up_layer_path(city_path)
    output = path + '/node2way.json'
    ways = parsed_obj.wayDic
    for key in ways:
        tag, refs = ways[key]
        for node in refs:
            node2way[node] = key
    with open(output, 'w+') as node2way_file:
        node2way_file.write(json.dumps(node2way))
    return node2way


def get_index_from_list(array, start, end, lat):
    mid_index = (end - start)//2 + start
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
    start = get_index_from_list(array, 0, len(array) - 1, lat - acc)
    end = get_index_from_list(array, 0, len(array) - 1, lat + acc)
    return array[start:end]


def get_distance(lng1, lat1, lng2, lat2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon = lng2-lng1
    dlat = lat2-lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    dis = 2*asin(sqrt(a))*6371*1000
    return dis


# generate city's lat/lon file
def gen_city_coordinate_json(cities_path, parsed_obj_path):

    for city_path in cities_path:

        print 'generate node2coords json file for ', city_path

        with open(parsed_obj_path, 'rb') as f:
            parsed_obj = pkl.load(f)
        ct = get_parent_dir(city_path)
        network_file = ct + '/network/' + ct + '.network'
        path = get_up_layer_path(city_path)

        node2coords = {}
        for osm_id in parsed_obj.nodeDic:
            node2coords[str(osm_id)] = parsed_obj.nodeDic[osm_id][1]
        for osm_id in parsed_obj.coordDic:
            node2coords[str(osm_id)] = parsed_obj.coordDic[osm_id]
        coordinate_file = path + '/node2coords.json'
        with open(coordinate_file, 'w+') as f:
            f.write(json.dumps(node2coords))

        node_coordinate = []
        node_read = set()
        with open(network_file) as f:
            for line in f:
                for node in line.strip().split(' '):
                    if node in node_read:
                        continue
                    node_read.add(node)
                    coordinate = node2coords[node]
                    node_coordinate.append((node, coordinate))

        with open(path + '/node_latitude.txt', 'w+') as lat_file:
            for node in node_coordinate:
                (node_id, [node_lon, node_lat]) = node
                lat_file.write(node_id + ' ' + str(node_lat) + '\n')

        with open(path + '/node_longitude.txt', 'w+') as lon_file:
            for node in node_coordinate:
                (node_id, [node_lon, node_lat]) = node
                lon_file.write(node_id + ' ' + str(node_lon) + '\n')


# supplement stop_tag for network highway node
def supp_node2tags_in_network(city_path, node_to_tags, mta_file):
    ct = get_parent_dir(city_path)
    network_file = ct + '/network/' + ct + '.network'
    path = get_up_layer_path(city_path)
    coordinate_file = path + '/node_coordinate.json'
    supplement_stop_node = path + '/node_supplement.txt'
    node_tags_in_network = {}

    with open(coordinate_file, 'r') as f:
        node_to_coords = json.loads(f.readline())

    supplement_stop_node_file = open(supplement_stop_node, 'w+')

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
                else:
                    supplement_stop_node_file.write(min_node + '\n')
                node_tags_in_network[min_node]['highway'] = 'stop'
                have_availables = True
        if have_availables:
            available += 1
    print "availables: ", available
    return node_tags_in_network


def statistics(city_path, node_to_tags, tag):
    stat_count = 0
    ct = get_parent_dir(city_path)
    network_file = ct + '/network/' + ct + '.network'
    with open(network_file, 'r') as f:
        for line in f:
            for node in line.strip().split(' '):

                if node not in node_to_tags:
                    continue

                if 'highway' in node_to_tags[node] and node_to_tags[node]['highway'] == tag:
                    stat_count += 1

    return stat_count


def statistics_avg_distance(cities_path):
    for city_path in cities_path:
        print("start statistic for ", city_path)
        roadsegment = 0
        total_dis = 0
        ct = get_parent_dir(city_path)
        path = get_up_layer_path(city_path)
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


def gen_increament_tag_file(city, node_to_tags_in_network):

    tag_without_crossing = ['turning_loop', 'give_way', 'bus_stop', 'turning_circle', 'traffic_signals', 'stop',
                            'speed_camera', 'motorway_junction', 'mini_roundabout']
    tag_without_traffic = ['turning_loop', 'give_way', 'bus_stop', 'turning_circle', 'crossing', 'stop', 'speed_camera',
                           'motorway_junction', 'mini_roundabout']
    tag_classes = [tag_without_crossing, tag_without_traffic]

    for tag_class in tag_classes:
        # write the multi node tag to json file
        path = get_up_layer_path(city)
        ct = get_parent_dir(city)
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


# comput overlap node in network from crash file
def compute_overlap_crash_node(city_path, crash_file_path, highway=True, allNodes=False):

    crash_coordinates = []
    with open(crash_file_path) as f:
        first_line = True
        for line in f:
            if first_line:
                first_line = False
                continue
            items = line.strip().split(',')
            crn = items[0]
            lon = items[-3].strip('"')
            lat = items[-4].strip('"')
            if lat == '' or lon == '':
                continue
            else:
                lon = float(lon)
                lat = float(lat)
            crash_coordinates.append((lon, lat))

    ct = get_parent_dir(city_path)
    network_file_path = ct + '/network/' + ct
    if not highway:
        network_file_path = network_file_path + '_allWays'
    if allNodes:
        network_file_path = network_file_path + '_allNodes.network'
    else:
        network_file_path = network_file_path + '.network'
    path = get_up_layer_path(city_path)
    coordinate_file = path + '/node_coordinate.json'

    node_tags_in_network = {}

    with open(coordinate_file, 'r') as f:
        node2coords = json.loads(f.readline())

    node_coordinate = []
    node_read = set()
    with open(network_file_path, 'r') as f:
        for line in f:
            for node in line.strip().split(' '):

                if node in node_read:
                    continue

                node_read.add(node)
                coordinate = node2coords[node]
                coordinate = [float(coordinate[0]), float(coordinate[1])]
                node_coordinate.append((node, coordinate))

    node_coordinate_lat = copy.copy(node_coordinate)
    node_coordinate_lat.sort(key=lambda ele: ele[1][1])

    available = 0
    for _coords in crash_coordinates:
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
            if min_distance > 50:
                continue
            else:
                have_availables = True

        if have_availables:
            available += 1

    print "availables: ", available
    return node_tags_in_network


# map crash node coordinate to a road segment
def map_crash_coords_to_segment(city_path, crash_file_path, highway=True):

    print 'map crashes to segment for ', city_path

    crash_coordinates = []
    with open(crash_file_path) as f:
        crash_csv = csv.reader(f)
        crash_headers = next(crash_csv)
        for row in crash_csv:
            crash_id = row[23]
            lat = row[4]
            lon = row[5]
            if not crash_id.isdigit() or lat == '' or lon == '':
                continue
            else:
                lon = float(lon)
                lat = float(lat)
            crash_coordinates.append((crash_id, (lon, lat)))

    ct = get_parent_dir(city_path)
    network_file_path = ct + '/network/' + ct
    if not highway:
        network_file_path = network_file_path + '_allWays'
    network_file_path = network_file_path + '.network'
    path = get_up_layer_path(city_path)
    coordinate_file = path + '/node2coords.json'

    with open(coordinate_file, 'r') as f:
        node2coords = json.loads(f.readline())

    node2way_file = path + '/node2way.json'

    with open(node2way_file, 'r') as f:
        node2way = json.loads(f.readline())

    node_coordinate = []
    node_read = set()
    with open(network_file_path, 'r') as f:

        for line in f:
            for node in line.strip().split(' '):

                if node in node_read:
                    continue

                node_read.add(node)
                coordinate = node2coords[node]
                coordinate = [float(coordinate[0]), float(coordinate[1])]
                node_coordinate.append((node, coordinate))

    node_coordinate_lat = copy.copy(node_coordinate)
    node_coordinate_lat.sort(key=lambda ele: ele[1][1])

    crash2way = {}
    success_count = 0
    fail_count = 0
    fail_crash = []
    print 'How many crash node should be process: ', len(crash_coordinates)
    for _coords in crash_coordinates:

        have_availables = False
        (crash_id, (_lon, _lat)) = _coords

        if success_count > 1000:
            break

        print 'Start process No ' + str(success_count) + ' crash, id: ', crash_id

        _nodes = get_nodes_from_list(node_coordinate_lat, _lat)
        min_distance = float('inf')
        min_node = None
        for _node in _nodes:
            (node_lon, node_lat) = _node[1]
            dis = get_distance(_lon, _lat, node_lon, node_lat)
            if dis <= min_distance:
                min_distance = dis
                min_node = _node[0]
        if min_distance > 50:
            fail_count += 1
            fail_crash.append(crash_id)
            continue
        else:
            success_count += 1
            min_way = node2way[min_node]
            crash2way[crash_id] = min_way

    append_ext_info_to_csv(crash2way, crash_file_path)

    with open(path + '/crash2way.json', 'w+') as crash_json:
        crash_json.write(json.dumps(crash2way))
    with open(path + '/crash2way.csv', 'w+') as crash_csv:
        crash_csv.write("COLLISION_ID, OSM_ID_WAY\n")
        for key in crash2way:
            crash_csv.write(key + ', ' + str(crash2way[key]) + '\n')

    with open(path + '/failedcrash.txt', 'w+') as file:
        for ele in fail_crash:
            file.write(str(ele) + '\n')

    print 'succes: ', success_count
    print 'failed: ', fail_count


def append_ext_info_to_csv(crash2way, collision_file, crash_way_json='newyork/dataset/crash2way.json'):

    if crash2way is None:
        with open(crash_way_json, 'r') as f:
            crash2way = json.loads(f.readline())

    path, extension = collision_file.rsplit('.', 1)
    output = path + '_have_wayID.' + extension

    extended_crash = []
    with open(output, 'w+') as output_file:
        output_csv = csv.writer(output_file)
        with open(collision_file) as crash_file:
            crash_csv = csv.reader(crash_file)
            headers = next(crash_csv)
            headers.append('OSM_WAY_ID')
            headers.append('WEEK_DAY')
            extended_crash.append(headers)
            for row in crash_csv:
                crash_id = row[23]
                if crash_id not in crash2way:
                    result = 'None'
                else:
                    result = str(crash2way[crash_id])
                row.append(result)
                row.append("1")
                extended_crash.append(row)
        output_csv.writerows(extended_crash)


if __name__ == '__main__':

    city_name = 'newyork'

    mta_signals_file = 'sanfrancisco/dataset/MTA.signals_data.csv'
    mta_stops_file = 'sanfrancisco/dataset/MTA.stopsigns_data.csv'

    cities_path = ['sanfrancisco/dataset/SanFrancisco.osm.pbf',
                   'porto/dataset/Porto.osm.pbf',
                   'tokyo/dataset/Tokyo.osm.pbf',
                   'philadelphia/dataset/Philadelphia.osm-2.pbf',
                   'newyork/dataset/newyork.osm.pbf'
                   ]

    collision_file = 'newyork/dataset/Motor_Vehicle_Collisions_Crashes2015.csv'

    # node2tags = gen_node_tags_json(cities_path[4], parsed_obj_pkl)

    # node2ways = gen_node_way_json(cities_path[4], parsed_obj_pkl)

    # gen_city_coordinate_json(cities_path[-1:], parsed_obj_pkl)

    # supplemeted_node2tags = supp_node2tags_in_network(cities_path[0], node2tags, mta_stops_file)

    # compute_overlap_crash_node(cities_path[3], 'philadelphia/dataset/CRASH_2016_Philadelphia.csv', highway=False, allNodes=True)

    # map_crash_coords_to_segment(cities_path[4], collision_file, highway=True)

    append_ext_info_to_csv(None, collision_file, crash_way_json='newyork/dataset/crash2way.json')

    # gen_increament_tag_file(cities_path[0], supplemeted_node2tags)

    # print statistics(cities_path[0], node2tags, 'traffic_signals')

    # statistics_avg_distance(cities_path)

