import os
import subprocess

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

ref_file = "/home/jianszhang/UNSGM_PTP/data/ref/Database.fasta"


db_list = []
with open(ref_file, 'r') as myref:
    for line in myref:
        if line[0] = ">":
            db_list.append(line.strip()[1:])

for rname in db_list:
    cmd = f"seqkit grep -p {rname} {ref_file} > /home/jianszhang/UNSGM_PTP/data/ref/sep/{rname}.fa"
    bash_command(cmd)
