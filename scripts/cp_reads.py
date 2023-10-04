import os
import subprocess

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

mdu_reads = "/home/mdu/reads"
data_folder = "./Analysis/1/Data/fastq"
run_id = "M2022-00579"

cmd = f"mkdir -p {mdu_reads}/{run_id}"
bash_command(cmd)
print(cmd)
with open("distribute_table.txt", 'r') as mytable:
    count = 0
    for line in mytable:
        if count == 0:
            count = 1
            continue
        info = line.strip().split("\t")
        mdu_id = info[0]
        cmd = f"mkdir -p {mdu_reads}/{run_id}/{mdu_id}"
        bash_command(cmd)
        print(cmd)
        cmd = f"cp {data_folder}/{mdu_id}* {mdu_reads}/{run_id}/{mdu_id}"
        bash_command(cmd)
        print(cmd)
