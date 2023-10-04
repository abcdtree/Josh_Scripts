import pandas as pd
import os
import csv

query_df = pd.read_csv("candida.information.tab", sep="\t")[['ISOLATE', "SPECIES", "SPECIES_KGTDB", "SPECIES_EXP"]]
id_list = query_df["ISOLATE"].tolist()
summary = {}
for mid in id_list:
    if os.path.exists(f"{mid}/{mid}.profile"):
        df_pro = pd.read_csv(f"{mid}/{mid}.profile", sep="\t")[["taxname", "coverage"]]
        for index, row in df_pro.iterrows():
            summary[mid] = [row["taxname"], row["coverage"]]
print(summary)

with open("candida_summary.csv", 'w', newline="") as myout:
    spamwriter = csv.writer(myout)
    spamwriter.writerow(['ISOLATE', "SPECIES", "SPECIES_KGTDB", "SPECIES_EXP", "TaxName", "COVERAGE"])
    for index, row in query_df.iterrows():
        taxn, coverage = summary.get(row["ISOLATE"], ["",""])
        spamwriter.writerow([row["ISOLATE"], row["SPECIES"], row["SPECIES_KGTDB"], row["SPECIES_EXP"], taxn, coverage])
