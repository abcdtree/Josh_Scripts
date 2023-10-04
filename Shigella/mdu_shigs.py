import os
import subprocess
import argparse
import sys

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

def check_conda_envs():
	try:
		my_env = os.environ["CONDA_PREFIX"]
		if "shigs" in my_env:
			return True
		else:
			print("Please activea shigs env: ca /home/khhor/conda/envs/shigs")
			return False
	except:
		print("Please activea shigs env: ca /home/khhor/conda/envs/shigs")
		return False

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--mdu_ids", '-mdu_ids', help="run on a single/mutiple sample from MDU, you only need to provide file contains mdu ids")
	parser.add_argument("--tab", "-tab", help="run with a tab file as input, where tab file has 4 columns `prefix  read1   read2   contigs`")
	parser.add_argument("--cpu", "-cpu", help="number of cores to parallel the analysis", default=10)
	#parser.add_argument("--samplesheet", '-s', help="sample sheet with at least two columns MDU_ID, Barcode")
	args = parser.parse_args()

	if not check_conda_envs():
		sys.exit(0)
	else:
		if args.mdu_ids:
			if os.path.exists(args.mdu_ids):
				mdu_ids = []
				with open(args.mdu_ids,'r') as myids:
					for line in myids:
						mdu_id = line.strip()
						if len(mdu_id) > 0:
							mdu_ids.append(mdu_id)
				with open("tmp.tab", "w") as mytmp:
					for mdu_id in mdu_ids:
						reads_lines = check_output(f"mdu reads -s {mdu_id}").split()
						contig_lines = check_output(f"mdu contigs -s {mdu_id}").split()
						if len(reads_lines) > 2 and len(contig_lines) > 1:
							mytmp.write(f"{mdu_id}\t{reads_lines[1]}\t{reads_lines[2]}\t{contig_lines[1]}\n")
						else:
							print(f"No record in mdu db for {mdu_id}")
							continue
				command = "parallel -j "+ str(args.cpu) + " --colsep '\\t' shigs -p {1} -r1 {2} -r2 {3} -c {4} :::: tmp.tab"
				print(command)
				bash_command(command)

			else:
				print(f"Error, could not find the input file {args.mdu_ids}")
				sys.exit(0)
		elif args.tab:
			if os.path.exists(args.tab):
				command = "parallel -j "+ str(args.cpu) + " --colsep '\\t' shigs -p {1} -r1 {2} -r2 {3} -c {4} :::: " + args.tab
				print(command)
				bash_command(command)
			else:
				print(f"Error, could not find the input file {args.tab}")
				sys.exit(0)
	lines = []
	for folder in os.listdir("./"):
		if os.path.exists(os.path.join("./", folder, "shigs.csv")):
			with open(os.path.join("./", folder, "shigs.csv"), 'r') as myinput:
				count = 0
				for line in myinput:
					if count == 0:
						if len(lines) == 0:
							lines.append(line)
						count +=1
					else:
						lines.append(line)
	with open("shigs_summary.csv", 'w') as myout:
		for line in lines:
			myout.write(line)

if __name__ == "__main__":
	main()
