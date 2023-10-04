import os
import csv


mpath = "/home/mdu/data/M2020-03715"

csv_list = "/home/seq/MDU/incoming/bcl/nextseq/NextSeq500/nextseq/201211_NS500345_0404_AHHJHLAFX2"

id_list = []
for mfolder in os.listdir(mpath):
    if mfolder != "NTC" and os.path.isdir(os.path.join(mpath, mfolder)):
        id_list.append(mfolder)

#print(len(id_list))

with open(os.path.join(csv_list, "standard_bacteria_qc.csv"), 'r') as mycsv:
    csvreader = csv.reader(mycsv)
    title = []
    count = 0
    output_data = []
    for line in csvreader:
        if count == 0:
            count +=1
            title = line
        else:
            mdu_id = line[0]
            if mdu_id in id_list:
                output_data.append(line)

with open(os.path.join(csv_list, "standard_bacteria_qc_f.csv"), 'w') as myout:
    spamwriter = csv.writer(myout)
    spamwriter.writerow(title)
    for line in output_data:
        spamwriter.writerow(line)
