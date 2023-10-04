import os
import subprocess

def check_output(cmd):
	output = subprocess.run(cmd.split(" "), capture_output=True, text=True)
	return output.stdout.strip()

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

with open("ids.tab", 'r') as mytab:
    for line in mytab:
        info = line.strip().split("\t")
        if len(info) == 3:
            mdu_id, r1, r2 = info
            cmd = f"ska fastq -o {mdu_id} {r1} {r2}"
            bash_command(cmd)

#other command
cmd = "ls *.skf > ska_file_names.txt"
bash_command(cmd)

cmd = "ska merge -f ska_file_names.txt"
bash_command(cmd)

cmd = "ska distance -o all_VRE_distances -s 5 -S merged.skf"
bash_command(cmd)

print("ska analysis is done")
