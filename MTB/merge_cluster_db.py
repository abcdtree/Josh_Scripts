import json
import os
from datetime import datetime
import subprocess

def load_json(mfile):
	json_file = open(mfile, 'r')
	db_dict = json.load(json_file)
	json_file.close()
	return db_dict

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def get_current_datetime():
	now = datetime.now()
	current_time = now.strftime("%Y%m%d")
	return current_time

def back_up_dbs():
	current_time = get_current_datetime()
	file_path = "/home/jianszhang/mdu_jobs/cleptr_db"
	ST_list = ["1", "2", "3", "4"]
	for st in ST_list:
		cluster_db_path = os.path.join(file_path, f"Lineage_{st}", "possible_clusters.json")
		sample_db_path = os.path.join(file_path, f"Lineage_{st}", "possible_samples.json")
		cmd = f"cp -f {str(cluster_db_path)} {str(cluster_db_path)}.backup.{current_time}"
		bash_command(cmd)
		cmd = f"cp -f {str(sample_db_path)} {str(sample_db_path)}.backup.{current_time}"
		bash_command(cmd)


def save_db_to_json(db, path):
	with open(path, 'w') as json_file:
		json.dump(db, json_file, indent = 4)

def find_the_best_cluster_number(c_n, exist_list, top_c_n):
	if c_n == "UC":
		return c_n
	elif c_n not in exist_list:
		return c_n
	else:
		new_c_n = str(top_c_n + 1)
		return new_c_n

def sort_cluster_name(x):
	if x == "UC":
		return 0
	else:
		return int(x)

def change_sub_files(lineage, old_c, new_c):
	file_path = f"/home/jianszhang/mdu_jobs/cleptr_db/Lineage_{lineage}"
	cmd = f"mv {file_path}/clst_{old_c}_samples.json {file_path}/clst_{new_c}_samples.json"
	bash_command(cmd)
	cmd = f"mv {file_path}/clst_{old_c}_clusters.json {file_path}/clst_{new_c}_clusters.json"
	bash_command(cmd)
	cmd = f"mv {file_path}/tmp_{old_c}.txt {file_path}/tmp_{new_c}.txt"
	bash_command(cmd)

#backup all dbs
back_up_dbs()

file_path = "/home/jianszhang/mdu_jobs/cleptr_db"
ST_list = ["1", "2", "3", "4"]

## find cluster name that need to be changed
merge_cluster_db = {}
change_list = []

all_cluster_name = set()
for st in ST_list:
	cluster_db_path = os.path.join(file_path, f"Lineage_{st}", "possible_clusters.json")
	c_cluster_db = load_json(cluster_db_path)
	m_set = set(list(c_cluster_db.keys()))
	all_cluster_name.update(m_set)

all_cluster_name_list = sorted(list(all_cluster_name), key=sort_cluster_name)
top_value = int(all_cluster_name_list[-1])
print(top_value)


for st in ST_list:
	cluster_db_path = os.path.join(file_path, f"Lineage_{st}", "possible_clusters.json")
	#sample_db_path = os.path.join(file_path, f"Lineage_{st}", "possible_samples.json")
	c_cluster_db = load_json(cluster_db_path)
	c_keys = list(c_cluster_db.keys())
	c_keys.reverse()
	for m_c in c_keys:
		exist_list = list(merge_cluster_db.keys())
		new_c_name = find_the_best_cluster_number(m_c, exist_list, top_value)
		if m_c != new_c_name:
			change_list.append([st, m_c, new_c_name])
			top_value += 1
		merge_cluster_db[new_c_name] = c_cluster_db.get(m_c)

merge_cluster_db_path = "/home/jianszhang/mdu_jobs/cleptr_db/merge_db.json"
save_db_to_json(merge_cluster_db, merge_cluster_db_path)
with open("change_file.txt_20231003", 'w') as myout:
	for line in change_list:
		myout.write("\t".join(line) + "\n")

##change information in cluster_db and sample_db

for line in change_list:
	st, old_c, new_c = line
	cluster_db_path = os.path.join(file_path, f"Lineage_{st}", "possible_clusters.json")
	c_cluster_db = load_json(cluster_db_path)
	sample_list = []
	ids = c_cluster_db.get(old_c)
	for mid in ids:
		sample_list.append([mid, new_c])
	#change clusters_db
	c_cluster_db[new_c] = c_cluster_db.pop(old_c)
	save_db_to_json(c_cluster_db, cluster_db_path)
	#change files in Lineage folder
	change_sub_files(st, old_c, new_c)
	#change sample db
	sample_db_path = os.path.join(file_path, f"Lineage_{st}", "possible_samples.json")
	sample_db = load_json(sample_db_path)
	for line in sample_list:
		mid, new_c = line
		info_dc = sample_db.get(mid)
		c_dict = info_dc.get("clusters")
		m_time = list(c_dict.keys())[-1]
		c_dict[m_time] = new_c
		info_dc["clusters"] = c_dict
		sample_db[mid] = info_dc
	save_db_to_json(sample_db, sample_db_path)

print("all cluster name updated, please run combine.py to create report files")
