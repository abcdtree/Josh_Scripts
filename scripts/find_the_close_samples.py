import pandas as pd
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("sample_id", help="the focus isolates")
	parser.add_argument("matrix", help="mashtree distance matrix")
	parser.add_argument("-n", "--number", default=10, help="number of samples to output")
	args = parser.parse_args()
	df_matrix = pd.read_csv(args.matrix, sep="\t")[["Isolate",args.sample_id]]
	df_matrix = df_matrix.sort_values(by=args.sample_id)
	info_dict = {}
	for index, x in df_matrix.iterrows():
		info_dict[x["Isolate"]] = x[args.sample_id]
	sorted_id = df_matrix["Isolate"].tolist()
	num_of_out = min(int(args.number)+1, len(sorted_id))
	count = 0
	for id in sorted_id:
		if count < num_of_out:
			print(f"{id}\t{info_dict.get(id)}")
			count+=1
	#print(df_matrix.head(2))

if __name__ == "__main__":
	main()
