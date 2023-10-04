import os
import subprocess
import argparse
import datetime
import csv
import pathlib

def getYear():
	today = datetime.date.today()
	return today.year

def get_ont_home_folder():
	year = getYear()
	mpath = f"/home/mdu/instruments/nanopore/{year}"
	cmd = f"mkdir -p {mpath}"
	bash_command(cmd)
	return mpath

def check_output(cmd):
	output = subprocess.run(cmd.split(" "), capture_output=True, text=True)
	return output.stdout.strip()

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def ont_rsync(run_id):
	home_path = get_ont_home_folder()
	cmd = f'sshpass -p "grid" rsync -rav grid@gridion.mdu:/data/{run_id}/* {home_path}/{run_id}/'
	bash_command(cmd)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("run_id",  help="run id you would like rsync to local machine")
	parser.add_argument("--sample_sheet", '-s', help="Create reads based on the sample sheet")
	args = parser.parse_args()

	ont_rsync(args.run_id)
	ont_home = get_ont_home_folder()
	mdu_reads = os.environ.get('MDU_READS')
	target = f"{mdu_reads}/{args.run_id}"
	if args.sample_sheet:
		if os.path.exists(args.sample_sheet):
			nanopore_dir = pathlib.Path(ont_home, args.run_id)
			with open(args.sample_sheet, 'r') as mysamplesheet:
				csvreader = csv.reader(mysamplesheet)
				count = 0
				header = []
				for line in csvreader:
					if count == 0:
						header = line
						count+=1
						continue
					mduid = line[1]
					barcode = line[3]
					barcode_number = barcode[-2:]
					barcode_folder = f"barcode{barcode_number}"
					cmd = f"mkdir -p {target}"
					bash_command(cmd)
					cmd = f"mkdir -p {target}/{mduid}"
					bash_command(cmd)
					barcode_fastqpass = sorted(nanopore_dir.rglob(f'fastq_pass/{barcode_folder}'))[0]
					#print(barcode_fastqpass)
					cmd = f"gzip -c -d -f {barcode_fastqpass}/*.fastq* > {target}/{mduid}/{mduid}.fastq"
					print(cmd)
					bash_command(cmd)

if __name__ == "__main__":
	main()
