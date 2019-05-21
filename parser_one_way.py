import json


def extract(road_segments_file, one_way_json):
    with open(road_segments_file) as f:
        road_segments = json.loads(f.readline())

    one_way = {}
    for gid in road_segments:
        segment = road_segments[gid]
        reverse = segment['reverse']
        if reverse < 0:
            one_way[gid] = segment['class_id']

    with open(one_way_json, 'w+') as f:
        f.write(json.dumps(one_way))


if __name__ == '__main__':

    extract(road_segments_file='sanfrancisco/dataset/all_road_segments_dict.sanfrancisco',
            one_way_json='sanfrancisco/dataset/sanfrancisco_segments_one_way_.json',
            )
