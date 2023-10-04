import csv
import json
import pandas as pd

def load_json(path):
	json_file = open(path, 'r')
	db_dict = json.load(json_file)
	json_file.close()
	return db_dict

df_tbtamr = pd.read_csv("tbtamr.csv")

myids = df_tbtamr['Seq_ID'].tolist()
sub_dict = {}
for mid in myids:
    my_json_path = f"./{mid}/tb-profiler_report.json"
    db_dict = load_json(my_json_path)
    sublin = db_dict[mid]["sublin"]
    sub_dict[mid] = sublin

print(sub_dict)
df_tbtamr["Sub Lineage"] = df_tbtamr["Seq_ID"].apply(lambda x: sub_dict[x])

columns = list(df_tbtamr.columns)
new_columns = columns[0:3] + [columns[-1]] + columns[3:-1]
df_tbtamr = df_tbtamr[new_columns]
df_tbtamr.to_csv("tbtamr_with_sublin.csv", index=None)
