import os
import subprocess
import pandas as pd

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def get_id(mpath):
    return mpath.split("/")[-2]

mpath = "/home/jianszhang/mdu_jobs/PTP/PTP_20210720/pt1"
output_list = []

for mfolder in os.listdir(mpath):
    if os.path.isdir(os.path.join(mpath, mfolder)) and "BS" in mfolder:
        contigs = os.path.join(os.path.join(mpath, mfolder, "spades.fa"))
        cmd = f"abricate --db vfdb {str(contigs)} > {str(os.path.join(mpath, mfolder, 'abricate.tab'))}"
        #bash_command(cmd)
        output_list.append(str(os.path.join(mpath, mfolder, "abricate.tab")))

cmd = f"abricate --summary {' '.join(output_list)} > {str(os.path.join(mpath, 'abricate.summary.tab'))}"
#bash_command(cmd)

total_df = pd.DataFrame()
count = 0
for mfile in output_list:
    m_id = get_id(mfile)
    m_df = pd.read_csv(mfile, sep="\t")
    m_df = m_df[(m_df["%COVERAGE"] > 75) & (m_df["%IDENTITY"] > 75)]
    m_df["ID"] = m_id
    m_df = m_df[["ID", "GENE", "%COVERAGE", "%IDENTITY", "PRODUCT"]]
    #print(m_df.head(2))
    if count == 0:
        total_df = m_df.copy()
    else:
        total_df = total_df.append(m_df)
    count += 1

total_df.to_csv(os.path.join(mpath, "abricate.csv"), index=None)
