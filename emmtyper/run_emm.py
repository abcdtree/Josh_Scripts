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

#emm_cl = "emmtyper -o emm.out.txt -f verbose"
cmd = "mkdir -p contigs"
bash_command(cmd)

with open("contigs.tab", 'r') as mycontigs:
    for line in mycontigs:
        mdu_id = line.strip().split("\t")[0]
        contigs = line.strip().split("\t")[-1]
        if len(contigs) > 0:
            os.symlink(contigs, f"./contigs/{mdu_id}.fa")
            #emm_cl.append(contigs)

#bash_command(emm_cl + " ./contigs/*.fa")
