import subprocess

proc = subprocess.run(['export PYTHONPATH=.'], shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

if len(proc.stderr) != 0:
    print('Could not set the env var :\'(')
    print(str(proc.stderr.decode()))
    exit(-1)

else:
    print('DONE')
