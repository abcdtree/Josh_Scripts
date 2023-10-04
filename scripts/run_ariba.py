import os, subprocess, csv
def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def check_output(cmd):
	output = subprocess.run(cmd.split(" "), capture_output=True, text=True)
	return output.stderr.strip()

with open("ids.tab", 'r') as mtab:
    for line in mtab:
        mdu_id, r1, r2 = line.strip().split("\t")
        cmd = f"ariba run /home/mdu/pipelines/qc2/db/seroba/db/ariba_db/33A/ref {r1} {r2} {mdu_id}"
        bash_command(cmd)
