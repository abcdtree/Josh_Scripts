import pandas,numpy
import altair as alt
alt.data_transformers.disable_max_rows()
import toytree, toyplot
import toyplot.svg
import toyplot.png
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import os
import sys
import subprocess

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return


def ck_files():
	#checking sharepoint file
	if not os.path.exists("TBsharepoint.xlsx"):
		print("Please upload TBsharepoint.xlsx, process terminated")
		sys.exit()
	if not os.path.exists("new_isolates.txt"):
		print("Please create new_isoaltes.txt, process terminated")
		sys.exit()

ck_files()
report_date = "2023-10-03"
report_folder = "/home/jianszhang/mdu_jobs/cleptr_db"
analysis_folder = "/home/jianszhang/analysis/tb_dev"
# 1. get sharepoint and extract new sequences
sharepoint = pandas.read_excel('TBsharepoint.xlsx')

sharepoint['PHESS ID'] = sharepoint['PHESS ID'].apply(lambda x:int(x) if f"{x}" != 'nan' else '')
sharepoint['Specimen collection date'] = sharepoint['Specimen collection date'].apply(lambda x: str(x).strip('*'))
sharepoint['DOB'] = sharepoint['DOB'].apply(lambda x: str(x).strip('* '))
sharepoint['Collection date'] = pandas.to_datetime(sharepoint['Specimen collection date'], dayfirst = True)
sharepoint['DOB']=pandas.to_datetime(sharepoint['DOB'])
sharepoint = sharepoint.rename(columns = {'MDU ID': 'Seq_ID'})

metainfo = pandas.read_excel("tb_metadata.xlsx")
sharepoint = sharepoint.merge(metainfo, how='left', on="PHESS ID")
#sharepoint
# 2. get new isolates
#add read new batch##
#new_batch = ['2022-23', "2022-24"]
#new_isos = list(sharepoint[sharepoint['Batch #'].isin(new_batch)]['Seq_ID'])
new_isos = []
with open("new_isolates.txt", 'r') as mynew:
	for line in mynew:
		mid = line.strip()
		if len(mid) > 0:
			new_isos.append(mid)
print(f"There are {len(new_isos)} new isolates in this report")
lins = pandas.read_csv(f'{analysis_folder}/lineage_checked.csv')
#print("error Here?")
#print(lins.head())
tab = sharepoint.merge(lins, how = 'left')
tab.to_csv("epi.csv",index=None)
tab = tab[~tab['Seq_ID'].isna()]
for_epi = tab[~tab['Species'].isna()]
for_epi = for_epi[(for_epi['Collection date'] > '2017-01-01') &(for_epi['pass_lineage'] == 'pass') & (~for_epi['Phylogenetic lineage'].str.contains('La'))]
inside_collection_day_list = for_epi.Seq_ID.tolist()
mltd = for_epi.groupby([pandas.Grouper(key="Collection date", freq="1M"), "Phylogenetic lineage"]).agg('count').reset_index()
mltd_test = for_epi.groupby([pandas.Grouper(key="Collection date", freq="1M"), "Seq_ID"]).agg('count').reset_index()
mltd_test.to_csv("error_count.csv", index=None)
mltd.to_csv("epi_count.csv",index=None)
# 6. draw epicurve
_r = ["#fcba03","#9771b0","#69aed6","#c95975","#74d669","#d6851c","#42f5c8"]
_d = ["Lineage 1", 'Lineage 2', 'Lineage 3','Lineage 4','Lineage 5','Lineage 6', 'Lineage 9']

epi_chart = alt.Chart(mltd).mark_bar().encode(
	x=alt.X('yearmonth(Collection date)', title = 'Collection date', axis = alt.Axis(labelAngle = -90)),
	y=alt.Y('Seq_ID', title = 'Count'),
	color=alt.Color('Phylogenetic lineage',scale=alt.Scale(domain=_d, range=_r))
).properties(
	width=700,
	height=300
)
print("try to save the plot")
epi_chart.save("epi.html")
#epi_chart.save("epi.svg")
#epi_chart.save("epi.png")
#drawing = svg2rlg(f"epi.svg")
#renderPM.drawToFile(drawing, f"epi.png", fmt="PNG")
# make summary table
# 1. concat all snp-cluster tables
ct = None
count = 0
#for lin in ['1','2','3','4', '5']:
for lin in ['1', '2', '3', '4']:
	if count == 0:
		ct = pandas.read_csv(f"{report_folder}/Lineage_{lin}/lineage_{lin}.{report_date}.csv")
	else:
		ct = pandas.concat([ct, pandas.read_csv(f"{report_folder}/Lineage_{lin}/lineage_{lin}.{report_date}.csv")])
	print(f"loading {lin} Lineage")
	count += 1
ct = ct.rename(columns = {'ID':'Seq_ID'})
#ct.to_csv("test.csv")

# change subcluster name from large number to 1,2,3 ... PR
m_ids = []
cluster_dict = {}
id_info = []
title = ["Seq_ID","Cluster_poss","Cluster_highly","Cluster_ID"]
uncluster_list = []
for index, row in ct.iterrows():
	m_id = row["Seq_ID"]
	cluster = row["Cluster_poss"]
	sub_cluster = row["Cluster_highly"]
	m_ids.append(m_id)
	if cluster == "UC":
		id_info.append([m_id, cluster, sub_cluster, row["Cluster_ID"]])
		uncluster_list.append(m_id)
	elif sub_cluster == "UC":
		id_info.append([m_id, cluster, "PR", f"Clst-{cluster}-PR"])
	else:
		sub_dict = cluster_dict.get(cluster, {})
		new_name = sub_dict.get(sub_cluster, "x")
		if new_name == "x":
			names = list(sub_dict.values())
			#print(names)
			if len(names) == 0:
				new_name = "1"
			else:
				print(names)
				names.sort()
				new_name = str(int(names[-1]) + 1)
			sub_dict[sub_cluster] = new_name
		cluster_dict[cluster] = sub_dict
		id_info.append([m_id, cluster, new_name, f"Clst-{cluster}-{new_name}"])

new_ct = pandas.DataFrame(id_info, columns=title)
#new_ct.to_csv("test2.csv")
# 2. merge with tab
ct = new_ct.copy()
tab = tab.merge(ct, how = 'left')
tab = tab[['Seq_ID','PHESS ID','VIDRL Lab No.', 'Surname 2x','First Name 2x', 'DOB','Gender','Collection date','Species','Phylogenetic lineage','Cluster_poss','Cluster_highly' ,'Cluster_ID', "MANIFESTATION", \
"CALCULATED_DATE_OF_ONSET", "COUNTRY_OF_BIRTH", "YEAR_OF_ARRIVAL", "LGA", "ASSIGNED_TO"]]
# tab = tab.fillna('')
tab['Report_date'] = report_date
# tab[tab['Cluster_possible'] == '575']
#print("try to save report??")
tab.to_csv(f'cluster_report_{report_date}.csv', index = False)
# 3. sub out new
new_tab = tab[tab['Seq_ID'].isin(new_isos)]
new_tab = new_tab[['Seq_ID','PHESS ID','Phylogenetic lineage','Cluster_poss','Cluster_highly','Cluster_ID']]
new_tab = new_tab.rename(columns = {'Seq_ID':'MDU ID', "Cluster_ID":"Cluster ID"})
# new_tab['Cluster ID'] = new_tab['Cluster ID'].apply(lambda x:x.replace('UC',''))
#print(new_tab.head())
#new_tab[['MDU ID','PHESS ID','Phylogenetic lineage','Cluster ID']].to_csv('new_summary_table.csv', index = False)

#new_tab = new_tab.append(tab[(tab['Cluster_ID'].str.contains('574')) &(~tab['Cluster_ID'].isna())])
new_tab['MDU ID'] = numpy.where(new_tab['MDU ID'].isna(), new_tab['MDU ID'], new_tab['MDU ID'])
new_tab['Cluster ID'] = numpy.where(new_tab['Cluster ID'].isna(), new_tab['Cluster ID'], new_tab['Cluster ID'])
new_tab = new_tab.drop_duplicates(subset = ['MDU ID'])
new_tab[['MDU ID','PHESS ID','Phylogenetic lineage','Cluster ID']].to_csv('new_summary_table.csv', index = False)
# get clusters

#create table for uncluster samples

un_cluster_df = tab[tab['Seq_ID'].isin(uncluster_list)]
un_cluster_df = un_cluster_df[un_cluster_df['Seq_ID'].isin(new_isos)]
un_cluster_df = un_cluster_df.rename(columns = {"Seq_ID":"MDU ID","Cluster_ID":"Cluster ID"})
uncluster_table = un_cluster_df[['MDU ID','PHESS ID','VIDRL Lab No.', 'Surname 2x','First Name 2x', 'DOB','Gender','Collection date', \
"MANIFESTATION","CALCULATED_DATE_OF_ONSET", "COUNTRY_OF_BIRTH", "YEAR_OF_ARRIVAL", "LGA", "ASSIGNED_TO"]]
uncluster_table.to_csv("Uncluster_summary.csv", index=False)


for u in new_tab['Cluster_poss'].unique():
	if u != 'UC':
		d = tab[tab['Cluster_poss'] == u]

		ln = list(d['Phylogenetic lineage'].unique())
		for l in ln:
			#print(l)
			#print(u)
#             print(d)
			sub_ln = f"Lineage_{l.split()[-1]}"
			x = d.rename(columns = {"Seq_ID":"MDU ID","Cluster_ID":"Cluster ID"})
			x = x[x['Phylogenetic lineage'] == l]
			#print(x)
			seqs = list(x['MDU ID'].unique())
	#         epi table
			for_table_epi = x[['MDU ID','PHESS ID','VIDRL Lab No.', 'Surname 2x','First Name 2x', 'DOB','Gender','Collection date',"Cluster ID",\
			"MANIFESTATION","CALCULATED_DATE_OF_ONSET", "COUNTRY_OF_BIRTH", "YEAR_OF_ARRIVAL", "LGA", "ASSIGNED_TO"]]
			for_table_epi.to_csv(f"{sub_ln}_{u}.csv",index = False)
	#         snp table
			ds = pandas.read_csv(f"{analysis_folder}/{sub_ln}/report/distances.tab",sep = '\t')
			new_seqs = []
			for sk in seqs:
				if sk in inside_collection_day_list:
					if sk != "2021-157374":
						new_seqs.append(sk)
			seqs = new_seqs
			print("#", new_seqs)
			cols = ['Isolate']
			cols.extend(seqs)
			cls_ds = ds[ds['Isolate'].isin(seqs)][cols]
			#cls_cp = ds[ds['Isolate'].isin(seqs)]
			#cls_ds = cls_cp[["Isolate"]]
			#cls_ds.to_csv("temp_csv")
			##
			mlt_cls = pandas.melt(cls_ds, id_vars = 'Isolate', value_vars = seqs)
			mlt_cls = mlt_cls[mlt_cls['Isolate'] != mlt_cls['variable']]
			mlt_cls['ids'] = mlt_cls[['Isolate','variable']].apply(lambda x: '_'.join(sorted(list(set(x)))), axis = 1)
			mlt_cls = mlt_cls.drop_duplicates(subset = ["ids"])
			smm = mlt_cls.describe().T
			smm = smm.rename(columns = {'count':'Count','min':'Min distance', "25%":"25th percentile","50%":"50th percentile (median)" , "75%" :"75th percentile" ,"max":"Max distance"})
			smm['Count'] = len(seqs)
			bg_ds = pandas.melt(ds, id_vars = 'Isolate', value_vars = seqs)
			bg_ds = bg_ds[(bg_ds['Isolate'] != bg_ds['variable']) & (bg_ds['Isolate'] != "Reference") & (bg_ds['Isolate'] != "variable") ]
			bg_ds = bg_ds[~bg_ds['Isolate'].isin(seqs)]
			#if u == "1":
				#bg_ds.to_csv("1_table.csv")
			min_uc = bg_ds.describe().T['min'].values[0]
			med_uc = bg_ds.describe().T['50%'].values[0]
			smm['Distance to unclustered (min)'] = min_uc
			smm['Distance to unclustered (median)'] = med_uc
			smm = smm[['Count','Min distance', "25th percentile","50th percentile (median)","75th percentile","Max distance",'Distance to unclustered (min)','Distance to unclustered (median)']]
			smm.to_csv(f"{sub_ln}_{u}_dist_summary.csv", index = False)
#             cluster table
			if len(seqs) >2:
				mltd = x.groupby([pandas.Grouper(key="Collection date", freq="1M"), "Cluster_highly"]).agg('count').reset_index()
				m = len(list(mltd['MDU ID'].unique()))
				print(mltd)

#                 Code for timeline figures
				chart = alt.Chart(mltd[mltd['Cluster_highly'] != 'UC']).mark_line().encode(
					x=alt.X('yearmonth(Collection date)', title = 'Collection date', axis = alt.Axis(labelAngle = -90)),
		#             size=alt.Size('Seq_ID', legend = None),
					y = alt.Y('Cluster_highly', title = ""),
					color=alt.Color('Cluster_highly',legend=alt.Legend(title="Highly related"))
				).properties(
					width=700,
					height=300
				)
				chart += alt.Chart(mltd).mark_circle().encode(
					x=alt.X('yearmonth(Collection date)', title = 'Collection date', axis = alt.Axis(labelAngle = -90)),
					size=alt.Size('MDU ID:Q', legend=alt.Legend(title="Cases", tickCount = m)),
					y = alt.Y('Cluster_highly', title = ""),
					color=alt.Color('Cluster_highly')
				).properties(
					width=700,
					height=300
				)
				#chart.save(f"{u}_{l}.svg")
				chart.save(f"{u}_{l}.html")
				#drawing = svg2rlg(f"{u}_{l}.svg")
				#renderPM.drawToFile(drawing, f"{u}_{l}_history.png", fmt="PNG")
				#chart.save(f"{u}_{l}.png")
				#chart.save(f"{u}_lineage{l}.json")
				annotation_dict = {}
	#             cls =
				for i in list(x['MDU ID']):
					annotation_dict[i] = {'subcluster': x[x['MDU ID'] == i]['Cluster_highly'].values[0]}

#           Code for tree
				tree = toytree.tree(f"{analysis_folder}/{sub_ln}/report/core.newick")
				tree= tree.drop_tips([node for node in tree.get_tip_labels() if node not in seqs])
				TIP_DICT= {'1':"#4c78a8",'2':"#f58518",'3':"#e45756",'PR':"#84dae0", 'new':"#e33f22"} #colors need to be generalised - not hardcoded...
				for node in tree.treenode.traverse():
						if node.is_leaf():
							s = annotation_dict[node.name]['subcluster'] if node.name in annotation_dict else 428
							print(s)
							print(node.name)
							node.add_feature('color', TIP_DICT.get(s, "#a4a9b3"))
							node.add_feature('size', 10)
						else:
							node.add_feature('color', 'black')
							node.add_feature('size', 0)
				height = len(tree.get_tip_labels())
				# # store color list with values for tips and root
				colors = tree.get_node_values('color', show_root=1, show_tips=1)
				print(colors)
				sizes = tree.get_node_values('size', show_root=1, show_tips=1)
				# draw tree with node colors
				colorlist = [TIP_DICT['new'] if tip in new_isos else "#black" for tip in tree.get_tip_labels()]

				canvas = toyplot.Canvas(width =400, height = height*75)
				axes = canvas.cartesian()

				tree.draw(axes=axes, tip_labels=True,node_labels=False, node_colors=colors, node_sizes=sizes, edge_colors= 'black', edge_widths = 2, tip_labels_colors=colorlist, tip_labels_style={"font-size": "16px"})
				axes.show = False
				toyplot.svg.render(canvas, f"{u}_{l}_tree.svg")
				#toyplot.png.render(canvas, f"{u}_lineage{l}_tree.png")
				drawing = svg2rlg(f"{u}_{l}_tree.svg")
				renderPM.drawToFile(drawing, f"{u}_{l}_tree.png", fmt="PNG")
