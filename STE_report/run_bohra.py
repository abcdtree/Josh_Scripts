import os
import subprocess
import argparse
import csv
import sys
from datetime import date

today = date.today()
c_date = today.strftime("%Y%m%d")

cwd = os.getcwd()
db_folder = "/home/jianszhang/database/refs/Salmonella"
ref_path = os.path.join(db_folder, "ref.fa")
mask_path = os.path.join(db_folder, "mask_sites.bed")


def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def change_to_cgT_folder(cgt):
	mpath = os.path.join(cwd, f"cgt{cgt}")
	os.chdir(mpath)
	cmd = f"cp -f {ref_path} ."
	bash_command(cmd)
	cmd = f"cp -f {mask_path} ."
	bash_command(cmd)
	cmd = f"bohra run -p snps -i cgt_{cgt}.tab -r ref.fa -m mask_sites.bed --cpu 100 --proceed"
	print(os.getcwd() + ":")
	print("running", cmd)
	bash_command(cmd)
	return

def copy_bohra_links(cgt):
	cmd = f"mkdir -p /home/jianszhang/public_html/MDU/STE"
	bash_command(cmd)
	os.chdir(cwd)
	cmd = f"mkdir -p /home/jianszhang/public_html/MDU/STE/{cgt}_{c_date}/"
	bash_command(cmd)
	if os.path.exists(f"cgt{cgt}/report/report.html"):
		cmd = f"cp cgt{cgt}/report/report.html /home/jianszhang/public_html/MDU/STE/{cgt}_{c_date}/"
		bash_command(cmd)
		return f"cgT{cgt}: https://bioinformatics.mdu.unimelb.edu.au/~jianszhang/MDU/STE/{cgt}_{c_date}/report.html"
	else:
		return f"cgT{cgt}: no enough samples for bohra analysis"
def check_conda_envs():
	try:
		my_env = os.environ["CONDA_PREFIX"]
		if "bohra_nf" in my_env:
			return True
		else:
			print("Please activea bohra env: ca /home/khhor/conda/envs/bohra_nf")
			return False
	except:
		print("Please activea bohra env: ca /home/khhor/conda/envs/bhora_nf")
		return False

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("cgt_summary_csv", help="cgt summary tab created on summary step")
	args = parser.parse_args()
	if check_conda_envs():
		print("conda env in activate")
	else:
		sys.exit()
	cgt_list = []
	with open(args.cgt_summary_csv, 'r') as mycsv:
		csvreader = csv.reader(mycsv)
		count = 0
		for line in csvreader:
			if count == 0:
				count = 1
				continue
			cgt = line[0]
			cgt_list.append(cgt)
	link_lines = []
	for cgt in cgt_list:
		#change_to_cgT_folder(cgt)
		link_lines.append(copy_bohra_links(cgt))

	with open("links.txt", 'w') as mylinks:
		mylinks.write("\n".join(link_lines))
if __name__ == "__main__":
	main()
