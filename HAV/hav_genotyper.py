import subprocess
import os
import argparse
import csv

genotype_db_path = "/home/jianszhang/analysis/hav/DataResources/TypeDB.fa"

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

def summary_genotype(blastn_out, summary_out):
	output_dict = {}
	with open(blastn_out, 'r') as myinput:
		for line in myinput:
			info = line.strip().split("\t")
			id, genotype, rate = info[:3]
			genotype = genotype.replace("Gt","")
			correct_id = id +"_" + genotype
			if id not in output_dict.keys():
				output_dict[id] = [genotype, rate, correct_id]
			else:
				continue
	with open(summary_out, "w", newline="") as mycsv:
		title = ["ID", "Genotype", "Rate", "SEQ ID"]
		spamwriter = csv.writer(mycsv)
		spamwriter.writerow(title)
		for key in output_dict:
			info = output_dict[key]
			spamwriter.writerow([key] + info)

def correct_fasta(genotype_summary, input_fasta):
	#create alias file
	cmd = f"csvtk csv2tab {genotype_summary} | cut -f 1,4 > tmp.txt"
	bash_command(cmd)
	#correct seqname
	if "ncbi" in genotype_summary:
		cmd = "seqkit replace -p '^(\\S+).+?$' -r '{kv}' -k tmp.txt " + input_fasta +  " > " + input_fasta + ".corrected"
	else:
		cmd = "seqkit replace -p '^(\\S+).?$' -r '{kv}' -k tmp.txt " + input_fasta +  " > " + input_fasta + ".corrected"
	bash_command(cmd)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("query",  help="query fasta files")
	parser.add_argument("--output", "-o", help="output prefix", default="mdu")
	args = parser.parse_args()

	if os.path.exists(args.query):
		run_blastn(args.query, genotype_db_path, f"{args.output}_blastn_summary.tab")
		summary_genotype(f"{args.output}_blastn_summary.tab", f"{args.output}_genotype_summary.csv")
		correct_fasta(f"{args.output}_genotype_summary.csv", args.query)

	else:
		print(f"Could not find {args.query}, please check your input")

if __name__ == "__main__":
	main()
