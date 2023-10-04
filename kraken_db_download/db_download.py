import subprocess
import os
import argparse
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

def efetch_download(mid):
	if mid[:3] == "NGB":
		return False
	command = f'esearch -db nucleotide -query "{mid}" | efetch -format fasta > {mid}.fasta'
	bash_command(command)
	#print(command)
	return True

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("id_list", help="list of ids to download from ncbi")
	parser.add_argument("-continue_from_number", "-c", default="0", help="continue from group i")
	args = parser.parse_args()
	id_list = []
	with open(args.id_list, 'r') as myids:
		for line in myids:
			id_list.append(line.strip())

	group_number = 1000
	len_of_list = len(id_list)
	number_of_group = len_of_list//group_number + 1
	for i in range(number_of_group+1):
		if i == number_of_group:
			sample_list = id_list[i*1000:]
		sample_list = id_list[i*1000:(i+1)*1000]
		if i < int(args.continue_from_number):
			continue
		with Pool(3) as p:
			result = p.map(efetch_download, sample_list)
		print(f"Download finish for the ids from {i*1000} to {(i+1)*1000}, if need to restart, -c {i+1}")

if __name__ == "__main__":
	main()
