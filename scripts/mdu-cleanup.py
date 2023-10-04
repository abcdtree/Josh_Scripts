import os
import argparse
import subprocess

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def find_work_folders(root_path, temp_file):
	cmd = f"find {root_path} -name work | tee {temp_file}"
	print(f"**checking all the nextflow/work folder under {root_path}, this may take a long time~**")
	bash_command(cmd)
	print(f"**please check {temp_file} and del the works you would like to keep**")
	print(f"**please run `python3 mdu-cleanup.py -c {temp_file} --size 100M` to clean up")

def do_cleanup(path, size, bam):
	if bam:
		cmd = f"find {path} -name '*.bam' | tee large.file"
	else:
		cmd = f"find {path} -size +{size} | tee large.file"
	bash_command(cmd)
	with open("large.file", 'r') as mylarge:
		for line in mylarge:
			cmd = f"rm -f {line.strip()}"
			bash_command(cmd)
	bash_command("rm -f large.file")
	print(f"**Cleanning up on folder {path} has been done**")
	return


def clean_up_folders(temp_file, size, bam):
	path_list = []
	with open(temp_file, "r") as mytmp:
		for line in mytmp:
			path_list.append(line.strip())
	for mpath in path_list:
		do_cleanup(mpath, size, bam)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--find_folder_path","-f", help="mode to find work folders in the input path")
	parser.add_argument("--output_temp_file", '-o', default="temp.file", help="a text file to save the work path that found")
	parser.add_argument("--clean", '-c', default="temp.file", help="The file contains work folder to clean up")
	parser.add_argument("--size", choices=["100M", "250M", "500M", "1G"], default="100M", help="size of large file to delete")
	parser.add_argument("--bam", action="store_true", help="remove bam file only")
	args = parser.parse_args()

	if args.find_folder_path:
		find_work_folders(args.find_folder_path, args.output_temp_file)
	else:
		clean_up_folders(args.clean, args.size, args.bam)

if __name__ == "__main__":
	main()
