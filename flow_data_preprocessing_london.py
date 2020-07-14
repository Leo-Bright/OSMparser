import pickle as pkl
import os
from datetime import datetime


def process_flow_data_files(flow_data_file_location):

    subdirs = os.listdir(flow_data_file_location)

    flow_data = {}
    count = 0
    for s in subdirs:
        subdir = flow_data_file_location + '/' + s
        subdir_files = os.listdir(subdir)
        for file_name in subdir_files:
            if file_name.endswith('.csv'):
                count += 1
                data = extract_flow_data(subdir + '/' + file_name)
                flow_data[s] = []
                flow_data[s].append(data)
    print count
    return flow_data


def extract_flow_data(flow_file_path):

    flow = {}

    flow['total_flow'] = 0
    flow['week_flow'] = 0
    flow['weekend_flow'] = 0

    with open(flow_file_path) as f:
        seg = 96
        l_num = 0
        available_lines = []
        for line in f:
            if l_num in (0, 2, 3):
                l_num += 1
                continue
            cols = line.strip().split(',')
            if l_num == 1:
                legecy_tid = cols[1]
            elif len(cols) > 10:
                available_lines.append(cols)
            l_num += 1

    # total_lines_num = len(available_lines)
    # split_time = total_lines_num // seg

    for cols in available_lines:

        date = cols[0]
        cars = cols[3]

        dt_format = "%Y-%m-%d"
        dt = datetime.strptime(date, dt_format)
        wd = dt.weekday()

        if cars.strip() =='':
            cars = '0'
        flow['total_flow'] += int(cars)
        if wd == 5 or wd == 6:
            flow['weekend_flow'] += int(cars)
        else:
            flow['week_flow'] += int(cars)
    return flow







if __name__ == '__main__':

    flow_month = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    stations_file_path = 'sanfrancisco/dataset/flow_data/TMAS2012.sta'

    lat_lon_file_path = 'sanfrancisco/dataset/flow_data/tmas2012_stations.coordinate'

    search_coordinate = [36.80776731, -85.46235191]
    search_lat = search_coordinate[0]
    search_lon = search_coordinate[1]

    flow_data_dir = "E:/Nicole/traffic flow/London/road flow data"
    flow_data = process_flow_data_files(flow_data_dir)
    print flow_data

    # s_flow_data = find_station_flow_data(flow_month, stations)
    #
    # flow_stat_file_path = 'sanfrancisco/dataset/flow_data/flow_data_stat_2.sanfrancisco'
    #
    # output_flow_stat(s_flow_data, flow_stat_file_path)