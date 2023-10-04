import os
import subprocess
from multiprocessing import Pool
import argparse
import sys


def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def run_kraken2_gtdb(x):
	r1, r2, mdu_id = x
	cmd = f"kraken2 --db /tmp/gtdb_r207 --paired {r1} {r2} --report {mdu_id}_gtdb.tab --output - --memory-mapping"
	#print(cmd)
	print(f"running kraken2 gtdb on {mdu_id}")
	bash_command(cmd)
	return f"{mdu_id}_gtdb.tab"

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("tabfile", help="tab file to reads to run kraken2")
	#parser.add_argument("--db", default="/tmp/gtdb_r207", help="kraken2 db to use")
	args = parser.parse_args()
	if os.path.exists(args.tabfile):
		x_input = []
		with open(args.tabfile, 'r') as myfile:
			for line in myfile:
				if len(line.strip()) > 0:
					try:
						mdu_id, r1, r2 = line.strip().split("\t")
					except:
						continue
					x_input.append([r1, r2, mdu_id])
		my_result_list = []
		with Pool(20) as p:
			my_result_list = p.map(run_kraken2_gtdb, x_input)
		print(my_result_list)
	else:
		print(f"could not find the {args.tabfile}")

if __name__ == "__main__":
	main()
