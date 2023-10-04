import os
import subprocess

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return


def my_command(mpath, mfolder):
    backup_cmd = f"cp {mpath}/{mfolder}/isolates.tab {mpath}/{mfolder}/isolates.tab.backup20230113"
    bash_command(backup_cmd)
    grep_cmd = f"grep -v -f {mpath}/remove.list {mpath}/{mfolder}/isolates.tab.backup20230113 > {mpath}/{mfolder}/isolates.tab"
    bash_command(grep_cmd)
    #print(grep_cmd)

mpath = "/home/jianszhang/analysis/tb_dev"
folder_list = ["Lineage_1", "Lineage_2", "Lineage_3", "Lineage_4"]

for mfolder in folder_list:
    my_command(mpath, mfolder)
