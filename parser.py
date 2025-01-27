from imposm.parser import OSMParser
import json


# simple class that handles the parsed OSM data.
class OSMCounter(object):
    relationDic = {} #{osmid:(tag, refs)}
    coordDic = {} #{osmid:(lat, lon)}
    crossing_nodes = {} #{osmid:(tag, coordinary)}
    nodeDic = {} #{osmid:(tag, coordinary)}
    highwayDic = {}  # {osmid:(tag, refs)}
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
            if 'highway' in tags:
                if 'crossing' == tags['highway']:
                    self.crossing_nodes[osmid] = (tags, coordinary)
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

city_name = 'newyork'
p.parse(city_name + '/dataset/newyork.osm.pbf')

with open(city_name + '/dataset/' + city_name + '_ways.json', 'w+') as f:
    f.write(json.dumps(counter.wayDic))

with open(city_name + '/dataset/' + city_name + '_relations.json', 'w+') as f:
    f.write(json.dumps(counter.relationDic))

with open(city_name + '/dataset/' + city_name + '_coords.json', 'w+') as f:
    f.write(json.dumps(counter.coordDic))

with open(city_name + '/dataset/' + city_name + '_nodes.json', 'w+') as f:
    f.write(json.dumps(counter.nodeDic))

with open(city_name + '/dataset/' + city_name + '_highways.json', 'w+') as f:
    f.write(json.dumps(counter.highwayDic))

with open(city_name + '/dataset/' + city_name + '_crossing_nodes.json', 'w+') as f:
    f.write(json.dumps(counter.crossing_nodes))