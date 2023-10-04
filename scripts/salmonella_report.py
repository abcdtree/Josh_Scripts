import os
import sys
import subprocess
import json
import logging
import argparse
import getpass
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import pandas as pd

URL = "http://172.30.48.230:703/nepss/enteritidis"
PREVIOUS_CSV_PATH = "./ARCHIVE"
COPY_ARCHIVE = "/home/jianszhang/projects/salmonella_report/ARCHIVE"
REF_LOC = "/home/jianszhang/database/refs/Salmonella/ref.fa"
MASK_LOC = "/home/jianszhang/database/refs/Salmonell/mask_sites.bed"

def create_logger(logging, tool_name, level):
	"""
	A function to create a logger.
	"""
	logger = logging.getLogger(tool_name)

	# Create handlers
	handler = logging.StreamHandler()
	handler.setLevel(level)

	# Create formatters and add it to handlers
	logformat = logging.Formatter(
		'[%(name)s - %(asctime)s] %(levelname)s: %(message)s')
	handler.setFormatter(logformat)

	# Add handlers to the logger
	logger.addHandler(handler)
	logger.setLevel(level)

	return logger

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

def get_current_date():
	date_1 = str(datetime.date(datetime.now()))
	date_2 = date_1.replace("-", "")
	return date_1, date_2

def sync_database(date_str, logger):
	if os.path.exists(f"./nepss/salmo_nepss_{date_str}.json"):
		logger.info("Database has already been downloaded to local")
		return
	logger.info("Downloading Salmonella database to local")
	server_name = os.uname()[1]
	if server_name == "garkbit.unimelb.edu.au":
		cmd = f"curl {URL} > ./nepss/salmo_nepss_{date_str}.json"
	else:
		cmd = f"ssh garkbit.unimelb.edu.au curl {URL} > ./nepss/salmo_nepss_{date_str}.json"
	if not os.path.exists("./nepss"):
		os.mkdir("./nepss")
	bash_command(cmd)
	return

def trans_json_to_csv(date_str, logger):
	if os.path.exists(f"./nepss/salmo_nepss_{date_str}.json"):
		df = pd.read_json(f"./nepss/salmo_nepss_{date_str}.json")
		df.to_csv(f"./nepss/salmo_nepss_{date_str}.csv", index=None)
	else:
		logger.error("Could not open the database json file")
	return

def find_the_most_recent_archive_csv(date_str, logger):
	now_date_time = datetime.strptime(date_str, "%Y%m%d")
	recent_date_time = None
	recent_file = None
	if not os.path.exists(PREVIOUS_CSV_PATH):
		cmd = f"cp -r {COPY_ARCHIVE} ."
		bash_command(cmd)
	for file in os.listdir(PREVIOUS_CSV_PATH):
		if file[-3:] == "csv":
			file_date = file.split(".")[0].split("_")[-1]
			file_date_time = datetime.strptime(file_date, "%Y%m%d")
			if recent_date_time == None:
				if file_date_time < now_date_time:
					recent_date_time = file_date_time
					recent_file = file
			else:
				if file_date_time > recent_date_time and file_date_time < now_date_time:
					recent_date_time = file_date_time
					recent_file = file
	return os.path.join(PREVIOUS_CSV_PATH, file)

def window_cut(number_of_months, date_str, logger):
	df_window = None
	if number_of_months == 0:
		df = pd.read_csv(f"./nepss/salmo_nepss_{date_str}.csv")
		df_window = df.copy()
		#df_window.drop_duplicates(subset="mdu_nmr", keep='first', inplace=True)
	else:
		date = datetime.strptime(date_str, "%Y%m%d")
		my_months = -1 * number_of_months
		previous_date = date + relativedelta(months=my_months)
		previous_date = str(datetime.date(previous_date))
		#print(previous_date)
		df = pd.read_csv(f"./nepss/salmo_nepss_{date_str}.csv")
		#print(df["id"].count())
		mask = df["received_date"] > previous_date
		df_window = df[mask].copy()
	df_window.drop_duplicates(subset="mdu_nmr", keep='first', inplace=True)
	number_of_window_record = df_window["id"].count()
	logger.info(f"Total {number_of_window_record} isolates are in the window")
	return df_window

def new_record(df_window, previous_file, logger):
	df_previous = pd.read_csv(previous_file)
	previous_id_list = df_previous["mdu_nmr"].tolist()
	mask = ~df_window["ISOLATE"].isin(previous_id_list)
	df_window_new = df_window[mask]
	number_of_new_record = df_window_new["ISOLATE"].count()
	logger.info(f"Total {number_of_new_record} new isolates are included in this report")
	return df_window_new

def id_tab_prepare(df_window, logger):
	command = f"mdu reads --noqc -s "
	my_ids = df_window["ISOLATE"].tolist()
	command += " ".join(my_ids)
	command += " > input.tab"
	bash_command(command)
	return

def run_bohra(bohra_type, bohra_cpu, bohra_noqc, logger):
	path_env = os.environ['PATH']
	os.environ['PATH'] = "/home/khhor/miniconda3/envs/bohra2/bin/:" + path_env
	check_snippy_version = "snippy -v"
	snippy_version = check_output(check_snippy_version)
	print(snippy_version)
	if snippy_version != "snippy 4.4.5":
		logger.error("Wrong Snippy version, please check the PATH env")
		sys.exit()
	cp_ref = f"cp {REF_LOC} ./"
	bash_command(cp_ref)
	cmd = "bohra run -mdu "
	cmd += f"-r {REF_LOC} "
	#cmd += f"-m {MASK_LOC} "
	if bohra_noqc:
		cmd += "-mc 0 -ma 0 "
	cmd += f"-i input.tab --pipeline {bohra_type} -j Salmonella_RUN -c {bohra_cpu}"
	logger.info(cmd)
	bash_command(cmd)
	#print(cmd)
	return

def email_report(my_email, my_jobid, date_str, logger):
	if os.path.exists(f"./Salmonella_RUN/report"):
		cmd = f"rsync -a ./Salmonella_RUN/report/ ./Salmonella_RUN/report_{date_str}"
		bash_command(cmd)
	else:
		logger.error(f"Please check the Bohra log, No output found")
		sys.exit()
	cmd = f"mkdir -p ~/public_html/MDU"
	bash_command(cmd)
	cmd = f"mkdir -p ~/public_html/MDU/Salmonella"
	bash_command(cmd)
	cmd = f"mkdir -p ~/public_html/MDU/Salmonella/{my_jobid}_{date_str}"
	bash_command(cmd)
	cmd = f"cp ./Salmonella_RUN/report_{date_str}/index.html ~/public_html/MDU/Salmonella/{my_jobid}_{date_str}/index.html"
	bash_command(cmd)
	#send email
	username = ""
	try:
		username = getpass.getuser()
	except:
		username = "jianszhang"
	public_link = f"https://bioinformatics.mdu.unimelb.edu.au/~{username}/MDU/Salmonella/{my_jobid}_{date_str}"
	message = """\
	JOBID: %s
	PUBLIC LINKS:
	%s
	""" % (my_jobid+"_"+date_str, public_link)
	if my_email:
		message_cmd = f"echo '{message}' | mailx -s 'Salmonella Analysis {my_jobid} {date_str}' {my_email}"
		bash_command(message_cmd)
	return

def archive_csv(date_str, logger):
	cmd = f"cp ./nepss/salmo_nepss_{date_str}.csv ./ARCHIVE/"
	bash_command(cmd)
	logger.info("current salmonella database was saved in ARCHIVE")
	return

def st_id_tab_prepare(st, logger):
	if os.path.exists("./input.tab"):
		os.remove("./input.tab")
	for my_st in st:
		cmd = f"mdu search -st {my_st} -sp Salmonella | cut -f1 | tail -n +2 | sort > temp.list"
		bash_command(cmd)
		#print(cmd)
		mdu_cmd = f"mdu reads --idfile temp.list --noqc >> input.tab"
		#print(mdu_cmd)
		bash_command(mdu_cmd)
	return

def upload_the_report():
	pass

def check_st(df_window, date_str, logger):
	qc_database = ""
	if os.path.exists("/home/mdu/reads/qc.tab"):
		qc_database = "/home/mdu/reads/qc.tab"
	else:
		qc_database = "/home/mdu/reads/qc.tab.backup"
	qc_df = pd.read_csv(qc_database, sep="\t")[["ISOLATE", "ST"]]
	window_id = df_window["mdu_nmr"].tolist()
	qc_df = qc_df[qc_df["ISOLATE"].isin(window_id)]
	qc_st_df = qc_df.groupby("ST").size().reset_index(name="counts")
	qc_st_df = qc_st_df[qc_st_df["counts"] > 5]
	st_list = qc_st_df["ST"].tolist()
	qc_df_in = qc_df[qc_df["ST"].isin(st_list)]
	qc_df_out = qc_df[~qc_df["ST"].isin(st_list)]
	qc_df_in.to_csv(f"isolates_included_{date_str}.csv", index=None)
	qc_df_out.to_csv(f"isolates_not_included_{date_str}.csv", index=None)
	include_number = qc_df_in["ISOLATE"].count()
	exclude_number = qc_df_out["ISOLATE"].count()
	logger.info(f"Total {include_number} isolates are included in this report, skip {exclude_number} isolates")
	#print(qc_df_in)
	#print("####")
	#print(qc_df_out)
	return qc_df_in

def main():
	parser = argparse.ArgumentParser()
	#parser.add_argument("--st", metavar="ST", nargs="+", type=str, \
	#					help="A list of STs would like to Analysis")
	parser.add_argument("--bohra", "-b", help="Model of Bohra Pipeline: preview, all, sa",\
						default="sa")
	parser.add_argument("--reportid", help="Report ID to create publich html folder", default="Salmonella_Report")
	parser.add_argument("--email", "-e", help="Enable Email Notification while job is done")
	parser.add_argument("--cpu", "-c", help="Number of cpus to use (default as 16)", \
						default="16")
	parser.add_argument("--noqc", help="disable the qc filter of Bohra and run with all samples", \
						action='store_true')
	parser.add_argument("--window", '-w', type=int, help="time window for reporting (default as 6 months)", \
						default=12)
	parser.add_argument("--skiplist", help="a txt file listing all isolates mdu-id which should be skipped in this run")
	parser.add_argument("-t", "--test", help="just a test")
	args = parser.parse_args()
	logger = create_logger(logging, "salmonella-report", logging.INFO)
	#STEP 1 Prepare input
	logger.info("Welcome to Salmonella-Report")
	logger.info("Sync database from Server")
	date_type_1, date_str = get_current_date()
	#if args.st:
		#st_id_tab_prepare(args.st, logger)
	sync_database(date_str, logger)
	trans_json_to_csv(date_str, logger)
	previous_file = find_the_most_recent_archive_csv(date_str, logger)
		#print(previous_file)
	df_window = window_cut(args.window, date_str, logger)
	if args.skiplist:
		skiplist = get_skiplist(args.skiplist, logger)
		mask = ~df_window['mdu_nmr'].isin(skiplist)
		df_window = df_window[mask].copy()
	df_window_st = check_st(df_window, date_str, logger)
	df_window_new = new_record(df_window_st, previous_file, logger)
	id_tab_prepare(df_window_st, logger)
	run_bohra(args.bohra, args.cpu, args.noqc, logger)
	email_report(args.email, args.reportid, date_str, logger)
	archive_csv(date_str, logger)
	logger.info("Salmonella report pipeline finished successfully")


if __name__ == "__main__":
	main()
