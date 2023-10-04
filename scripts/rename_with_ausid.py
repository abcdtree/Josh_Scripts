import csv
import argparse
import os
import sys


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("sample_sheet", help="sample sheet with at least 2 column: MDU ID,AUS MDU ID")
	parser.add_argument("--rename_path", "-p", default="./", help="path to find the reads files")
	args = parser.parse_args()

	if os.path.exists(args.sample_sheet):
		with open(args.sample_sheet, 'r') as mysample:
			csvreader = csv.reader(mysample)
			MDU_ID_p = 0
			AUS_MDU_ID_p = 1
			count = 0
			for line in csvreader:
				if count == 0:
					MDU_ID_p = line.index("MDU ID")
					AUS_MDU_ID_p = line.index("AUS MDU ID")
					count = 1
				else:
					MDU_ID = line[MDU_ID_p]
					AUS_MDU_ID = line[AUS_MDU_ID_p]
					reads_path = os.path.join(args.rename_path, MDU_ID)
					for mfile in os.listdir(reads_path):
						new_filename = mfile.replace(MDU_ID, AUS_MDU_ID)
						if os.path.exists(os.path.join(reads_path, mfile)):
							os.rename(os.path.join(reads_path, mfile), os.path.join(reads_path, new_filename))
					os.rename(reads_path, os.path.join(args.rename_path, AUS_MDU_ID))
	else:
		sys.exit()
		print(f"Could not find {args.sample_sheet}")

if __name__ == "__main__":
	main()
