import os
import argparse
import subprocess
import csv


seroba_blastn_db = "/home/jianszhang/database/blastn/seroba/seroba.fa"
def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def run_blastn(query_sample, db, output):
	cmd = f'blastn -task blastn -query {query_sample} -db {db} -evalue 1e-10 -outfmt "6 qseqid sseqid pident length qlen"\
	 | sort -k 3 -rm > {output}'
	bash_command(cmd)


def spades_assembly(r1, r2, mid, core=50):
	cmd = f"spades.py -1 {r1} -2 {r2} -o {mid} --isolate -t {core} --tmp-dir ./tmp"
	bash_command(cmd)
	cmd = f"mkdir -p contigs"
	bash_command(cmd)
	cmd = f"cp {mid}/contigs.fasta contigs/{mid}.fa"
	bash_command(cmd)
	cmd = "rm -rf ./tmp"
	bash_command(cmd)
	return

def run_blastn_on_sample(contigs, mid):
	cmd = f"mkdir -p blastn_result"
	bash_command(cmd)
	run_blastn(contigs, seroba_blastn_db, f"./blastn_result/{mid}.blastn")

def handle_blastn_result(blastn_file):
	with open(blastn_file, 'r') as myblastn:
		result_pool = []
		top_score = 0
		for line in myblastn:
			info = line.strip().split("\t")
			if len(info) != 5:
				if len(result_pool) == 0:
					return ["Error", "N/A"]
				else:
					return ["|".join(result_pool), str(top_score)]
			else:
				score = float(info[2])
				if score >= top_score:
					top_score = score
					result_pool.append(info[1])
				else:
					return ["|".join(result_pool), str(top_score)]
		return ["|".join(result_pool), str(top_score)]

def summary_serotype(output_file):
	summary = [["MDU_ID", "SEROTYPE", "SCORE"]]
	for blastn_f in os.listdir("./blastn_result"):
		mid = blastn_f.split(".")[0]
		serotype, score = handle_blastn_result(f"./blastn_result/{blastn_f}")
		summary.append([mid, serotype, score])
	with open(output_file, 'w', newline="") as myout:
		spamwriter = csv.writer(myout)
		for line in summary:
			spamwriter.writerow(line)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--readstab","-r",  help="reads tab file with 3 columns mduid<tab>r1<tab>r2")
	parser.add_argument("--contigstab", '-c', help="contigs tab file with 2 columns mduid<tab>contigs")
	parser.add_argument("--output", "-o", default="streptyping.csv", help="output file")
	parser.add_argument("--summary", action="store_true", help="summary the blastn files only")
	args = parser.parse_args()
	if not args.summary:
		if args.readstab:
			if os.path.exists(args.readstab):
				with open(args.readstab, 'r') as mytab:
					for line in mytab:
						info = line.strip().split("\t")
						if len(info) == 3:
							mduid, r1, r2   = info
							spades_assembly(r1, r2, mduid)
							run_blastn_on_sample(f"contigs/{mduid}.fa", mduid)
						else:
							continue
		if args.contigstab:
			if os.path.exists(args.contigstab):
				with open(args.contigstab, 'r') as mytab:
					for line in mytab:
						info = line.strip().split("\t")
						if len(info) == 2:
							mduid, contigs = info
							run_blastn_on_sample(contigs, mduid)
						else:
							continue
	summary_serotype(args.output)

if __name__ == "__main__":
	main()
