import os
import subprocess

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def run_clean_up(mpath):
    cmd = f"rm -rf {mpath}/work"
    bash_command(cmd)
    return

home_path = "/home/jianszhang/mdu_jobs/CC"
for mfolder in os.listdir(home_path):
    if os.path.isdir(os.path.join(home_path, mfolder)):
        if os.path.exists(os.path.join(home_path, mfolder, "work")):
            run_clean_up(os.path.join(home_path, mfolder))
        else:
            for subfolder in os.listdir(os.path.join(home_path, mfolder)):
                if os.path.isdir(os.path.join(home_path, mfolder, subfolder)):
                    if os.path.exists(os.path.join(home_path, mfolder, subfolder, "work")):
                        run_clean_up(os.path.join(home_path, mfolder, subfolder))
