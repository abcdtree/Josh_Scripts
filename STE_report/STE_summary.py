import os
import pandas as pd
import subprocess
import argparse
import csv

cmd_home = "/home/jianszhang/github/atom/STE_report"
def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def create_summary(cgt_csv):
	df = pd.read_csv(cgt_csv)[["ISOLATE", "cgT"]]
	df_cgt_sum = df.groupby("cgT").count().reset_index()
	df_cgt_sum.columns = ["cgT", "Count"]
	return df_cgt_sum
	#df_cgt_sum.to_csv("cgT_count.csv")

#create_summary("cgT_2023-01-08_record.csv")

def export_date_cgt_csv(date_cut):
	cmd = f"python3 {cmd_home}/cgT_db.py -d {date_cut}"
	bash_command(cmd)
	if os.path.exists(f"cgT_{date_cut}_record.csv"):
		print(f"**Export cgt data with date cut off as {date_cut}**")
		return f"cgT_{date_cut}_record.csv"
	else:
		print("**Error! csv file was not found**")
		return f"Error"

def create_cgT_lists(cgt_sum):
	summary_list= []
	for index, x in cgt_sum.iterrows():
		cgt = x["cgT"]
		count = x["Count"]
		cmd = f"python3 {cmd_home}/cgT_db.py --cgt {cgt}"
		bash_command(cmd)
		if os.path.exists(f"cgT_{cgt}_record.csv"):
			df_cgt = pd.read_csv(f"cgT_{cgt}_record.csv")
			now_cut = pd.to_datetime('now')
			six_month = (now_cut - pd.DateOffset(months=6)).strftime("%Y-%m-%d")
			df_cgt_six_month = df_cgt[df_cgt.collection_date >= six_month]
			df_cgt_six_month.to_csv(f"cgT_{cgt}_sixmonth_record.csv")
			six_month_count = int(df_cgt_six_month.ISOLATE.count())
			summary_list.append([cgt, count, six_month_count])
			#create cgt_{cgt}.tab for bohra run
			cmd = f"mkdir -p cgt{cgt}"
			bash_command(cmd)
			isolate_list = df_cgt.ISOLATE.tolist()
			with open(f"cgt{cgt}/cgt_{cgt}.txt", 'w') as myout:
				myout.write("\n".join(isolate_list))
			cmd = f"mdu reads --idfile cgt{cgt}/cgt_{cgt}.txt > cgt{cgt}/cgt_{cgt}.tab"
			bash_command(cmd)
	return summary_list

def main():
	parser = argparse.ArgumentParser()
	#parser.add_argument("-cgt","--cgt", metavar="cgMLST", nargs="+", type=str,\
		#help="cgmlst list to search for list of isolates")
	parser.add_argument("date", help="date cut off")
	args = parser.parse_args()

	cgt_csv = export_date_cgt_csv(args.date)
	if cgt_csv != "Error":
		cgt_sum = create_summary(cgt_csv)
		summary_list = create_cgT_lists(cgt_sum)
		title = ["cgT",f"Added since {args.date}", "Total in cgT (6 months)"]
		with open(f"cgT_summary_{args.date}.csv","w", newline="") as myout:
			csvwriter = csv.writer(myout)
			csvwriter.writerow(title)
			for line in summary_list:
				csvwriter.writerow(line)
	else:
		return 0

if __name__ == "__main__":
	main()
