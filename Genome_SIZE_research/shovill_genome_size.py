import os
import subprocess
import argparse
import csv
import sys
from multiprocessing import Pool
import pandas as pd

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

def check_genome_size(fasta_path):
    cmd = f"seqkit stats {fasta_path}"
    m_out = check_output(cmd)
    lines = m_out.split("\n")
    if len(lines) > 1:
        info = lines[1].split()
        return [info[3], info[4]]
    else:
        return ["-", "-"]

def check_on_mdu_id(mduid):
    cmd = f"mdu contigs -s {mduid} --assemblier shovill"
    m_out = check_output(cmd)
    try:
        fasta_path = m_out.split()[1]
        return [mduid] + check_genome_size(fasta_path)
    except:
        return [mduid, "-", "-"]

#print(check_on_mdu_id("1998-07812"))

def main():
    df = pd.read_csv("qc_no_covid.csv", sep="\t")[["ISOLATE", "SPECIES", "GENOME_SIZE", "CONTIGS"]]
    mdu_id_list = df.ISOLATE.tolist()
    result_list = []
    with Pool(100) as p:
        result_list = p.map(check_on_mdu_id, mdu_id_list)
    headers = ["ISOLATE", "Shovill_CONTIGS", "Shovill_GSIZE"]
    with open("shovill_genome_size.csv", "w", newline="") as mycsv:
        csvwriter = csv.writer(mycsv)
        csvwriter.writerow(headers)
        for line in result_list:
            csvwriter.writerow(line)
    df_shovill = pd.DataFrame(result_list, columns=headers)
    df_merge = df.merge(df_shovill, on="ISOLATE", how="left")
    df_merge.to_csv("shovill_result_merge.csv", index=None)

if __name__ == "__main__":
    main()
