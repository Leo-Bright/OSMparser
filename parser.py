from imposm.parser import OSMParser
import pickle as pkl


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


if __name__ == '__main__':

    # instantiate counter and parser and start parsing Proto ways
    counter = OSMCounter()
    p = OSMParser(concurrency=4, ways_callback=counter.ways, nodes_callback=counter.nodes,
                  coords_callback=counter.coords, relations_callback=counter.relations)
    p.parse('philadelphia/dataset/Philadelphia.osm-2.pbf')

    with open('philadelphia/dataset/philadelphia_parsed_obj.pkl', 'wb') as f:
        pkl.dump(counter, f)

    with open('philadelphia/dataset/philadelphia_parsed_obj.pkl', 'rb') as f:
        counter1 = pkl.load(f)
        for key in counter1.relationDic:
            print key
            break