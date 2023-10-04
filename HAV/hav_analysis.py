import os
import sys
import pandas as pd
import subprocess
import argparse

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

def unique_name(x):
	seq_report = x["Sequence Name Report"]
	seq_name = x["Sequence Name"]
	genotype = x["Genotype"]
	try:
		if genotype not in seq_name:
			return seq_name +"_" + genotype
		else:
			return seq_name
	except:
		try:
			return str(seq_report) + "_"+genotype
		except:
			return "EMPTY"
def coverage(x):
	return str(round(x["MATCH"]/float(x["LENGTH"])*100, 2))+"%"
def covert_int(x):
	try:
		return int(x)
	except:
		return x

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("meta_aus",  help="most recent australian meta data xlsx file")
	parser.add_argument("meta_int", help="most recent international meta data xlsx file")
	parser.add_argument("--output", "-o", default="HAV_report.xlsx", help="folder ")
	parser.add_argument("--analysis_folder", "-a", default=os.getcwd(), help="folder the assembly files was set up")
	parser.add_argument("--tree", "-t", action='store_true', help="create tree for each genotype")
	parser.add_argument("--ausdb",default="HAV_AUS_0822.fa", help="blastn db with aus samples only")
	parser.add_argument("--interdb", default="HAV_REST_0822_NDUP.fa", help="blastn db with international samples")
	args = parser.parse_args()

	#read meta data
	df_meta_aus = None
	df_meta_int = None
	if os.path.exists(args.meta_aus):
		df_meta_aus = pd.read_excel(args.meta_aus)[["Sequence Name Report","Sequence Name","Genotype","REDCap ID","Jurisdiction ID","Jurisdiction","Specimen collection date","Outbreak ID","Cluster ID (from Report in 2018)","Epi Risk Factor 1","Epi Risk Factor 2","Risk Country","Risk Food","Age at Onset (years)"]]
		df_meta_aus["SEQ ID"] = df_meta_aus.apply(unique_name, axis=1)
		df_meta_aus = df_meta_aus[["SEQ ID", "Genotype","REDCap ID","Jurisdiction ID","Jurisdiction","Specimen collection date","Outbreak ID","Cluster ID (from Report in 2018)","Epi Risk Factor 1","Epi Risk Factor 2","Risk Country","Risk Food","Age at Onset (years)"]]
		df_meta_aus["Specimen collection date"] = df_meta_aus["Specimen collection date"].dt.date
		df_meta_aus["Jurisdiction ID"] = df_meta_aus["Jurisdiction ID"].astype(str)
		df_meta_aus["Age at Onset (years)"] = df_meta_aus["Age at Onset (years)"].apply(covert_int)
	else:
		print(f"{args.meta_aus} does not exist")
		sys.exit(1)

	#make_label_dict
	meta_label_dict = {}
	for index, row in df_meta_aus.iterrows():
		mid = row["SEQ ID"]
		redcp_id = row["REDCap ID"]
		juris = row["Jurisdiction"]
		meta_label_dict[mid] = f"{mid}|{redcp_id}|{juris}"

	if os.path.exists(args.meta_int):
		df_meta_int = pd.read_excel(args.meta_int)[["SEQ ID", "Country", "Year", "Sample Source", "ORIGIN Country", "ORIGIN Food"]]
	else:
		print(f"{args.meta_int} does not exist")
		sys.exit(1)

	#cmd = "mv -f HAV_report.xlsx HAV_report.xlsx.backup"
	#bash_command(cmd)


	#with pd.ExcelWriter('output.xlsx', mode='a') as writer:

	#list the new samples (folders) in the current analysis folder
	serotype_set = set()
	for mfile in os.listdir(args.analysis_folder):
		mpath = os.path.join(args.analysis_folder, mfile)
		if os.path.isdir(mpath) and mfile != "new_samples" and mfile != "new_prepare":
			for sfile in os.listdir(mpath):
				if "fasta" in sfile:
					query_sample = os.path.join(mpath, sfile)
					info = sfile.split(".")[0].split("_")
					serotype = info[-1]
					serotype_set.add(serotype)
					#short_id = info[-3]
					full_name = "_".join(info)
					#label_name = meta_label_dict.get(full_name, f"{full_name} | |")
					run_blastn(query_sample, args.ausdb, os.path.join(mpath, f"{full_name}_aus.tab"))
					run_blastn(query_sample, args.interdb, os.path.join(mpath, f"{full_name}_int.tab"))
					# aus analysis
					c_names =  ["Query ID","SEQ ID", "IDENTITY", "MATCH", "LENGTH"]
					df_blastn_aus = pd.read_csv( os.path.join(mpath, f"{full_name}_aus.tab"), sep="\t", names = c_names)
					df_blastn_aus["COVERAGE"] = df_blastn_aus.apply(coverage, axis=1)
					df_report_aus = df_blastn_aus[["Query ID", "SEQ ID", "IDENTITY", "COVERAGE"]].merge(df_meta_aus, on="SEQ ID", how="left")
					# int analysis
					df_blastn_int = pd.read_csv( os.path.join(mpath, f"{full_name}_int.tab"), sep="\t", names = c_names)
					df_blastn_int["COVERAGE"] = df_blastn_int.apply(coverage, axis=1)
					df_report_int = df_blastn_int[["Query ID", "SEQ ID", "IDENTITY", "COVERAGE"]].merge(df_meta_int, on="SEQ ID", how="left")
					if os.path.exists(args.output):
						with pd.ExcelWriter(args.output, mode='a') as writer:
							df_report_aus.to_excel(writer, sheet_name=f"{full_name}_AUS",index=None)
							df_report_int.to_excel(writer, sheet_name=f"{full_name}_INT",index=None)
					else:
						with pd.ExcelWriter(args.output) as writer:
							df_report_aus.to_excel(writer, sheet_name=f"{full_name}_AUS",index=None)
							df_report_int.to_excel(writer, sheet_name=f"{full_name}_INT",index=None)
	if args.tree:
		for sero in serotype_set:
			#create sero fasta
			cmd1 = f"seqkit grep -p _{sero}$ -r -n {args.ausdb} > {sero}.fa"
			bash_command(cmd1)
			#create aln
			cmd2 = f"clustalo -i {sero}.fa -o {sero}.aln --outfmt fasta"
			bash_command(cmd2)
			#build fasttree
			cmd3 = f"fasttree -nt {sero}.aln > {sero}.tree"
			bash_command(cmd3)


if __name__ == "__main__":
	main()
