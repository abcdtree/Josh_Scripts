import os, subprocess, csv
import argparse
import datetime
import pathlib

def get_year():
	return datetime.datetime.now().year

def get_analysis_home():
	return "/home/mdu/analysis/sars_nanopore_qc/Research"

def get_ont_home():
	nanopare_home = "/home/mdu/instruments/nanopore/"
	myear = get_year()
	return str(os.path.join(nanopare_home, str(myear)))

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

def merge_fastq(runid, mode, mdu_id_barcode_dict):
	#create work folder
	ont_home = get_ont_home()
	if not os.path.exists(os.path.join(ont_home, runid)):
		print(f"could not find data folder for {runid} in {ont_home}, please rsync the data or use the right runid")
		return
	#work_folder = get_analysis_home()
	#cmd = f"mkdir -p {work_folder}/{runid}"
	#bash_command(cmd)
	mdu_reads = os.environ.get('MDU_READS')
	if mode == "single":
		mdu_id = list(mdu_id_barcode_dict.keys())[0]
		nanopore_dir = pathlib.Path(f'{ont_home}', f'{runid}')
		pass_fastq = sorted(nanopore_dir.rglob('fastq_pass'))
		#print(pass_fastq[0])
		target = f"{mdu_reads}/{runid}"
		cmd = f"mkdir -p {target} && gzip -c -d -f {pass_fastq[0]}/*.fastq* > {target}/{mdu_id}.fastq"
		#bash_command(cmd)
		print(f"Running {cmd}")
		bash_command(cmd)
		return
	else:
		print("Please run regular seqgen command to handle")
		return

def merge_and_copy(runid, samplesheet):
	with open(samplesheet, 'r') as msh:
		csvreader = csv.reader(msh)
		count = 0
		title = []
		mdata = []
		for line in csvreader:
			if count == 0:
				title = line
				count += 1
				continue
			if len(line) > 2:
				mdata.append(line)
		if "MDU ID" not in title and "MDU_ID" not in title:
			print("Please check your samplesheet, a MDU ID/MDU_ID column is requested in the sample sheet")
			return
		if "Barcode" not in title:
			print("Please check your samplesheet, a Barcode column is requested in the sample sheet")
			return

		mdu_id_index = 0
		barcode_index = title.index("Barcode")
		mdu_id_barcode_dict = {}
		mode = ""
		#no barcode --- only one sample in a run
		if len(mdata) == 1:
			mode = "single"
			mdu_id_barcode_dict[mdata[0][0]] = mdata[0][0]
		else:
			mode = "multiple"
			for data_line in mdata:
				if runid not in data_line:
					print("Please check your runid, it does not match with the sample sheet")
					return
				mdu_id = data_line[mdu_id_index]
				barcode = data_line[barcode_index]
				mdu_id_barcode_dict[barcode] = mdu_id
		merge_fastq(runid, mode, mdu_id_barcode_dict)
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--runid", '-r', help="ONT sequence run Id")
	parser.add_argument("--samplesheet", '-s', help="sample sheet with at least two columns MDU_ID, Barcode")
	args = parser.parse_args()

	if args.runid:
		if args.samplesheet:
			if os.path.exists(args.samplesheet):
				merge_and_copy(args.runid, args.samplesheet)
				return
			else:
				print(f"Could not find file {args.samplesheet}, please check your input")
				return
		else:
			print("please input the samplesheet with -s option")
			return
	else:
		print("please input the runid with -r option")
		return

if __name__ == "__main__":
	main()
