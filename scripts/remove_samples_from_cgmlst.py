import pandas as pd
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("samplelist", help="list of samples to remove")
	args = parser.parse_args()
	cgmlst_allele = "/home/mdu/analysis/cgmlst/salmonella_enterica/overall_alleles.txt"
	df = pd.read_csv(cgmlst_allele, sep="\t")

	id_list = []
	with open(args.samplelist, 'r') as mylist:
		for line in mylist:
			info = line.strip()
			if len(info) != 0:
				id_list.append(info)

	#print(id_list)
	#print(len(id_list))
	#print(df.FILE.count)

	df_short = df[~(df['FILE'].isin(id_list))]

	#print(df_short.FILE.count)
	df_short.to_csv("/home/mdu/analysis/cgmlst/salmonella_enterica/overall_alleles.txt.new", index=None, sep="\t")

if __name__ == "__main__":
	main()
