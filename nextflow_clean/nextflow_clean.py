import os
import subprocess

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

#home_path = "/home/jianszhang/mdu_jobs/CC"
#home_path = "/home/jianszhang/mdu_jobs/seroba_related"
home_path = "/home/jianszhang/mdu_jobs/BT"
list_of_working_dir = []
for mdir in os.listdir(home_path):
    if os.path.isdir(os.path.join(home_path, mdir)):
        list_of_working_dir.append(os.path.join(home_path, mdir))

for mpath in list_of_working_dir:
    if "work" in os.listdir(mpath):
        os.chdir(mpath)
        cmd = "nextflow clean -f"
        bash_command(cmd)
