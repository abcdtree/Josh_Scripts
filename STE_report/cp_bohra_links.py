import os
import subprocess
import argparse
import csv
import sys
from multiprocessing import Pool
import pandas as pd

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def check_output(cmd):
	output = subprocess.run(cmd.split(" "), capture_output=True, text=True)
	return output.stdout.strip()

def copy_bohra_links(cgt):
    cmd = f"mkdir -p /home/jianszhang/public_html/MDU/STE"
    bash_command(cmd)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("cgt_summary_csv", help="cgt summary tab created on summary step")
	args = parser.parse_args()

    with open(args.cgt_summary_csv, 'r') as mycsv:
		csvreader = csv.reader(mycsv)
		count = 0
		for line in csvreader:
			if count == 0:
				count = 1
				continue
			cgt = line[0]
			cgt_list.append(cgt)
