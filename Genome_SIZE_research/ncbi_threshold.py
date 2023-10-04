import numpy as np
import os
import subprocess
from multiprocessing import Pool
import csv
import json

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def check_output(cmd):
	output = subprocess.run(cmd.split(" "), capture_output=True, text=True)
	return output.stderr.strip()

def load_json(mfile):
	json_file = open(mfile, 'r')
	db_dict = json.load(json_file)
	json_file.close()
	return db_dict

def get_stats(taxon):
    filename = taxon.replace(" ", "_")
    if not os.path.exists(f"{filename}.json"):
        cmd = f"datasets summary genome taxon '{taxon}' > {filename}.json"
        bash_command(cmd)
    try:
        taxon_json = load_json(f"{filename}.json")
        assembly_lengths = []
        for subdict in taxon_json["reports"]:
            assembly_lengths.append(int(subdict["assembly_stats"]["total_sequence_length"]))
        #print(assembly_lengths)
        a = np.array(assembly_lengths)
        q25, q75 = np.percentile(a, [25, 75])
        intr_qr = q75 - q25
        max = q75 +(1.5* intr_qr)
        min = q25 -(1.5* intr_qr)
        #print(max, min)
        outlier_count = 0
        for i in assembly_lengths:
            if i > max or i < min:
                outlier_count += 1
        return [taxon, max, min, len(assembly_lengths), outlier_count]
    except:
        return [taxon, 0, 0, 0, 0]


def main():
    with open("ncbi_genome_range.csv", 'r') as mycsv:
        csvreader = csv.reader(mycsv)
        count = 0
        tax_list = []
        for line in csvreader:
            if count == 0:
                count = 1
                continue
            tax_list.append(line[0])

    #get_stats(tax_list[1])
    result_list = []
    with Pool(20) as p:
        result_list = p.map(get_stats, tax_list)
    print("\t".join(["SPECIES", "MAX", "MIN", "TOTAL_NUM", "OUTLIERS"]))
    for line in result_list:
        print("\t".join(list(map(str, line))))

if __name__ == "__main__":
    main()
