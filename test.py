import os
import shutil
import json
import re
import csv


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


def delete_zero_of_walks(input, output):

    new_walks = []

    with open(input) as f:
        for line in f:
            id_zeros = line.strip().split(' ')
            ids = id_zeros[::2]
            new_walks.append(ids)

    with open(output, 'w+') as f:
        for walk in new_walks:
            f.write(' '.join(walk) + '\n')


def reg_number():

    collision_file = 'newyork/dataset/Motor_Vehicle_Collisions_Crashes2015.csv'

    with open(collision_file) as crash_file:
        crash_csv = csv.reader(crash_file)
        for line in crash_file:
            row = next(crash_csv)
            print 'LINE: ', line
            print 'ROW: ', row

    strings_to_test = ['01234567', '00000000', 'special-word 01234567'
                                               'special-word01234567', 'special-word01234567-']
    digits_present = [re.search("(\S*) *([0-9]{8}) *(\S*)", i)
                      for i in strings_to_test]
    for match in digits_present:
        print "{0:s} = {1:s} : {2:s} : {3:s}".format(match.group(0),
                                                     match.group(1), match.group(2), match.group(3))

if __name__ == '__main__':

    # stations = search_sf_station('sanfrancisco/dataset/TMAS2012.sta')
    # for item in stations:
    #     print(item)
    # print(len(stations))

    # delete_zero_of_walks('sanfrancisco/network/sanfrancisco_shortest.walks',
    #                      'sanfrancisco/network/sanfrancisco_shortest_nozero.walks')

    reg_number()