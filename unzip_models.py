import os.path
import subprocess

MODEL_ZIP_FILES = {'detection_models.zip': './lego_sorter_server/analysis/detection/models',
                   'classification_models.zip': './lego_sorter_server/analysis/classification/models'}
TIMEOUT = 30

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

    print('Unziping file: "{0}", timeout {1}s...'.format(file_name, TIMEOUT))
    proc = subprocess.run('unzip {0} -d {1}'.format(total_source_path, total_destination_path), shell=True,
                          stderr=subprocess.PIPE, stdout=subprocess.PIPE, timeout=TIMEOUT)

    if len(proc.stderr) != 0:
        print('Error occurred while unziping files:')
        print(str(proc.stderr.decode()))

    else:
        print(str(proc.stdout.decode()))
        print('Unziping successful')
