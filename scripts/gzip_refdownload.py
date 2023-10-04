import os
import subprocess

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return


def find_species(mfile):
    with open(mfile, 'r') as myread:
        count = 0
        r_line = ""
        for line in myread:
            if count == 0:
                r_line = line
                count += 1
            else:
                break
    info = r_line.strip().split()
    print(info)
    return f"{info[1]}_{info[2]}"

path_of_download = "/home/jianszhang/mdu_jobs/PTP/PTP_20230426/ncbi/refseq/bacteria"
path_to_save = "/home/jianszhang/mdu_jobs/PTP/PTP_20230426/ncbi/contigs"

command = f"mkdir -p {path_to_save}"
bash_command(command)

for sample_folder in os.listdir(path_of_download):
    for mfile in os.listdir(os.path.join(path_of_download, sample_folder)):
        if mfile != "MD5SUMS":
            if "gz" in mfile:
                command = f"gzip -d {os.path.join(path_of_download, sample_folder, mfile)}"
                bash_command(command)
    for mfile in os.listdir(os.path.join(path_of_download, sample_folder)):
        if mfile != "MD5SUMS":
            sp = find_species(os.path.join(path_of_download, sample_folder, mfile))
            new_file_name = sp + "_" + mfile
            command = f"cp {os.path.join(path_of_download, sample_folder, mfile)} \
            {os.path.join(path_to_save, new_file_name)}"
            bash_command(command)
            #print(command)
