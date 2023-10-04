import csv
import os
import argparse
import sys

archive_folder = "/home/jianszhang/analysis/shigella/archive"

history_file = "Sonnei_meta.csv"

#bohra path /home/jianszhang/analysis/shigella/bohra/20230216/sonnei
#shigs path /home/jianszhang/analysis/shigella/shigs/20230217/sonnei/shigs_summary.csv

def guess_location(mid):
	if mid[0] == "M":
		return "QLD"
	elif mid[0] == "S":
		return "OVERSEAS"
	elif "-" in mid:
		info = mid.split("-")
		if len(info[0]) == 2:
			return "NSW"
		elif len(info[0]) == 4:
			return "VIC"
		else:
			return "UNKNOWN"
	elif len(mid) == 10:
		if mid[0] == "2":
			return "SA"
		else:
			return "WA"
	else:
		return "UNKNOWN"

def get_pos_list(title):
	mylist = ["ESBL", "Macrolide","Sulfonamide", "Quinolone", "Trimethoprim"]
	return_p = []
	for m in mylist:
		index = title.index(m)
		return_p.append(index)
	return return_p

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("shigs_summary", help="input shigs_summary_file")
	parser.add_argument("bohra_run_folder", help="path to the bohra_run_folder")
	args = parser.parse_args()

	#check the bohra related files: mlst.txt, resistome.txt
	mlst_dict = {}
	if os.path.exists(os.path.join(args.bohra_run_folder, "report", "mlst.txt")):
		with open(os.path.join(args.bohra_run_folder, "report", "mlst.txt"), 'r') as mymlst:
			count = 0
			for line in mymlst:
				if count == 0:
					count +=1
					continue
				info = line.strip().split("\t")
				if len(info) > 0:
					mlst_dict[info[0]] = info[2]
	else:
		print("Please check whether mlst.txt is in bohra run folder")
		sys.exit(1)
	resistome_dict = {}
	if os.path.exists(os.path.join(args.bohra_run_folder, "report", "resistome.txt")):
		with open(os.path.join(args.bohra_run_folder, "report", "resistome.txt"), 'r') as myresist:
			csvreader = csv.reader(myresist, delimiter='\t')
			count = 0
			title = []
			pos_list = []
			#list of resistance to check ["ESBL", "Marcolide","Sulfonamide", "Quinolone", "Trimethoprim"]
			#[4, -3, -4, -2, 5]
			for info in csvreader:
				if count ==0:
					title = info
					pos_list = get_pos_list(title)
					count +=1
					continue
				#info = line.strip().split("\t")
				if len(info) > 0:
					'''Quinolone = ""
					try:
						Quinolone = info[10]
					except:
						Quinolone = ""'''
					resistome_dict[info[0]] = [info[pos_list[0]], info[pos_list[1]], info[pos_list[2]], info[pos_list[3]], info[pos_list[4]]]
	else:
		print("Please check whether resistome.txt is in bohra run folder")
		sys.exit(1)

	if os.path.exists(args.shigs_summary):
		shigs_dict = {}
		with open(args.shigs_summary, 'r') as myshigs:
			csvreader = csv.reader(myshigs)
			count = 0
			for row in csvreader:
				if count == 0:
					count = 1
					continue
				shigs_dict[row[0]] = [row[-2], row[-1]]

	#save to file
	with open("Sonnei_meta_new.csv", 'w',newline = "") as myout:
		spamwriter = csv.writer(myout)
		spamwriter.writerow(["Isolate", "LOCATION", "MLST", "ESBL","Macrolide", "Sulfonamide", "Quinolone", "Trimethoprim",\
		"sonneitype", "name"])
		for key in shigs_dict:
			row = [key, guess_location(key), mlst_dict.get(key,"")] + resistome_dict.get(key, ["","", "","",""]) + \
			shigs_dict.get(key)
			spamwriter.writerow(row)

if __name__ == "__main__":
	main()
