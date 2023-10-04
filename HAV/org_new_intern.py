import csv
import os

result_dict = {}
with open("type_check.tab", 'r') as mytab:
    for line in mytab:
        info = line.strip().split("\t")
        acc, gtype, score = info[:3]
        p = result_dict.get(acc, [])
        if len(p) == 0:
            if float(score) >= 90:
                result_dict[acc] = [acc, gtype[2:]]
            else:
                result_dict[acc] = [acc, "FAIL"]

with open("serotype.tab", 'w') as mytab:
    for key in result_dict:
        acc, gtype = result_dict.get(key)
        mytab.write(f"{acc}\t{gtype}\n")
outline = []
with open("sequences_0101.fasta", 'r') as myfasta:
    for line in myfasta:
        if line[0] == ">":
            m_acc = line[1:].split("|")[0].strip()
            gtype = result_dict.get(m_acc)[1]
            outline.append(f">{m_acc}_{gtype}\n")
        else:
            outline.append(line)

with open("sequences_correct.fasta", 'w') as myout:
    for line in outline:
        myout.write(line)
