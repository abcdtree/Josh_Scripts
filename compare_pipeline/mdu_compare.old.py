import os
import argparse
import logging
import subprocess
import pandas as pd
import markdown
import sys
from datetime import date
import toytree
import toyplot
import getpass

#pipeline to handle Task that to compare whether A and B isolates are related
#if a ref is provided, there will be 6 bohra, if not, only 4 will be perform
#run 1: ref using input reference, without/with mask
#run 2: using A isolate's contigs as reference, without mask
#run 3: using A isolate's contigs as reference, with mask (phastaf)
#run 4: using B isolate's contigs as reference, without mask
#run 5: using B isolate's contigs as reference, with maks (phastaf)

def create_logger(logging, tool_name, level):
	"""
	A function to create a logger.
	"""
	logger = logging.getLogger(tool_name)

	# Create handlers
	handler = logging.StreamHandler()
	handler.setLevel(level)

	# Create formatters and add it to handlers
	logformat = logging.Formatter(
		'[%(name)s - %(asctime)s] %(levelname)s: %(message)s')
	handler.setFormatter(logformat)

	# Add handlers to the logger
	logger.addHandler(handler)
	logger.setLevel(level)

	return logger

logger = None

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

def check_bohra():
	version = check_output("bohra -v")
	try:
		v = int(version.split()[1].split(".")[0])
		if v == 1:
			return True
		logger.error(f"Wrong bohra version {version.strip()}")
		return False
	except:
		logger.error(f"Bohra is not installed or set up wrong")
		return False

def run_bohra(reference, mask, cpu, input_tab, job_id, b_type):
	if not check_bohra():
		logger.error("Could not find bohra, please check your environment")
		sys.exit()
	cmd = ""
	if mask == None:
		cmd = f"bohra run -c {cpu} -i {input_tab} -j {job_id} -r {reference}\
		 -p {b_type} -mdu -ma 0 -mc 0"
	else:
		cmd = f"bohra run -c {cpu} -i {input_tab} -j {job_id} -r {reference}\
		 -m {mask} -p {b_type} -mdu -ma 0 -mc 0"
	bash_command(cmd)
	return

def copy_contigs(c_path, mid):
	logger.info(f"Copying {c_path} to current path")
	cmd = f"cp {c_path} ./{mid}.contigs.fna"
	bash_command(cmd)
	return f"{mid}.contigs.fna"

def read_pair_file(pair_file):
	logger.info("Reading the pair file to get focus isolates")
	with open(pair_file, 'r') as mypair:
		focus_dict = {}
		for line in mypair:
			info = line.strip().split("\t")
			if len(info) < 1:
				logger.error("Pair file should contains focus sample MDUID at least")
				sys.exit()
			elif len(info) == 1:
				mid = info[0]
				contigs = check_output(f"mdu contigs -s {mid}").strip().split("\t")[-1]
				logger.info(f"find contigs at {contigs}")
				if contigs[:2] == "No":
					logger.error(f"Could not find contigs file for {mid}")
					sys.exit()
				focus_dict[mid] = copy_contigs(contigs, mid)
			elif len(info) == 2:
				mid = info[0]
				contigs = info[1]
				focus_dict[mid] = copy_contigs(contigs, mid)
	return focus_dict

def check_phastaf():
	cmd = "phastaf -v"
	line = check_output(cmd).strip()
	if line[:3] != "pha":
		logger.error("Could not find phastaf, please check the environment")
		sys.exit()
	return True

def delete_pre_phastaf_folder(mid):
	if os.path.exists(f"./{mid}"):
		cmd = f'rm -rf {mid}'
		bash_command(cmd)
	return

def get_mask(mid, contigs):
	check_phastaf()
	delete_pre_phastaf_folder(mid)
	cmd = f"phastaf {contigs} --outdir {mid} --cpus 4"
	logger.info(f"creating mask for {mid}")
	bash_command(cmd)
	if os.path.exists(f"./{mid}/phage.bed"):
		return f"./{mid}/phage.bed"
	else:
		return None

def perform_analysis(task_list, task_dict, args):
	for mtask in task_list:
		ref, mask, report_id = task_dict[mtask]
		logger.info(f"Bohra run {report_id} is started, it may take a while to finish")
		run_bohra(ref, mask, args.cpu, args.input, report_id, args.bohra)

def check_folder_name(mfile):
	if "input_reference_run" in mfile:
		return True
	elif "ref_only" in mfile:
		return True
	elif "with_mask" in mfile:
		return True
	else:
		return False
def copy_to_public(mfile, reportid):
	usr = getpass.getuser()
	html_file = f"./{mfile}/report/index.html"
	#create folder
	cmd = f"mkdir -p /home/{usr}/public_html/MDU/{reportid}"
	bash_command(cmd)
	cmd = f"mkdir -p /home/{usr}/public_html/MDU/{reportid}/{mfile}"
	bash_command(cmd)
	cmd = f"cp {html_file} /home/{usr}/public_html/MDU/{reportid}/{mfile}/index.html"
	bash_command(cmd)
	return f"https://bioinformatics.mdu.unimelb.edu.au/~{usr}/MDU/{reportid}/{mfile}"

def get_date():
	today = date.today()
	return today.strftime("%Y-%m-%d")

def get_email_address():
	usr = getpass.getuser()
	if os.path.exists(f"/home/{usr}/.forward"):
		with open(f"/home/{usr}/.forward",'r') as myforward:
			return myforward.readline().strip()
	else:
		return "josh.zhang@unimelb.edu.au"

def email_the_link(link, report_id):
	email_address = get_email_address()
	message = f'''
	MDU Compare Analysis -- {report_id}:\t{link}
	'''
	message_cmd = f"echo '{message}' | mail -s 'MDU Compare Analysis' {email_address}"
	bash_command(message_cmd)

def get_pan_info(pair_list):
	a, b = pair_list
	gene_present_file = f"./{a}_ref_only/roary/gene_presence_absence.csv"
	if os.path.exists(gene_present_file):
		pan_gene_df = pd.read_csv(gene_present_file)
		pan_summary_df = pan_gene_df[["Gene", "Annotation", a, b]]
		pan_dif_1 = pan_summary_df[pan_summary_df[a].isna() & ~pan_summary_df[b].isna()]
		a_p_not_b = pan_dif_1.Gene.count()
		pan_dif_2 = pan_summary_df[~pan_summary_df[a].isna() & pan_summary_df[b].isna()]
		b_p_not_a = pan_dif_2.Gene.count()
		summary_df = pan_dif_1.append(pan_dif_2)
		summary_df = summary_df.sort_values(by=[a, b])
		return (True, a_p_not_b, b_p_not_a, summary_df)
	else:
		return (False, None, None, None)

def get_accessory_tree(pair_list):
	a, b = pair_list
	accessory_tree = f"./{a}_ref_only/roary/accessory_binary_genes.fa.newick"
	with open(accessory_tree, 'r') as mytree:
		newick = mytree.readline().strip()
	tre0 = toytree.tree(newick, tree_format=0)
	colors = []
	nsize = []
	colormap = toyplot.color.brewer.map("Paired")
	for name in tre0.get_node_values('name', True, True):
		if name in pair_list:
			nsize.append(10)
			colors.append(colormap.colors([0])[0])
		else:
			nsize.append(0)
			colors.append(colormap.colors([1])[0])
	canvas, axes, mark = tre0.draw(height=500, node_hover=True, node_sizes=nsize, tip_labels_align=True, node_colors=colors)
	html_str = toyplot.html.tostring(canvas)
	return f"<h3>Accessory Binary Gene Tree:</h3>\n" + html_str

def create_html(total_df, link_dict, reportid, pair_list):
	usr = getpass.getuser()
	a, b = pair_list
	run_date = get_date()
	html_head = f'''
	<h1>{reportid}</h1>
	<h2>MDU Compare Job on {run_date}</h2>'''
	line = '\n<h3>bohra report links for runs:</h3>\n'
	line += "<ul>\n"
	for mrun in link_dict:
		mlink = link_dict[mrun]
		part = f' <li><a href="{mlink}">{mrun}</a></li>\n'
		line = line + part
	line = line + f'</ul>\n<h3>core genome and distance table:<h3>\n'
	#html_output = markdown.markdown(line)
	html_output = html_head + line + total_df.to_html(index=False, justify="center")
	#pan gene information
	pan_flag, a_count, b_count, pan_gene_df = get_pan_info(pair_list)
	if pan_flag:
		html_output += f'<h3>Number of genes present in {a} not {b}: {a_count}</h3>\n'
		html_output += f'<h3>Number of genes present in {b} not {a}: {b_count}</h3>\n'
		html_output += pan_gene_df.to_html(index=False, justify="center")
		html_output += get_accessory_tree(pair_list)
	html_file = open("./index.html", 'w')
	html_file.write(html_output)
	html_file.close()
	cmd = f"cp index.html /home/{usr}/public_html/MDU/{reportid}/index.html"
	bash_command(cmd)
	email_the_link(f"https://bioinformatics.mdu.unimelb.edu.au/~{usr}/MDU/{reportid}", reportid)

def summary_the_output(report_id, pair_list):
	logger.info("Summary all bohra runs")
	a, b = pair_list
	total_df = pd.DataFrame()
	link_dict = {}
	for mfile in os.listdir("./"):
		if check_folder_name(mfile):
			title = mfile
			distance_file = f"./{title}/report/distances.tab"
			core_genome = f"./{title}/report/core_genome.tab"
			#distance
			dis_df = pd.read_csv(distance_file, sep="\t")
			dis_df = dis_df[["snp-dists 0.6.3", a, b]]
			dis_df.columns = ["MDU_ID", a, b]
			dis_df = dis_df[dis_df["MDU_ID"].isin(pair_list)]
			#print(dis_df)
			#core_genome
			core_df = pd.read_csv(core_genome, sep="\t")
			core_df = core_df.rename(columns={"Isolate":"MDU_ID"}, inplace=False)
			#print(core_df)
			summary_df = core_df.merge(dis_df, how='inner', on='MDU_ID')
			#print(summary_df)
			summary_df["Bohra_Run"] = mfile
			if total_df.empty:
				total_df = summary_df.copy()
			else:
				total_df = total_df.append(summary_df)
			report_link = copy_to_public(mfile, report_id)
			link_dict[mfile] = report_link
	logger.info("Creating summary report and email it out")
	create_html(total_df, link_dict, report_id, pair_list)

def get_pair_id(pair_file):
	pair = []
	with open(pair_file, 'r') as myfile:
		for line in myfile:
			mid = line.strip().split("\t")[0]
			pair.append(mid)
	if len(pair) == 2:
		return pair
	else:
		logger.error("Error format in pair file, please check your input")
		sys.exit()

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--bohra", "-b", help="Model of Bohra Pipeline: preview, all, sa",\
						default="sa")
	parser.add_argument("--summary", action="store_true", help="run summary only on a finished compare run")
	parser.add_argument("--reportid", "-rp", help="Report ID to create publich html folder", default="compare_job")
	parser.add_argument("--cpu", "-c", help="Number of cpus to use (default as 16)", \
						default="48")
	parser.add_argument("--reference", "-r", help="Selected reference to run bohra")
	parser.add_argument("--mask", "-m", help="mask file corresponding to reference")
	parser.add_argument("--input", "-i", help="Input table file contains MDUID, R1, R2")
	parser.add_argument("--pair", "-p", help="A txt file contains the focus pair, with/without contigs file path")
	args = parser.parse_args()
	global logger
	logger = create_logger(logging, "mdu-compare", logging.INFO)
	logger.info("Welcome to MDU-COMPARE")
	logger.info("Checking inputs")
	try:
		my_cpu = int(args.cpu)
		if my_cpu < 0 or my_cpu >= 200:
			logger.error("CPU number was invalid, please choose number from 1 to 200")
			sys.exit()
	except:
		logger.error("CPU number was invalid, please choose number from 1 to 200")
		sys.exit()
	if not args.input or not os.path.exists(args.input):
		logger.error("Could not find input tab file")
		sys.exit()
	if not args.pair or not os.path.exists(args.pair):
		logger.error("Could not find focus pair input file")
		sys.exit()
	pair_list = get_pair_id(args.pair)
	if args.summary:
		summary_the_output(args.reportid, pair_list)
	else:
		task_dict = {}
		task_list = []
		if args.reference:
			reference_file = args.reference
			mask = args.mask
			report_id = "input_reference_run"
			task_dict[report_id] = [reference_file, mask, report_id]
			task_list.append(report_id)
		focus_dict = read_pair_file(args.pair)
		for mid in focus_dict:
			reference_file = focus_dict[mid]
			mask = None
			report_id = f"{mid}_ref_only"
			task_dict[report_id] = [reference_file, mask, report_id]
			task_list.append(report_id)
			report_id = f"{mid}_with_mask"
			mask = get_mask(mid, reference_file)
			if mask != None:
				task_dict[report_id] = [reference_file, mask, report_id]
				task_list.append(report_id)
		logger.info("Preparation is done, bohra analysis is going to start")
		perform_analysis(task_list, task_dict, args)
		summary_the_output(args.reportid, pair_list)
	#print(task_dict)

if __name__ == "__main__":
	main()
