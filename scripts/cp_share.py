import os
import subprocess

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

with open("share.tab", 'r') as myshare:
    for line in myshare:
        mid, r1, r2 = line.strip().split("\t")
        print(f"copying reads for {mid}")
        cmd = f"cp {r1} ./share"
        bash_command(cmd)
        cmd = f"cp {r2} ./share"
        bash_command(cmd)
