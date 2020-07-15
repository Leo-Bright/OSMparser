from imposm.parser import OSMParser
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


# instantiate counter and parser and start parsing Proto ways
counter = OSMCounter()
p = OSMParser(concurrency=4, ways_callback=counter.ways, nodes_callback=counter.nodes,
              coords_callback=counter.coords, relations_callback=counter.relations)

cities = ['sanfrancisco/dataset/SanFrancisco.osm.pbf',
          'porto/dataset/Porto.osm.pbf',
          'tokyo/dataset/Tokyo.osm.pbf']

tag_without_crossing = ['turning_loop', 'give_way', 'bus_stop', 'turning_circle', 'traffic_signals', 'stop', 'speed_camera', 'motorway_junction', 'mini_roundabout']
tag_without_traffic = ['turning_loop', 'give_way', 'bus_stop', 'turning_circle', 'crossing', 'stop', 'speed_camera', 'motorway_junction', 'mini_roundabout']
tag_without_stop = ['turning_loop', 'give_way', 'bus_stop', 'turning_circle', 'traffic_signals', 'crossing', 'speed_camera', 'motorway_junction', 'mini_roundabout']
tag_without_crossing_and_traffic = ['turning_loop', 'give_way', 'bus_stop', 'turning_circle', 'stop', 'speed_camera', 'motorway_junction', 'mini_roundabout']
tag_classes = [tag_without_crossing, tag_without_traffic, tag_without_stop]

# extract node_with_crossing.tag file
for tag_class in tag_classes:
    for city in cities:
        p.parse(city)
        node_to_tag = {}
        # write the multi node tag to json file
        path, _ = city.rsplit('/', 1)
        all_node = counter.nodeDic
        for key in all_node:
            node_to_tag[str(key)] = {}
            tags, _ = all_node[key]
            for k in tags:
                node_to_tag[str(key)][k] = tags[k]

        ct, _ = city.split('/', 1)
        network_file = ct + '/network/' + ct + '.network'
        output_file = path + '/node_with_' + tag_class[4] + '.tag'
        with open(output_file, 'w+') as output:
            with open(network_file, 'r') as f:
                for line in f:
                    for node in line.strip().split(' '):
                        if node not in node_to_tag or 'highway' not in node_to_tag[node]:
                            output.write(node + ' 0\n')
                        else:
                            tags = node_to_tag[node]
                            highway_tag = tags['highway']
                            try:
                                node_tag_index = tag_class.index(highway_tag)
                            except ValueError:
                                node_tag_index = -1
                            output.write(node + ' ' + str(node_tag_index + 1) + '\n')

# extract node_with_none.tag file
# for city in cities:
#     p.parse(city)
#     node_to_tag = {}
#     # write the multi node tag to json file
#     path, _ = city.rsplit('/', 1)
#     all_node = counter.nodeDic
#     for key in all_node:
#         node_to_tag[str(key)] = {}
#         tags, _ = all_node[key]
#         for k in tags:
#             node_to_tag[str(key)][k] = tags[k]
#
#     ct, _ = city.split('/', 1)
#     network_file = ct + '/network/' + ct + '.network'
#     output_file = path + '/node_with_none.tag'
#     with open(output_file, 'w+') as output:
#         with open(network_file, 'r') as f:
#             for line in f:
#                 for node in line.strip().split(' '):
#                     if node not in node_to_tag or 'highway' not in node_to_tag[node]:
#                         output.write(node + ' 0\n')
#                     else:
#                         tags = node_to_tag[node]
#                         highway_tag = tags['highway']
#                         try:
#                             node_tag_index = tag_without_all.index(highway_tag)
#                         except ValueError:
#                             node_tag_index = -1
#                         output.write(node + ' ' + str(node_tag_index + 1) + '\n')


