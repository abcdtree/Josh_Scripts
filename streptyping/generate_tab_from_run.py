import os
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("RUNID", help="runid to create a contigs tab")
	args = parser.parse_args()

	data_path = f"/home/mdu/data/{args.RUNID}"

	output_list = []

	for mfolder in os.listdir(data_path):
		if os.path.isdir(os.path.join(data_path, mfolder)):
			if "ntc" not in mfolder:
				contigs = str(os.path.join(data_path, mfolder, "shovill/shovill.fa"))
				#print(contigs)
				if os.path.exists(contigs):
					output_list.append([mfolder, contigs])

	with open("contigs.tab", 'w') as myout:
		for line in output_list:
			myout.write("\t".join(line) + "\n")

if __name__ == "__main__":
	main()
