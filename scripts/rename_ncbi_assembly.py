import os
import subprocess

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

for mfile in os.listdir("./"):
    if mfile[-3:] == "fna":
        with open(mfile, 'r') as myf:
            first_line = myf.readline()
        info = first_line.split()
        sp = info[1] + "_" + info[2]
        cmd = f"mv {mfile} {mfile[:-4]}_{sp}.fna"
        bash_command(cmd)
