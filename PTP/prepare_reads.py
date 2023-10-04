import os

mpath = "/home/jianszhang/mdu_jobs/PTP/PTP_20210720/pt1"

with open(os.path.join(mpath, "readsandcontigs.tab"), 'w') as myout:
    myout.write("ID\tR1\tR2\tCONTIGS\n")
    for mfolder in os.listdir(mpath):
        if os.path.isdir(os.path.join(mpath, mfolder)):
            r1 = str(os.path.join(mpath, mfolder, f"{mfolder}_trim_R1.fastq.gz"))
            r2 = str(os.path.join(mpath, mfolder, f"{mfolder}_trim_R2.fastq.gz"))
            contigs = str(os.path.join(mpath, mfolder, "spades.fa"))
            myout.write(f"{mfolder}\t{r1}\t{r2}\t{contigs}\n")
