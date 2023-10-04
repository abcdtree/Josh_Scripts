import os
import subprocess

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

for mfasta in os.listdir("./new_samples"):
	if mfasta[-5:] == "fasta":
		mfilename = mfasta.split(".")[0]
		cmd = f"mkdir -p {mfilename}"
		bash_command(cmd)
		cmd = f"cp ./new_samples/{mfasta} {mfilename}/"
		bash_command(cmd)
