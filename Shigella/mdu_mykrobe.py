import os
import subprocess
import argparse
import sys
from multiprocessing import Pool

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
		if "sonnei" in my_env:
			return True
		else:
			print("Please activea shigs env: ca /home/jianszhang/conda/envs/sonneityping")
			return False
	except:
		print("Please activea shigs env: ca /home/jianszhang/conda/envs/sonneityping")
		return False

def run_mykrobe(info):
	mdu_id, r1, r2 = info
	command = f"mykrobe predict --sample {mdu_id} --species sonnei --format json --out {mdu_id}.json --seq {r1} {r2}"
	bash_command(command)
	return True


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("tab", help="mdu reads style tab file")
	#parser.add_argument("--cpu", "-cpu", help="number of cores to run parellel", default=10)
	args = parser.parse_args()

	if not check_conda_envs():
		sys.exit()
	else:
		minfo = []
		if os.path.exists(args.tab):
			with open(args.tab, 'r') as myfile:
				for line in myfile:
					info = line.strip().split("\t")
					if len(info) == 3:
						minfo.append(info)
			with Pool(1) as p:
				result = p.map(run_mykrobe, minfo)
		command = "mkdir -p json"
		bash_command(command)
		command = "mv *.json json/"
		bash_command(command)
		command = f"python3 /home/jianszhang/github/sonneityping/parse_mykrobe_predict.py --jsons json/*.json --alleles /home/jianszhang/github/sonneityping/alleles.txt --prefix sonneityping_result"
		bash_command(command)

if __name__ == "__main__":
	main()
