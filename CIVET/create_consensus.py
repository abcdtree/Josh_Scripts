import os
import subprocess
import argparse

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def create_no_reads_bed(prefix):
	cmd = f"samtools depth {prefix}.sorted.bam -aa -o {prefix}.depth"
	#print(cmd)
	bash_command(cmd)
	no_reads_line = []
	with open(f"{prefix}.depth", 'r') as mydepth:
		for line in mydepth:
			contigs, pos, n = line.strip().split()
			if int(n) == 0:
				no_reads_line.append(f"{contigs}\t{pos}")
	with open(f"{prefix}_no_read.tab", 'w') as myout:
		myout.write("\n".join(no_reads_line))

def consensus_with_no_reads(prefix, ref):
	cmd = f"cat {ref} | bcftools consensus -m {prefix}_no_read.tab {prefix}.calls.vcf.gz > {prefix}.consensus.fa"
	bash_command(cmd)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--reference", '-r', help="Checking the RUN ID for a MDU-ID")
	parser.add_argument("--read1",'-R1', help="paired reads one")
	parser.add_argument("--read2",'-R2', help="paired reads two")
	parser.add_argument("--ONT", action="store_true", help="single long reads is provided")
	parser.add_argument("--fasta", action="store_true", help="single long contigs is provided")
	parser.add_argument("--prefix", "-p", help="prefix for output", default="aln")
	parser.add_argument("--with_n", '-n', action='store_true', help="mark the missing region as N")
	args = parser.parse_args()

	#minimap2 and samtools to create bam file
	cmd = ""
	if args.ONT:
		cmd = f"minimap2 -ax map-ont {args.reference} {args.read1} | samtools sort --threads 16 > {args.prefix}.sorted.bam"
	elif args.fasta:
		cmd = f"minimap2 -a {args.reference} {args.read1} | samtools sort --threads 16 > {args.prefix}.sorted.bam"
	else:
		cmd = f"minimap2 -ax sr {args.reference} {args.read1} {args.read2} | samtools sort --threads 16 > {args.prefix}.sorted.bam"
	print(cmd)
	bash_command(cmd)
	#bcftools
	cmd2 = f"bcftools mpileup -Ou -f {args.reference} {args.prefix}.sorted.bam | bcftools call -mv -Oz -o {args.prefix}.calls.vcf.gz"
	print(cmd2)
	bash_command(cmd2)
	cmd3 = f"bcftools index {args.prefix}.calls.vcf.gz"
	print(cmd3)
	bash_command(cmd3)
	#create consensus
	if args.with_n:
		#create consensus with N
		create_no_reads_bed(args.prefix)
		consensus_with_no_reads(args.prefix, args.reference)
	else:
		cmd4 = f"cat {args.reference} | bcftools consensus {args.prefix}.calls.vcf.gz > {args.prefix}.consensus.fa"
		print(cmd4)
		bash_command(cmd4)

	cmd5 = f'sed -i "1s/.*/>{args.prefix}/" {args.prefix}.consensus.fa'
	bash_command(cmd5)


if __name__ == "__main__":
	main()
