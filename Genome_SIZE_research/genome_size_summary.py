import json
import csv


def load_json(mfile):
	json_file = open(mfile, 'r')
	db_dict = json.load(json_file)
	json_file.close()
	return db_dict


info_json = load_json("AQUAMIS_thresholds.json")
#print(info_json["thresholds"].keys())
output_list = [["species", "1", "2", "3", "4"]]


for species in info_json["thresholds"]:
    th_dict = info_json["thresholds"].get(species, {})
    len_dict = th_dict.get("Total length", [{}])[0]
    len_list = [0,0,0,0]
    if len_dict != None:
        len_list = len_dict.get("interval", [0,0,0,0])
    output_list.append([species] + len_list)

with open("AQUAMIS_threshold.csv", 'w', newline="") as myout:
    spamwriter = csv.writer(myout)
    for row in output_list:
        spamwriter.writerow(row)
