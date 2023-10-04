import os
import subprocess

path_one = "/home/mdu/data/M2023-00329-backup"
path_two = "/home/mdu/data/M2023-00329"

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

file_list = []
for folder in os.listdir(path_two):
    file_list.append(folder)

for mf in os.listdir(path_one):
    if mf not in file_list:
        command = f"cp -r {path_one}/{mf} {path_two}/"
        print(command)
        bash_command(command)
