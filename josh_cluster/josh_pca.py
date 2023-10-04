import numpy as np
import os
import argparse
import skbio
import matplotlib.pyplot as plt



def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("distanceM",  help="distance matrix in tab seperate")
	args = parser.parse_args()

	if args.distanceM:
		if os.path.exists(args.distanceM):
			with open(args.distanceM,'r') as mydis:
				count = 0
				title = []
				data_matrix = []
				id_list = []
				for line in mydis:
					if count == 0:
						title = line.strip().split("\t")[1:]
						count = 1
						continue
					if len(line.strip()) > 1:
						dis_line = list(map(float, line.strip().split("\t")[1:]))
						sample_id = line.strip().split("\t")[0]
						data_matrix.append(dis_line)
						id_list.append(sample_id)
			x_matrix = np.array(data_matrix)
			my_pcoa = skbio.stats.ordination.pcoa(x_matrix)
			#print(x_matrix)
			plt.scatter(my_pcoa.samples['PC1'],  my_pcoa.samples['PC2'])
			for i in range(len(x_matrix)):
				plt.text(my_pcoa.samples.loc[str(i),'PC1'],  my_pcoa.samples.loc[str(i),'PC2'], id_list[i])
			plt.savefig('result.png')
		else:
			print("Distance Matrix file does not exist")
			exit()


if __name__ == "__main__":
	main()
