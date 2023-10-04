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
		if "sonnei" in my_env:
			return True
		else:
			print("Please activea shigs env: ca /home/jianszhang/conda/envs/sonneityping")
			return False
	except:
		print("Please activea shigs env: ca /home/jianszhang/conda/envs/sonneityping")
		return False

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("shigs", help="shigs summary file in the shigs run folder, please run the command in the shigs analysis folder")
	args = parser.parse_args()

	if not check_conda_envs():
		sys.exit()
	else:
		command = f"mkdir -p json"
		bash_command(command)
		if os.path.exists(args.shigs):
			with open(args.shigs, 'r') as myshigs:
				count = 0
				#mdu_ids = []
				for line in myshigs:
					if count == 0:
						count += 1
						continue
					mdu_id = line.split(",")[0]
					if len(mdu_id) > 0:
						if os.path.exists(f"./{mdu_id}/mykrobe.json"):
							command = f"cp ./{mdu_id}/mykrobe.json ./json/{mdu_id}.json"
							bash_command(command)
			command = f"python3 /home/jianszhang/github/sonneityping/parse_mykrobe_predict.py --jsons json/*.json --alleles /home/jianszhang/github/sonneityping/alleles.txt --prefix sonneityping_result"
			bash_command(command)

if __name__ == "__main__":
	main()
