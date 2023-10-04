import os
import json
import csv

def reads_db_path():
	reads_path = os.environ.get("READS_DB", "/home/mdu/reads/reads.json")
	if not os.path.exists(reads_path):
		backup_path = "/home/mdu/reads/reads.json.backup"
		copy_backup(backup_path, "reads")
		reads_path = "/home/mdu/reads/reads.json"
	return reads_path

def load_reads_json():
	reads_json = reads_db_path()
	back_up = "/home/mdu/reads/reads.json.backup"
	json_file = open(reads_json, 'r')
	if not json_file.readable():
		json_file.close()
		json_file = open(back_up, 'r')
	db_dict = json.load(json_file)
	json_file.close()
	return db_dict

def no_item_code(mid):
	info = mid.split("-")
	if len(info) > 2 and len(info) < 5:
		return "-".join(info[:2])
	else:
		return mid

def mdu_fuzzy_match(idA, idB):
	idA_chopped = no_item_code(idA)
	idB_chopped = no_item_code(idB)
	return idA_chopped == idB_chopped

def noitemcode_search(reads_db, mid):
	output_dict = {}
	for key in reads_db:
		if mdu_fuzzy_match(key, mid):
			output_dict[key] = reads_db[key][0]
	return output_dict

db_dict = load_reads_json()
check_run = "M2023-00028"
for key in db_dict:
	result = db_dict.get(key,[{}])[0]
	run_id = result.get("RUN_ID")
	if run_id == check_run:
		print(result)


'''
out_check_result = []
with open("ids.txt", 'r') as mychecklist:
    for line in mychecklist:
        mdu_id = line.strip()
        if len(mdu_id) > 0:
            info = noitemcode_search(db_dict, mdu_id)
            if len(info) == 0:
                out_check_result.append([mdu_id, "False", "N/A"])
            elif len(info) > 1:
                mdu_id_list = ";".join(sorted(list(info.keys())))
                out_check_result.append([mdu_id, "True", mdu_id_list])
            else:
                out_check_result.append([mdu_id, "True", "N/A"])
with open("check_result.csv", 'w') as myout:
    spamwriter = csv.writer(myout)
    title = ["MDU_ID", "Available", "Item Code Choice"]
    spamwriter.writerow(title)
    for line in out_check_result:
        spamwriter.writerow(line)
'''
