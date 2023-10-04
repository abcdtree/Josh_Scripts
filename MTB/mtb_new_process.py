import csv
import json
import subprocess
import os

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

mdate = "2023-10-03"

#lineage_list = ["1", "2", "3", "4", "5"]
lineage_list = ["1", "2", "3","4"]
mtb_analysis_path = "/home/jianszhang/analysis/tb_dev"
c_path = "/home/jianszhang/mdu_jobs/cleptr_db"
#STEP1
#cp files
for lineage in lineage_list:
    cmd = f"cp {mtb_analysis_path}/Lineage_{lineage}/snp_clusters.txt.{mdate} {c_path}/Lineage_{lineage}/"
    print(cmd)
    bash_command(cmd)
#STEP2
    os.chdir(f"{c_path}/Lineage_{lineage}")
    cmd = f"python3 make_uc.py snp_clusters.txt.{mdate} snp_clusters_uc.txt.{mdate}"
    print(cmd)
    bash_command(cmd)
    cmd = f"cleptr run -i snp_clusters_uc.txt.{mdate} -s possible_samples.json -c possible_clusters.json --cluster_col Tx:12 --id_col Seq_ID"
    print(cmd)
    bash_command(cmd)
    cmd = f"cleptr report -s possible_samples.json -p Lineage_{lineage}_{mdate}_report --id_col Seq_ID"
    print(cmd)
    bash_command(cmd)
    cmd = f"python3 make_high.py snp_clusters_uc.txt.{mdate} possible_samples.json Tx:5 Seq_ID possible_clusters.json"
    print(cmd)
    bash_command(cmd)
