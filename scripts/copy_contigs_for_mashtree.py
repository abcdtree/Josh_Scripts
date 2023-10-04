import os
import subprocess

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

with open("contigs.tab", 'r') as mytab:
    for line in mytab:
        mid, mpath = line.strip().split("\t")
        command = f"ln -s {mpath} contigs/{mid}.fa"
        bash_command(command)
