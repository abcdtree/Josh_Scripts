import os
import subprocess
import argparse
import sys

def check_conda_envs():
	try:
		my_env = os.environ["CONDA_PREFIX"]
		if "KMCP" in my_env:
			return True
		else:
			print("Please activea KMCP env: ca /home/jianszhang/conda/envs/KMCP")
			return False
	except:
		print("Please activea KMCP env: ca /home/jianszhang/conda/envs/KMCP")
		return False

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def run_kmcp(mid, r1, r2, db, taxidmap, taxdump, mode, processors):
    cmd1 = f"kmcp search -d {db} -1 {r1} -2 {r2} -o {mid}.tsv.gz -j {processors}"
    bash_command(cmd1)
    cmd2 = f"kmcp profile --taxid-map {taxidmap} --taxdump {taxdump} --level species -m {mode} {mid}.tsv.gz --out-file {mid}.profile"
    bash_command(cmd2)
    print(f"**kmcp profiling finished on sample {mid}**")
    cmd3 = f"mkdir -p {mid}"
    bash_command(cmd3)
    cmd4 = f"mv {mid}.* {mid}/"
    bash_command(cmd4)
    return

def run_kmcp_gtdb(mid, r1, r2, db, taxidmap, taxdump, mode, processors):
    #run kmcp search on part 1
    cmd1 = f"kmcp search -d {db} -1 {r1} -2 {r2} -o {mid}.part1.tsv.gz -j {processors}"
    bash_command(cmd1)
    cmd2 = f"kmcp search -d {db}2 -1 {r1} -2 {r2} -o {mid}.part2.tsv.gz -j {processors}"
    bash_command(cmd2)
    #merge search result
    cmd3 = f"kmcp merge {mid}.part*.tsv.gz --out-file {mid}.tsv.gz"
    bash_command(cmd3)
    cmd4 = f"kmcp profile --taxid-map {taxidmap} --taxdump {taxdump} --level species -m {mode} {mid}.tsv.gz --out-file {mid}.profile"
    bash_command(cmd4)
    print(f"**kmcp profiling finished on sample {mid}**")
    cmd5 = f"mkdir -p {mid}"
    bash_command(cmd5)
    cmd6 = f"mv {mid}.* {mid}/"
    bash_command(cmd6)
    return



db_dict = {
    "fungi":["/home/jianszhang/database/refseq-fungi.kmcp",
    "/home/jianszhang/database/refseq-fungi.kmcp/taxdump/taxid.map",
    "/home/jianszhang/database/refseq-fungi.kmcp/taxdump"],
    "gtdb":["/home/jianszhang/database/gtdb.kmcp",
    "/home/jianszhang/database/gtdb.kmcp/taxdump/taxid.map",
    "/home/jianszhang/database/gtdb.kmcp/taxdump"]
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--idfile", "-i", help="mdu reads tab file")
    parser.add_argument("--database", '-db', help="kcmp database name", default="fungi", choices=["fungi", "gtdb"])
    parser.add_argument("--mode", '-m', help="0 - 5, 0 for pathogen detection, 3 as default, 5 for highest precision", default="3")
    parser.add_argument("--process", "-p", help="number of processors to use", default=100)
    args = parser.parse_args()

    if check_conda_envs():
        db, taxidmap, taxdump = db_dict[args.database]
        if os.path.exists(args.idfile):
            with open(args.idfile, 'r') as myinput:
                for line in myinput:
                    if len(line.strip()) > 0:
                        try:
                            mid, r1, r2 = line.strip().split("\t")
                            if args.database == "fungi":
                                run_kmcp(mid, r1, r2, db, taxidmap, taxdump, args.mode, args.process)
                            elif args.database == "gtdb":
                                run_kmcp_gtdb(mid, r1, r2, db, taxidmap, taxdump, args.mode, args.process)
                            else:
                                print(f"{args.database} is not a valid database option")
                                sys.exit()
                        except:
                            print(f"Input tab file contains wrong formats")
                            print(line.strip())
                            continue
        else:
            print(f"Could not find {args.idfile}, please check your input")
            sys.exit(1)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
