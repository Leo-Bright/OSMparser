import os
import shutil


# get names of files in the directory
def get_filename_list(src_path, regex):
    import os
    result = []
    filenames = os.listdir(src_path)
    for file_name in filenames:
        if file_name.find(regex) >= 0:
            result.append(file_name)
    return result


def main(source_path, regex, output_filename):

    filename_list = get_filename_list(source_path, regex)
    filename_list.sort(key=lambda x: x.rsplit('.', 1)[1])

    output_file = open(source_path + output_filename, 'a')
    for file in filename_list:
        input_file = open(source_path + file, 'r')
        shutil.copyfileobj(input_file, output_file)
        input_file.close()
    output_file.close()


main(source_path='sanfrancisco/network/',
     regex='sf_shortest_path.walks_part',
     output_filename='sf_shortest_path.walks',
     )