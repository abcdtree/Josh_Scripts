import os
import subprocess
import argparse
import sys

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("tab", help="input tab file to run bohra")
	args = parser.parse_args()

	if os.path.exists(args.tab):
		input_list = []
		with open(args.tab, "r") as mytab:
			for line in mytab:
				info = line.strip().split("\t")
				if len(info) > 2:
					mdu_id, r1, r2 = info
					current_folder = os.getcwd()
					contigs = os.path.join(current_folder,f"{mdu_id}/contigs.fa")
					input_list.append([mdu_id, r1, r2, contigs])
		with open("shigs.input.tab", 'w') as myout:
			for line in input_list:
				myout.write("\t".join(line) + "\n")

if __name__ == "__main__":
	main()
