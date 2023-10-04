import os
import subprocess
import logging
import argparse

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("idfile", help="list of SRA ids to download")
	parser.add_argument("--outtab", default="sra.tab", help="output tab file for bohra")
	args = parser.parse_args()
	outfile = open(args.outtab, 'w')

	with open(args.idfile, 'r') as myids:
		for line in myids:
			m_id = line.strip()
			print(f"****start to download {m_id}****")
			download_command = f"/home/jianszhang/downloads/tools/sratoolkit/bin/fasterq-dump -p -e 20 {m_id}"
			bash_command(download_command)
			print(download_command)
			print(f"****{m_id} downloading process finished****")
			print(f"****gzip download files****")
			cmd = f"mkdir {m_id}"
			bash_command(cmd)
			path_1 = os.path.join(os.getcwd(),m_id+"_1.fastq")
			path_2 = os.path.join(os.getcwd(),m_id+"_2.fastq")
			if not os.path.exists(path_1):
				print(f"****{m_id} download failed")
				continue
			cmd = f"mv {m_id}*.fastq {m_id}/"
			bash_command(cmd)
			path_1 = os.path.join(os.getcwd(),m_id, m_id+"_1.fastq")
			path_2 = os.path.join(os.getcwd(),m_id, m_id+"_2.fastq")
			cmd = f"gzip -1 {path_1}"
			bash_command(cmd)
			cmd = f"gzip -1 {path_2}"
			bash_command(cmd)
			outfile.write(f"{m_id}\t{path_1}.gz\t{path_2}.gz\n")
			print(f"****{m_id} path was wroten into sra.tab**")

	print("Job Finished")
	outfile.close()

if __name__ == "__main__":
	main()
