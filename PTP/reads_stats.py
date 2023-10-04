import os
import subprocess

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def check_output(cmd):
	output = subprocess.run(cmd.split(" "), capture_output=True, text=True)
	return output.stdout.strip()

def run_tax(logid):
    cmd = f"cut -f 3 {logid}.log | taxonkit lineage -r -n > {logid}.tax"
    bash_command(cmd)

def merge_two(logid):
    cmd = f"paste {logid}.log {logid}.tax > {logid}.combine"
    bash_command(cmd)

def no_human(logid):
    cmd = f"grep -v 'Homo sapiens' {logid}.combine | cut -f 2 > {logid}.no_human"
    bash_command(cmd)

def virus_only(logid):
    cmd = f"grep 'Viruses' {logid}.combine | cut -f 2 > {logid}.virus"
    bash_command(cmd)

def monkey_pox_only(mid):
	cmd = f"grep 'Monkeypox' {mid}.combine | cut -f 2 > {mid}.monkypox"
	bash_command(cmd)
	cmd = f"seqkit grep -f {mid}.monkypox {mid}_no_human.fa -o {mid}_monkeypox.fa"
	bash_command(cmd)

def seqkit_grep(logid, type):
    cmd = f"seqkit grep -f {logid}.{type} /home/jianszhang/UNSGM_PTP/{logid}_R1.fastq.gz -o ./{type}/{logid}_{type}_R1.fastq.gz"
    bash_command(cmd)
    cmd = f"seqkit grep -f {logid}.{type} /home/jianszhang/UNSGM_PTP/{logid}_R2.fastq.gz -o ./{type}/{logid}_{type}_R2.fastq.gz"
    bash_command(cmd)

def find_largest_contigs(contigs):
	cmd = f"seqkit sort -l -r {contigs} | seqkit seq -n -i | head -n 1 > {contigs}.top_id"
	bash_command(cmd)

def create_largest_contigs_fa(contigs):
	sample_id = contigs.split(".")[0]
	find_largest_contigs(contigs)
	largest_id =  ""
	with open(f"{contigs}.top_id", 'r') as myid:
		largest_id = myid.readline().strip()
	cmd = f"seqkit grep -p {largest_id} {contigs} > {sample_id}_largest.fa"
	#print(cmd)
	bash_command(cmd)
	cmd = f"seqkit replace -p ^{largest_id} -r {sample_id} {sample_id}_largest.fa > {sample_id}_l_rename.fa"
	bash_command(cmd)

def run_shovill(sample_id):
	cmd = f"shovill --outdir {sample_id}/shovill -R1 {sample_id}/{sample_id}_no_human_R1.fastq.gz -R2 {sample_id}/{sample_id}_no_human_R2.fastq.gz"
	bash_command(cmd)

def run_kraken2(sample_id):
	contigs = f"{sample_id}_no_human.fa"
	cmd = f"kraken2 --db /tmp/pluspf {contigs} --report {sample_id}_pluspf.tab --output {sample_id}.log --memory-mapping"
	bash_command(cmd)

def create_no_reads_bed(sample_id):
	bam_home = "/home/jianszhang/UNSGM_PTP/data/"
	cmd = f"samtools depth {bam_home}/{sample_id}/consensus/{sample_id}.sorted.bam -a -o {bam_home}/{sample_id}/consensus/{sample_id}.depth"
	#print(cmd)
	#bash_command(cmd)
	no_reads_line = []
	with open(f"{bam_home}/{sample_id}/consensus/{sample_id}.depth", 'r') as mydepth:
		for line in mydepth:
			contigs, pos, n = line.strip().split()
			if int(n) == 0:
				no_reads_line.append(f"{contigs}\t{pos}")
	with open(f"{bam_home}/{sample_id}/consensus/{sample_id}_no_read.tab", 'w') as myout:
		myout.write("\n".join(no_reads_line))

def consensus_with_no_reads(sample_id):
	bam_home = "/home/jianszhang/UNSGM_PTP/data/"
	ref = f"{bam_home}/ref/GCA_014621585.1_ASM1462158v1_genomic.fna"
	cmd = f"cat {ref} | bcftools consensus -m {bam_home}/{sample_id}/consensus/{sample_id}_no_read.tab {bam_home}/{sample_id}/consensus/{sample_id}.calls.vcf.gz > {bam_home}/{sample_id}/consensus/{sample_id}.consensus.withm.fa"
	#print(cmd)
	bash_command(cmd)

sample_list = ["Sample-01-X-2023",
"Sample-02-X-2023","Sample-03-X-2023",
"Sample-04-X-2022","Sample-05-X-2022",
"Sample-06-X-2022",
"Sample-07-Y-2023","Sample-08-Y-2023"
]

for mid in sample_list:
	#create_largest_contigs_fa(f"{mid}.fa")
    #run_tax(mid)
    #merge_two(mid)
	#monkey_pox_only(mid)
    #no_human(mid)
    #virus_only(mid)
    #seqkit_grep(mid, "no_human")
    #seqkit_grep(mid, "virus")
	#run_shovill(mid)
	#run_kraken2(mid)
	#create_no_reads_bed(mid)
	consensus_with_no_reads(mid)
