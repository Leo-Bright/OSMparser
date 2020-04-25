import os
import shutil
import json


# get names of files in the directory
def get_filename_list(src_path, regex):
    import os
    result = []
    filenames = os.listdir(src_path)
    for file_name in filenames:
        if file_name.find(regex) >= 0:
            result.append(file_name)
    return result


def main():

    src_path = 'sanfrancisco/network/'
    regex = 'sf_shortest_path.walks_part'
    filename_list = get_filename_list(src_path, regex)
    filename_list.sort(key=lambda x: x.rsplit('.', 1)[1])

    output_filename = 'sf_shortest_path.walks'
    output_file = open(src_path + output_filename, 'a')
    for file in filename_list:
        input_file = open(src_path + file, 'r')
        shutil.copyfileobj(input_file, output_file)
        input_file.close()
    output_file.close()


# main()
# with open('sanfrancisco/dataset/all_road_segments_dict.sanfrancisco') as f:
#     road_segments_file = f.readline()
#     road_segments = json.loads(road_segments_file)
#     print(len(road_segments))


def search_sf_station(station_file):

    stations = set()

    with open(station_file) as f:
        for line in f:
            lat = line[51:53]
            lat_all = line[51:59]
            lon = line[59:62]
            lon_all = line[59:68]
            if lat.strip() == '' or lon.strip() == '':
                continue
            station = line[4 - 1:9]
            diff_lat = abs(int(lat) - 37.5)
            diff_lon = abs(int(lon) - 122.3)
            if diff_lat < 1 and diff_lon < 1:
                stations.add((station, lat_all, lon_all))

    return stations



stations = search_sf_station('sanfrancisco/dataset/TMAS2012.sta')
for item in stations:
    print(item)
print(len(stations))
