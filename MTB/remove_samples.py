import os
import json


def load_json(mfile):
	json_file = open(mfile, 'r')
	db_dict = json.load(json_file)
	json_file.close()
	return db_dict

def save_db_to_json(db, path):
	with open(path, 'w') as json_file:
		json.dump(db, json_file, indent = 4)

myd = []
with open("remove.list", 'r') as mylist:
    for line in mylist:
        myd.append(line.strip())

load_dict = load_json("possible_samples.json")
for mid in myd:
    load_dict.pop(mid)
save_db_to_json(load_dict, "possible_samples.json.new")
