import csv
import json
import subprocess
import pandas as pd
import os

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

def save_db_to_json(db, path):
	with open(path, 'w') as json_file:
		json.dump(db, json_file, indent = 4)

#load change list
df_change_list = pd.read_csv("change_list.new.20230723")[["MDU_ID", "TYPE_OF_CHANGE", "DETAIL"]]
#print(df_change_list.head())

df_lineage_info = pd.read_csv("lineage_checked.csv")[["Seq_ID", "Phylogenetic lineage"]]
df_lineage_info.columns = ["MDU_ID", "Lineage"]
#print(df_lineage_info.head())

df_merge = df_change_list.merge(df_lineage_info, on="MDU_ID", how="left")
#print(df_merge.head())

info_dict = {}
for index, row in df_merge.iterrows():
    mdu_id = row["MDU_ID"]
    change_type = row["TYPE_OF_CHANGE"]
    change_dt = row["DETAIL"]
    lineage = row["Lineage"]
    change_dict = info_dict.get(lineage, {})
    change_dict[mdu_id] = [mdu_id, change_type, change_dt]
    info_dict[lineage] = change_dict

#print(info_dict)

# delete remove samples from snp_clusters.txt.2022-10-05, possible_clusters.json,possible_samples.json
# delete pair clusters and add the keep samples to UC
root_path = "/home/jianszhang/mdu_jobs/cleptr_db"
for lineage in info_dict.keys():
    print(lineage)
    change_dict = info_dict.get(lineage, {})
    change_del_list = []
    del_cluster_add_to_uc_list = []
    cluster_change_list = []
    for mid in change_dict.keys():
        m_id, type, change = change_dict.get(mid)
        if type == "DELETE":
            change_del_list.append(m_id)
        elif type == "CLUSTER":
            a, b = "", ""
            try:
                a, b = change.split(";")
            except:
                print(m_id, type, change)
                break
            if b == "UC":
                del_cluster_add_to_uc_list.append([m_id, a])
            else:
                cluster_change_list.append([m_id, a, b])
    lineage_path = lineage.replace(" ", "_")
    lineage_num = lineage.split(" ")[-1]
    lineage_folder = str(os.path.join(root_path, lineage_path))
    #write the del list to a file and use grep to del samples
    #cmd = f"cp {lineage_folder}/snp_clusters.txt.2022-10-05 {lineage_folder}/snp_clusters.txt.2022-10-05.backup"
    #bash_command(cmd)
    #grep_line = "\|".join(change_del_list)
    #cmd = f"grep -v '{grep_line}' {lineage_folder}/snp_clusters.txt.2022-10-05.backup"
    #print(grep_line)
    #print(cmd)
    #del it in possible_samples.json
    sample_db_path = os.path.join(root_path, lineage_path, "possible_samples.json")
    sample_db = load_json(sample_db_path)
    cluster_db_path = os.path.join(root_path, lineage_path, "possible_clusters.json")
    cluster_db = load_json(cluster_db_path)
    for s_id in change_del_list:
        k = sample_db.pop(s_id, "")

    #change_cluster to UC and del previus cluster
    for info in del_cluster_add_to_uc_list:
        m_id, old_cluster = info
        sample_dict = sample_db.get(m_id)
        #print(sample_dict)
        sample_dict["data_updated"] = "2023-07-23"
        sample_dict["current"] = "2023-07-23"
        sample_dict["clusters"]["2023-07-23"] = 'UC'

        k = cluster_db.pop(old_cluster, [])
        #remove sub json files
        cmd = f"rm -f {lineage_folder}/clst_{old_cluster}_*.json"
        bash_command(cmd)
        cmd = f"rm -f {lineage_folder}/tmp_{old_cluster}.txt"
        bash_command(cmd)

        UC_list = cluster_db.get("UC")
        UC_list.append(m_id)
        cluster_db["UC"] = UC_list

    #change cluster id:
    for info in cluster_change_list:
        m_id, old_cluster, new_cluster = info
        sample_dict = sample_db.get(m_id)
        #print(sample_dict)
        sample_dict["date_updated"] = "2023-07-23"
        sample_dict["current"] = "2023-07-23"
        sample_dict["clusters"]["2023-07-23"] = new_cluster

        k =  cluster_db.pop(old_cluster, [])
        C_list = cluster_db.get(new_cluster, [])
        C_list.append(m_id)
        cluster_db[new_cluster] = C_list

        cmd = f"mv {lineage_folder}/clst_{old_cluster}_clusters.json {lineage_folder}/clst_{new_cluster}_clusters.json"
        bash_command(cmd)
        cmd = f"mv {lineage_folder}/clst_{old_cluster}_samples.json {lineage_folder}/clst_{new_cluster}_samples.json"
        bash_command(cmd)
        cmd = f"mv {lineage_folder}/tmp_{old_cluster}.txt {lineage_folder}/tmp_{new_cluster}.txt"
        bash_command(cmd)

        #print(sample_db.get(m_id))
    #save all results
    save_db_to_json(sample_db, sample_db_path)
    save_db_to_json(cluster_db, cluster_db_path)

    #
