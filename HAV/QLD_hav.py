import os
import pandas as pd

df_hav_meta = pd.read_excel("HAV_20230829.xlsx")

#print(df_hav_meta.head())
new_QLD_list = []
with  open("QLD_new.txt", 'r') as myqld:
    new_QLD_list = [line.strip() for line in myqld]

#print(new_QLD_list)

df_hav_meta = df_hav_meta[["Sequence Name", "Genotype"]]
df_hav_meta_QLD = df_hav_meta[df_hav_meta["Sequence Name"].isin(new_QLD_list)]
QLD_dict = {}
for index, x in df_hav_meta_QLD.iterrows():
    QLD_dict[x["Sequence Name"]] = x["Genotype"]

with open("QLD_Genome.txt", 'r') as myfa:
    title = True
    save_line = ""
    seq_name = ""
    for line in myfa:
        if title:
            seq_name = line.strip()[1:]
            type = QLD_dict[seq_name]
            seq_name = seq_name + "_" + type
            save_line = line.strip() + "_" + type
            title = False
        else:
            seq_line = line.strip()
            with open(seq_name + ".fasta", 'w') as myout:
                myout.write(save_line + "\n")
                myout.write(seq_line +"\n")
            title = True
