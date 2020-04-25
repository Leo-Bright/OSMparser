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


def flow_statistic(flow_datas):

    stat = {}
    stat['total_days'] = 0
    stat['week_days'] = 0
    stat['weekend_days'] = 0
    stat['total_flow'] = 0
    stat['week_flow'] = 0
    stat['weekend_flow'] = 0

    for row in flow_datas:
        day4week = row[19]
        flow_data = row[20:140]
        if flow_data.split() == '' or day4week == ' ':
            continue

        nums = []
        idx = 0
        while idx < len(flow_data):
            _flow = flow_data[idx:idx + 5].lstrip('0')
            if _flow == '':
                _flow = '0'
            nums.append(int(_flow))
            idx += 5
        sum_flow = sum(nums)

        stat['total_days'] += 1
        stat['total_flow'] += sum_flow

        if day4week in set(['2', '3', '4', '5', '6']):
            stat['week_days'] += 1
            stat['week_flow'] += sum_flow
        else:
            stat['weekend_days'] += 1
            stat['weekend_flow'] += sum_flow

    stat['total_avg'] = stat['total_flow'] // stat['total_days']
    stat['week_avg'] = stat['week_flow'] // stat['week_days']
    stat['weekend_avg'] = stat['weekend_flow'] // stat['weekend_days']

    return stat


def find_station_flow_data(months, stations):

    s_flow_data = {}

    all_station = set()
    for station in stations:

        all_station.add(station[0])

        station_info = {}
        station_info['station_id'] = station[0]
        station_info['lat'] = station[1]
        station_info['lon'] = station[2]
        station_info['data'] = []
        s_flow_data[station[0]] = station_info

    for month in months:
        file_path = 'sanfrancisco/dataset/flow_data/CA_' + month + '_2012 (TMAS).VOL'
        with open(file_path) as f:
            for line in f:
                station_id = line[5:11]
                if station_id in all_station:
                    s_flow_data[station_id]['data'].append(line)

    for key in s_flow_data:
        datas = s_flow_data[key]['data']
        if len(s_flow_data[key]['data']) > 0:
            s_flow_data[key]['stat'] = flow_statistic(datas)

    return s_flow_data


def output_flow_stat(stations_flow_data, output_file_path):
    with open(output_file_path, 'w+') as f:
        f.write('station_id lat lon total_days total_avg week_days week_avg weekend_days weekend_avg \n')
        for key in stations_flow_data:
            station_flow_stat = stations_flow_data[key]
            if 'stat' in station_flow_stat:
                stat_data = station_flow_stat['stat']
                station_id = station_flow_stat['station_id']
                lat = station_flow_stat['lat']
                lon = station_flow_stat['lon']
                f.write(station_id + ' ' + lat + ' ' + lon + ' ' + str(stat_data['total_days']) + ' ' +
                        str(stat_data['total_avg']) + ' ' + str(stat_data['week_days']) + ' ' +
                        str(stat_data['week_avg']) + ' ' + str(stat_data['weekend_days']) + ' ' +
                        str(stat_data['weekend_avg']) + '\n')


if __name__ == '__main__':

    flow_month = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    stations = search_sf_station('sanfrancisco/dataset/flow_data/TMAS2012.sta')

    s_flow_data = find_station_flow_data(flow_month, stations)

    flow_stat_file_path = 'sanfrancisco/dataset/flow_data/flow_data_stat_2.sanfrancisco'

    output_flow_stat(s_flow_data, flow_stat_file_path)