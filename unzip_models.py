import os.path
import zipfile

MODEL_ZIP_FILES = {'detection_models.zip': './lego_sorter_server/analysis/detection/models',
                   'classification_models.zip': './lego_sorter_server/analysis/classification/models'}

TIMEOUT = 30


def unzip_file(src_path: str, dst_path: str):
    print('Unzipping file: ' + str(src_path))
    with zipfile.ZipFile(src_path, 'r') as f:
        f.extractall(dst_path)
    print('\tDONE')


missing_files = 0
for f in MODEL_ZIP_FILES.keys():
    if not os.path.isfile(f):
        print('zip file "{0}" not found in current directory: {1}'.format(f, os.getcwd()))
        missing_files += 1

if missing_files > 0:
    exit(-1)

for file_name, destination_path in MODEL_ZIP_FILES.items():
    total_destination_path = os.path.abspath(destination_path)
    total_source_path = os.path.abspath(file_name)

    unzip_file(total_source_path, total_destination_path)
