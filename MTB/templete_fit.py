from docxtpl import DocxTemplate, InlineImage
from docx.shared import Cm
import toml
import logging
import pathlib
import os
import datetime
import pandas as pd

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('[%(levelname)s:%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
ch.setFormatter(formatter)
LOGGER.addHandler(ch)

DAY = datetime.datetime.today().strftime("%d/%m/%Y")

def initialise_report_dict(config, report_id):

    LOGGER.info(f"Checking that all required fields are present in config file")
    check_config(config = config)
    report_dict = {
        'report_title':config['report_title'],
        'primary_recipient': config['primary_recipient'],
        'report_id': report_id,
        'prepared_by': config['prepared_by'],
        'authorised_by': config['authorised_by'],
        'secondary_recipients': config['secondary_recipients'],
        'report_date': DAY
    }
    return report_dict

def file_present(path):

    if not pathlib.Path(path).exists():
        LOGGER.critical(f"It appears that {path} does not exist. Please check your inputs and trya again.")
        raise SystemExit
    else:
        return path

def open_config(config):

    cfg = file_present(config)
    return toml.load(open(cfg, 'r'))


def check_config(config):

    required_fields = ['report_title', 'primary_recipient', 'report_id', 'prepared_by', 'authorised_by', 'secondary_recipients']

    for r in required_fields:
        if r not in config:
            LOGGER.critical(f"{r} must be a field in your config file. Please check your inputs and try again.")
            raise SystemExit
        elif config[r] == '' and r != 'report_id':
            LOGGER.critical(f"The field {r} must have a value. Please check your inputs and try again.")
            raise SystemExit

    LOGGER.info(f"All required fields are present.")

def generate_docx_template(template_file):

    if pathlib.Path(template_file).exists():
        return DocxTemplate(template_file)
    else:
        LOGGER.critical(f"The template file does not exist. Please check your inputs and try again.")
        raise SystemExit

def write_template(output_name, data, template):
    LOGGER.info(f"Rendering document.")
    template.render(data)
    LOGGER.info(f"Saving output file: {output_name}")
    template.save(output_name)

def change_date_type(data_string):
    try:
        info =  data_string.split("-")
        return f"{info[2]}/{info[1]}/{info[0]}"
    except:
        return data_string

def lineage_summary_table_to_list(df):
    summary_list = []
    for index, row in df.iterrows():
        new_dict = {}
        new_dict["phess"] = row["PHESS ID"]
        new_dict["mdu"] = row["MDU ID"]
        new_dict["gender"] = row["Gender"]
        #new_dict["surname"] = row["Surname 2x"]
        #new_dict["firstname"] = row["First Name 2x"]
        new_dict["name"] = str(row["First Name 2x"]) + " " + str(row["Surname 2x"])
        new_dict["dob"] = change_date_type(row["DOB"])
        new_dict["collection"] = change_date_type(row["Collection date"])
        new_dict["extended"] = row["Cluster ID"]
        new_dict["manife"] = row["MANIFESTATION"]
        new_dict["dos"] = row["CALCULATED_DATE_OF_ONSET"]
        new_dict["country"] = row["COUNTRY_OF_BIRTH"]
        new_dict["arrival"] = row["YEAR_OF_ARRIVAL"]
        new_dict["LGA"] = row["LGA"]
        new_dict["assign"] = row["ASSIGNED_TO"]
        summary_list.append(new_dict)
    return summary_list

def uncluster_summary_table_to_list(df):
    summary_list = []
    for index, row in df.iterrows():
        new_dict = {}
        new_dict["phess"] = row["PHESS ID"]
        new_dict["mdu"] = row["MDU ID"]
        new_dict["gender"] = row["Gender"]
        #new_dict["surname"] = row["Surname 2x"]
        #new_dict["firstname"] = row["First Name 2x"]
        new_dict["name"] = str(row["First Name 2x"]) + " " + str(row["Surname 2x"])
        new_dict["dob"] = change_date_type(row["DOB"])
        new_dict["collection"] = change_date_type(row["Collection date"])
        new_dict["manife"] = row["MANIFESTATION"]
        new_dict["dos"] = row["CALCULATED_DATE_OF_ONSET"]
        new_dict["country"] = row["COUNTRY_OF_BIRTH"]
        new_dict["arrival"] = row["YEAR_OF_ARRIVAL"]
        new_dict["LGA"] = row["LGA"]
        new_dict["assign"] = row["ASSIGNED_TO"]
        #new_dict["extended"] = row["Cluster ID"]
        summary_list.append(new_dict)
    return summary_list

def dis_summary_table_to_list(df):
    distance_list = []
    for index, row in df.iterrows():
        new_dict = {}
        new_dict["n"] = row["Count"]
        new_dict["min"] = row["Min distance"]
        new_dict["max"] = row["Max distance"]
        new_dict["tntyfifth"] = row["25th percentile"]
        new_dict["median"] = row["50th percentile (median)"]
        new_dict["sytyfifth"] = row["75th percentile"]
        new_dict["unmin"] = row["Distance to unclustered (min)"]
        new_dict["unmed"] = row["Distance to unclustered (median)"]
        distance_list.append(new_dict)
    return distance_list


def get_versions():

    with open('../software_versions.tab', 'r') as f:
        versions = f.read().split('\n')
    return versions[1], versions[4]


def read_summary_table(summary_table):
    df = pd.read_csv(summary_table)
    summary_table = []
    change_in_report = []
    lineage_dict = {}
    following_list = set()
    #uncluster_list = []
    for index, row in df.iterrows():
        new_dict = {}
        new_dict['phess'] = row["PHESS ID"]
        new_dict["mdu"] = row["MDU ID"]
        new_dict['lineage'] = row["Phylogenetic lineage"]
        new_dict['cluster'] = row["Cluster ID"]
        if row["Cluster ID"] != "UC" and not pd.isnull(row["Cluster ID"]):
            lineage_id = row["Phylogenetic lineage"].split(" ")[-1]
            cluster_id = row["Cluster ID"].split("-")[1]
            following_list.add(lineage_id+"-"+cluster_id)
            cluster_dict = lineage_dict.get(lineage_id, {})
            iso_list = cluster_dict.get(cluster_id, [])
            iso_info = {}
            iso_info["id"] = row["MDU ID"]
            iso_info["c_id"] = row["Cluster ID"]
            iso_list.append(iso_info)
            cluster_dict[cluster_id] = iso_list
            lineage_dict[lineage_id] = cluster_dict
        summary_table.append(new_dict)

    following_new_list = list(map(lambda x: x.split("-"), list(following_list)))
    following_new_list.sort(key=lambda x: (x[0], x[1]))
    new_isolates_number = len(summary_table)


    for l in lineage_dict:
        new_dict = {}
        new_dict["Lineage"] = l
        clst_dict = lineage_dict[l]
        change_clst = []
        for c in clst_dict:
            new_c_dict = {}
            iso_list = clst_dict[c]
            new_c_dict["clst"] = c
            new_c_dict["isolates"] = iso_list
            change_clst.append(new_c_dict)
        new_dict["change_clst"] = change_clst
        change_in_report.append(new_dict)

    return new_isolates_number, summary_table, following_new_list, change_in_report

if __name__ == "__main__":
    report_id = "2023-18"
    config_path = "../tb_report.toml"
    config_dict = open_config(config_path)
    check_config(config_dict)
    report_dict = initialise_report_dict(config_dict, report_id)
    reference = 'Mycobacterium tuberculosis H37Rv, complete genome'
    snippy_version, iqtree_version = get_versions()
    report_dict['reference_name'] = reference
    report_dict['snippy_version'] = snippy_version
    report_dict['iqtree_version'] = iqtree_version
    template_file = "/home/jianszhang/mdu_jobs/MTB_reporting/tb_template.docx"
    template = generate_docx_template(template_file=template_file)

    new_isolates_number, summary_table, following_list, change_in_report = read_summary_table("./new_summary_table.csv")
    #print(summary_table)
    report_dict["new_isolates"] = str(new_isolates_number)
    report_dict["summary_table"] = summary_table

    cwd = os.getcwd()
    epi_png = str(os.path.join(cwd, "epi.png"))
    report_dict["victorian_epi"] = InlineImage(template, epi_png, Cm(12))

    pairs_for_report = []
    clusters_for_report = []
    cluster_change_id = []
    unclusters = []
    uncluster_file = "Uncluster_summary.csv"
    df_uncluster = pd.read_csv(uncluster_file)
    unclusters = uncluster_summary_table_to_list(df_uncluster)
    for lineage, cluster in following_list:
        summary_file = f"Lineage_{lineage}_{cluster}.csv"
        dist_file = f"Lineage_{lineage}_{cluster}_dist_summary.csv"
        df_sum = pd.read_csv(summary_file)
        df_dist = pd.read_csv(dist_file)
        summary_list = lineage_summary_table_to_list(df_sum)
        dist_list = dis_summary_table_to_list(df_dist)
        if len(summary_list) == 2:
            pairs_dict = {}
            pairs_dict["pairs_table"] = summary_list
            pairs_dict["distance_summary"] = dist_list
            pairs_for_report.append(pairs_dict)
        elif len(summary_list) > 2:
            clusters_dict = {}
            cluster_change_id.append(f"Clst-{cluster}")
            clusters_dict["isolates_table"] = summary_list
            clusters_dict["distance_summary"] = dist_list
            clusters_dict["name"] = f"Clst-{cluster}"
            clusters_dict["historyplot"] = InlineImage(template, os.path.join(cwd, f"Lineage_{lineage}_{cluster}_his.png"), Cm(10))
            clusters_dict["tree"] =  InlineImage(template, os.path.join(cwd, f"{cluster}_Lineage {lineage}_tree.png"), Cm(10))
            clusters_for_report.append(clusters_dict)
    number_of_new_pair = len(pairs_for_report)
    number_of_change_cluster = len(clusters_for_report)
    report_dict["pairs_for_report"] = pairs_for_report
    report_dict["clusters_for_report"] = clusters_for_report
    report_dict["unclusters"] = unclusters
    report_dict["new_add_to_cluster"] = str(number_of_change_cluster)
    report_dict["new_pairs"] = str(number_of_new_pair)
    if number_of_new_pair + number_of_change_cluster > 0:
        report_dict["change"] = "changes"
        report_dict["change_in_report"] = change_in_report
    else:
        report_dict["change"] = "no changes"
    if number_of_new_pair > 0:
        report_dict["pairs"] = "pairs"
    if number_of_change_cluster > 0:
        report_dict["clusters"] = "clusters"
    if len(unclusters) > 0:
        report_dict["uncluster_flag"] = "unclusters"

    print(report_dict)
    write_template(f"{report_id}_Mtb_surveillance.docx", report_dict, template)
