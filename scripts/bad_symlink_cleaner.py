import os
from pathlib import Path



mtb_path = "/home/jianszhang/analysis/mtb"
path_dict = {}
with open(os.path.join(mtb_path, "all_isolates_new.tab"), 'r') as mytab:
    for line in mytab:
        if len(line.strip()) > 0:
            mid, r1, r2 = line.strip().split("\t")
            path_dict[mid] = (r1, r2)
print(len(path_dict))
#se_path = "/home/jianszhang/analysis/enteritidis/"
for folder in os.listdir(mtb_path):
    if os.path.isdir(os.path.join(mtb_path, folder)):
        if os.path.islink(os.path.join(mtb_path, folder, "R1.fq.gz")):
            #print(os.path.join(mtb_path, folder))
            if not Path(os.path.join(mtb_path, folder, "R1.fq.gz")).exists():
                os.remove(os.path.join(mtb_path, folder, "R1.fq.gz"))
                os.remove(os.path.join(mtb_path, folder, "R2.fq.gz"))
                r1, r2 = path_dict.get(folder, ("", ""))
                #print(r1, r2)
                #break
                if len(r1) > 0:
                    os.symlink(r1, os.path.join(mtb_path, folder, "R1.fq.gz"))
                    os.symlink(r2, os.path.join(mtb_path, folder, "R2.fq.gz"))


'''for folder in os.listdir(se_path):
    if os.path.isdir(os.path.join(se_path, folder)):
        for subf in os.listdir(os.path.join(se_path, folder)):
            if os.path.isdir(os.path.join(se_path, folder, subf)):
                for mfile in os.listdir(os.path.join(se_path, folder, subf)):
                    if not Path(os.path.join(se_path, folder, subf, mfile)).exists():
                        #print(os.path.join(se_path, folder, subf, mfile))
                        os.remove(os.path.join(se_path, folder, subf, mfile))'''
