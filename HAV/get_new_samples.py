import os
import pandas as pd
from newick import read

def change_name(x):
	seq_name = x["Sequence Name"]
	gt = seq_name.split("_")[-1]
	if gt in ["IIIB", "IIIA", "IIB", "IIA", "IB", "IA", "IV", "V"]:
		return  seq_name
	else:
		return seq_name + "_" + str(x["Genotype"])


new_sample_path = "/home/jianszhang/analysis/hav/HAVALL_2022.2/09_23/ids.txt"
new_samples = []
with open(new_sample_path, 'r') as myids:
	for line in myids:
		new_samples.append(line.strip())
print(len(new_samples))

df = pd.read_excel("/home/jianszhang/analysis/hav/HAVALL_2022.2/09_23/HAV_20230829.xlsx")
df = df[["Sequence Name Report","Sequence Name", "Genotype", "REDCap ID", "Jurisdiction"]]
df = df.fillna("NA")
df["mid"] = df.apply(change_name, axis=1)
#df = df[df["Sequence Name"].isin(new_sample_short)]
#df = df.fillna("NA")
df["new_names"] = df.apply(lambda x: x["Sequence Name Report"] + "|"+str(x["REDCap ID"])+"|"+x["Jurisdiction"], axis=1)
new_names_list = df["new_names"].tolist()
old_id = df["mid"].tolist()
#print(new_names_list)

new_output = df[df["Sequence Name"].isin(new_samples)]["new_names"].tolist()
print(len(new_output))

new_output_IIIA = df[(df["Sequence Name"].isin(new_samples)) & (df["Genotype"] == "IIIA")]["new_names"].tolist()
new_output_IA = df[(df["Sequence Name"].isin(new_samples)) & (df["Genotype"] == "IA")]["new_names"].tolist()
new_output_IB = df[(df["Sequence Name"].isin(new_samples)) & (df["Genotype"] == "IB")]["new_names"].tolist()
print(len(new_output_IIIA))
print(len(new_output_IA))
print(len(new_output_IB))

#new_short = map(lambda x: x.split("|")[0], new_output)


for gtype in [ "IA", "IB", "IIIA"]:

	tree_path = f"/home/jianszhang/analysis/hav/HAVALL_2022.2/09_23/{gtype}.tree"
	#mtree = read(tree_path)
	output_lines = []
	with open(tree_path, 'r') as mytree:
		for line in mytree:
			#print(line)
			new_line = line
			for i in range(len(new_names_list)):
				new_line = new_line.replace(old_id[i], new_names_list[i])
			output_lines.append(new_line)
	#print(output_lines)
	with open(f"/home/jianszhang/analysis/hav/HAVALL_2022.2/09_23/{gtype}2.tree","w") as myout:
		for line in output_lines:
			myout.write(line)

#print(mtree[0].ascii_art())

with open("new.txt", 'w') as myout:
	myout.write("\n".join(new_output))

with open("new_IIIA.txt", 'w') as myout:
	myout.write("\n".join(new_output_IIIA))

with open("new_IA.txt", 'w') as myout:
	myout.write("\n".join(new_output_IA))

with open("new_IB.txt", 'w') as myout:
	myout.write("\n".join(new_output_IB))
