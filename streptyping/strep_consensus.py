import os
import argparse
import subprocess

reference_path = "/home/jianszhang/database/blastn/seroba/GCF_002076835.1_ASM207683v1_genomic.fna"

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("readstab",  help="reads tab file with 3 columns mduid<tab>r1<tab>r2")
	parser.add_argument("--output", "-o", default="consensus", help="output folder for the consensus")
	parser.add_argument("--summary", action="store_true", help="summary the tab file only")
	args = parser.parse_args()

	output_tab = []
	with open(args.readstab, 'r') as mytab:
		for line in mytab:
			info = line.strip().split("\t")
			if len(info) == 3:
				mid, r1, r2 = info
				if not args.summary:
					cmd = f"python3 /home/jianszhang/github/atom/PTP/create_consensus.py -r {reference_path} -R1 {r1} -R2 {r2} -p {mid} -n"
					bash_command(cmd)
					cmd = f"mkdir -p {args.output}"
					bash_command(cmd)
					cmd = f"mv -f {mid}.consensus.fa {args.output}/"
					bash_command(cmd)
					cmd = f"rm {mid}.*"
					bash_command(cmd)
				output_tab.append(f"{mid}\t{args.output}/{mid}.consensus.fa")
	with open("consensus.tab", 'w') as myout:
		for line in output_tab:
			myout.write(line + "\n")


if __name__ == "__main__":
	main()
