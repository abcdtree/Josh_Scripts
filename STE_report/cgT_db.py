import os
import sys
import subprocess
import json
import logging
import argparse
import getpass
import pandas as pd

URL = "http://172.30.48.230:703/nepss/enteritidis"
mdu_db = "/home/mdu/reads/qc.tab"
cgt_db = "/home/mdu/analysis/cgmlst/salmonella_enterica/db/mdu_samples.json"

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def check_output(cmd):
	output = subprocess.run(cmd.split(" "), capture_output=True, text=True)
	return output.stderr.strip()

def sync_database():
	server_name = os.uname()[1]
	if server_name == "garkbit.unimelb.edu.au":
		cmd = f"curl {URL} > ./salmo_nepss.json"
	else:
		cmd = f"ssh garkbit.unimelb.edu.au curl {URL} > ./salmo_nepss.json"
	bash_command(cmd)
	return

def read_db_from_json(mjson):
	with open(mjson, 'r') as f:
		db_dict = json.load(f)
	return db_dict

dict_cgt = read_db_from_json(cgt_db)

def get_cgt(mid):
	info_dict = dict_cgt.get(mid, {})
	mdate = info_dict.get("date_updated", "-")
	cgt = info_dict.get("clusters", {}).get(mdate, "-")
	return cgt

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-cgt","--cgt", metavar="cgMLST", nargs="+", type=str,\
		help="cgmlst list to search for list of isolates")
	parser.add_argument("--date", '-d', help="date cut off")
	args = parser.parse_args()
	#donwload nepss db
	sync_database()
	df_nepss = pd.read_json("salmo_nepss.json")[["mdu_nmr","collection_date"]]
	#print(df_nepss.head())
	df_nepss.columns = ["ISOLATE", "collection_date"]
	df_db = pd.read_csv(mdu_db, sep="\t")[["ISOLATE", "ST"]]
	df_nepss_st = df_nepss.merge(df_db, on="ISOLATE", how="left")

	df_nepss_st["cgT"] = df_nepss_st["ISOLATE"].apply(get_cgt)
	df_nepss_st.to_csv("cgT_db.csv", index=None)
	if args.cgt:
		for mcgt in args.cgt:
			df_sub = df_nepss_st[df_nepss_st.cgT == mcgt]
			df_sub.to_csv(f"cgT_{mcgt}_record.csv",index=None)

	if args.date:
		df_date = df_nepss_st[df_nepss_st["collection_date"] >= args.date]
		df_date.to_csv(f"cgT_{args.date}_record.csv", index=None)




if __name__ == "__main__":
	main()
