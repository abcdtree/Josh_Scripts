import pandas,pathlib,sys,subprocess

tdy = sys.argv[1]

header = f"""# STm Vic surveillance results

## Date analysed: {tdy}

## Author: Josh Zhang
"""
print(header)

url_stub = f"https://bioinformatics.mdu.unimelb.edu.au/~jianszhang/MDU/Salmonella/Stm_Vic_reports/{tdy}/"

intro = f"""

Core genome phylogeny of cgT groups of interest was performed using LT2 starin complete genome as reference (accession NC_003197.2).

SNP based clusters were defined by single-linkage clustering at 1,2,5,10 and 20 SNP thresholds. Note SNP cluster IDs are random and consistency between reports will not be maintained.

cgT table of all non-CIC Typhimurium in the 6 month rolling window can be found [here]({url_stub}cgmlst_{tdy}_typhimurium.csv)

Summary of new isolates added can be found [here]({url_stub}summary_new_{tdy}.csv)

Epi curve can be found [here]({url_stub}epi_{tdy}.html)

"""


with open(sys.argv[2],'r') as f:
    cgts = f.read().strip().split('\n')

results = []
target = f"/home/jianszhang/public_html/MDU/Salmonella/Stm_Vic_reports/{tdy}/"
subprocess.run(f"mkdir -p {target}", shell = True)
for cg in cgts:
    results.append(f"## cgT {cg}\n")
    results.append("\n")
    results.append(f"* [bohra]({url_stub}report_{cg}.html)\n")
    results.append(f"* [clusters]({url_stub}snp_clusters_{cg}.csv)\n")
    subprocess.run(f"cp {cg}/report/report.html {target}report_{cg}.html", shell = True)
    subprocess.run(f"cp snp_clusters_{cg}.csv {target}snp_clusters_{cg}.csv", shell = True)

subprocess.run(f"cp cgmlst_{tdy}_typhimurium.csv {target}cgmlst_{tdy}_typhimurium.csv", shell = True)
subprocess.run(f"cp summary_new_{sys.argv[3]}.csv {target}summary_new_{tdy}.csv", shell = True)
subprocess.run(f"cp epi_{tdy}.html {target}", shell = True)
res = '\n'.join(results)
pathlib.Path(f"{target}summary.md").write_text('\n'.join([header,intro,res]))
