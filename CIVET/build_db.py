import os
import subprocess
#from multiprocessing import Pool
import argparse
import sys

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("FASTA", help="a fasta with multiple sequences")
	parser.add_argument("Reference", help="reference genome")
	parser.add_argument("--names", "-n", help="a file listed names of the sequences to build db")
	args = parser.parse_args()

	name_list = []
	if args.names != None:
		if os.path.exists(args.names):
			with open(args.names, 'r') as mynamefile:
				for line in mynamefile:
					name_list.append(line.strip())
		else:
			print(f"could not find {args.name} name file, please check your input")
			sys.exit(-1)
	else:
		cmd = f"grep '>' {args.FASTA} > tmp.names"
		bash_command(cmd)
		with open("tmp.names", 'r') as mynamefile:
			for line in mynamefile:
				name_list.append(line.split()[0].replace(">", ""))
		cmd = "rm -f tmp.names"
		bash_command(cmd)
	#print(name_list)
	cmd = "rm -f combine.fa"
	bash_command(cmd)
	for name in name_list:
		if len(name) > 0:
			cmd = f"seqkit grep -p {name} {args.FASTA} -o {name}.fa"
			bash_command(cmd)
			cmd = f"python3 /home/jianszhang/github/atom/CIVET/create_consensus.py \
			-r {args.Reference} -R1 {name}.fa \
			--fasta -n -p {name}"
			bash_command(cmd)
			cmd_combine = f"cat {name}.consensus.fa >> combine.fa"
			bash_command(cmd_combine)
			cmd = f"mkdir -p {name}"
			bash_command(cmd)
			cmd = f"mv {name}*.* {name}/"
			bash_command(cmd)

	cmd = "seqkit stats combine.fa"
	bash_command(cmd)


if __name__ == "__main__":
	main()
