#!/usr/bin/env python3
import sys,json, subprocess, pathlib, argparse,os, tempfile, logging, csv, pandas,re


# set up logger
LOGGER =logging.getLogger(__name__) 
LOGGER.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(levelname)s:%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') 
ch.setFormatter(formatter)
LOGGER.addHandler(ch) 
# variables for generating AT IDs and merging various covid data
EPI_HOME = f"/home/crachic/EPI/"
COUNTRIES = {
        'Fiji': 'FJ',
        'Kiribati':'KIR',
        'Papua New Guinea':'PNG',
        'Solomon Islands':'SOL',
        'Timor Leste':'TL',
        'Timor-Leste':'TL',
        'Vanuatu':'VAN',
        'Naru': 'NR',
        'Nauru':'NR'
        }

STATES = {
        'Northern Territory':'NT',
        'Tasmania':'TAS',
        'Victoria':'VIC',
        'New South Wales': 'NSW',
        'Western Australia': 'WA',
        'Queensland': 'QLD',
        'Australian Capital Territory': 'ACT',
        'South Australia': 'SA'
        }

OWNERS = {
    'Northern Territory':'RDH',
    'Tasmania':'RHH',
    'Victoria':'MDU',
    'Fiji': 'FJ',
    'Kiribati':'KIR',
    'Papua New Guinea':'PNG',
    'Solomon Islands':'SOL',
    'Timor Leste':'TL',
    'Timor-Leste':'TL',
    'Vanuatu':'VAN'
}

# variables for webhooks for kovid
HOOKS = {
    "kristy":"https://hooks.slack.com/services/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",
    "vic":"https://hooks.slack.com/services/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",
    "apac":"https://hooks.slack.com/services/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",
    "anz":"https://hooks.slack.com/services/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",
    "qc":"https://hooks.slack.com/services/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"
}
CHANNELS = {
    "Victoria": "vic",
    'Northern Territory':'anz',
    'Tasmania':'anz',
    'Fiji': 'apac',
    'Kiribati':'apac',
    'Papua New Guinea':'apac',
    'Solomon Islands':'apac',
    'Timor Leste':'apac',
    'Timor-Leste':'apac',
    'Vanuatu':'apac',
    'qc': 'qc'
}

def get_master(master):
    if master.exists():
        _dict = json.load(open(f"{master}", 'r'))
    else:
        _dict = {}
    return _dict

def generate_temp():

    LOGGER.info('Generating temp directory for isolate files.')
    p = subprocess.run("mktemp", shell = True, capture_output = True, encoding = 'utf-8')
    return p.stdout.strip()

def update_master(master_dict, jsons, master_file, runid):
    dr = generate_temp()
    for j in jsons:
        with open(j, 'r') as f:
            d = json.load(f)
           
            master_dict = {**master_dict, **d}
    
    json.dump(master_dict, open(f"{dr}/{master_file.name}", 'w'))
    return f"{dr}/{master_file.name}"

def change_permissions(data, reads, runid):

    for path in [data, reads]:
        if 'data' in path:
            user = 'khhor:domain^users'
        else:
            user = 'root:5266gg-hpc-mdudata'
        cmd = f"sudo chown -R {user} {path}/{runid}"
        LOGGER.info(f"Now running : {cmd}")
        subprocess.run(cmd,shell = True)

def _run_cmd(cmd):

    LOGGER.info(f"Now running: {cmd}")
    subprocess.run(cmd, shell = True)


def clean_up(tmp_master):

    LOGGER.info(f"Cleaning up temp file.")
    subprocess.run(f"rm -rf {tmp_master}")


def move_master(tmp_master, master):

    run_cmd(f"sudo mv {tmp_master} {master}")
    run_cmd(f"sudo chown root:5266gg-hpc-mdudata {master}")
    

def get_current_jsons(data, runid):
    p = pathlib.Path(data, runid)
    jsons = sorted(p.glob("*/current.json"))
    # print(jsons)
    return jsons

def _check_data(data):

    if pathlib.Path(data).exists():
        return True
    else:
        return False

def _check_reads(reads):

    for r in reads:
        if not pathlib.Path(r).exists():
            return False
    return True

def check_files(jsons):

    for j in jsons:
        with open(j, 'r') as f:
            _dict = json.load(f)
            if not _check_reads(_dict[list(_dict.keys())[0]]['sequence_data']['Read_path']) or not _check_data(_dict[list(_dict.keys())[0]]['sequence_data']['Data_path']):
                return False
            else:
                LOGGER.info(f"All files for {list(_dict.keys())[0]} are present and accounted for!!")
    return True

def _update_dbs(runid):
    cmd = f"mdu update -r {runid}"
    LOGGER.info(f"Updating all DBs for RUN : {runid}")
    subprocess.run(cmd, shell = True)

def _check_for_data_duplication(sars_db, results):

    to_add = []
    seq_ids = []
    with open(sars_db, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            seq_ids.append(row['Seq_ID'])
    for r in results:
        i = r['Seq_ID']
        if i not in seq_ids:
            to_add.append(r)
            LOGGER.info(f"Will add {i}")

    
    return to_add


def guess_category(_id):

    mdu_pattern = re.compile('(\d{4}-\d{5,6}-?\d*)')
    match = re.search(mdu_pattern, _id)
    if 'QAP' in _id:
        return 'QAP'
    elif 'PTP' in _id:
        return 'PTP'
    elif _id.startswith('PTC'):
        return 'PTC'
    elif _id.startswith('NTC'):
        return 'NTC'
    elif match:
        return 'SEQ'
    elif 'DMG' in _id or 'RES' in _id:
        return 'DAMG'
    else:
        return 'UNK'

def guess_tech(tech):

    if 'Ill' in tech:
        return 'ILL'
    else:
        return 'ONT'

def _clean_qc(tmp_isos, sars_db):

    cmd = f"csvtk grep -v -f 'Seq_ID' -P {tmp_isos} {sars_db}.backup > {sars_db}"
    # print(cmd)
    _run_cmd(cmd)

def _clean_consensus(tmp_isos, master_consensus):

    cmd = f"seqkit grep -v -f {tmp_isos} {master_consensus}.backup > {master_consensus}"
    _run_cmd(cmd)

def _update_sars_db(jsons, sars_db, runid):
    
    LOGGER.info(f"Getting lineage family info.")
    # f"{os.getenv('BLAST_DB', '')}"
    with open(f"{os.getenv('SARS_HOME')}/lin_fam.json", 'r') as j:
        fams = json.load(j)
    LOGGER.info(f"Extracting SARS-CoV-2 samples")
    
    results = [] # data for qc2 update
    isolates = [] # for cleaning up of db and consensus etc
    tech = set()
    for j in jsons:
        with open(j, 'r') as f:
            try:
                _dict = json.load(f)
                if 'Species_exp' in _dict[list(_dict.keys())[0]]['sequence_data'] and 'TC' not in list(_dict.keys())[0]:
                    if _dict[list(_dict.keys())[0]]['sequence_data']['Species_exp'] == 'SARS-CoV-2':
                        s = {list(_dict.keys())[0]: _dict[list(_dict.keys())[0]]}
                        mdu_id = list(_dict.keys())[0]
                        isolates.append(mdu_id) # add sequence for cleaning
                        lin = fams[s[mdu_id]['sequence_data']["Pangolin_lineage"]]['Lineage_family'] if s[mdu_id]['sequence_data']["Pangolin_lineage"] in fams else ''
                        mdu_stem = '-'.join(mdu_id.split('-')[:2])
                        seq_model = guess_tech(f"\"{s[mdu_id]['sequence_data']['Sequencer_Model']}\"") if "Sequencer_Model" in s[mdu_id]['sequence_data'] else guess_tech(f"\"{s[mdu_id]['sequence_data']['Sequencer_model']}\"")
                        _d = {"Seq_ID":mdu_id,
                                "Sample_ID":mdu_stem,
                                "Seq_QC":s[mdu_id]['sequence_data']['TEST_QC'],
                                "Coverage": s[mdu_id]['sequence_data']["Coverage"], 
                                "Genome_Het":s[mdu_id]['sequence_data']["HET"], 
                                "Genome_WH1_Dist":"" if "Dist_Wuhan_1" not in s[mdu_id]['sequence_data'] else s[mdu_id]['sequence_data']["Dist_Wuhan_1"],
                                "Lineage_orig":s[mdu_id]['sequence_data']["Pangolin_lineage"],
                                # "Lineage_note":s[mdu_id]['sequence_data']["note"],
                                # "Scorpio":s[mdu_id]['sequence_data']["scorpio_call"],
                                "Date_sequenced":s[mdu_id]['sequence_data']["Date_sequenced"],
                                "Seq_barcode":s[mdu_id]['sequence_data']['Sequencer_Barcode'] if "Sequencer_Barcode" in s[mdu_id]['sequence_data'] else s[mdu_id]['sequence_data']["Sequencer_barcode"],
                                "Seq_tech":seq_model,
                                "Seq_protocol":"" if "Seq_protocol" not in s[mdu_id]['sequence_data'] else s[mdu_id]['sequence_data']["Seq_protocol"],
                                "Assembly_methods":"" if "Assembly_methods" not in s[mdu_id]['sequence_data'] else  f"{s[mdu_id]['sequence_data']['Assembly_methods']}",
                                "Seq_run":runid,
                                "Seq_category":guess_category(mdu_id),
                                "Seq_by":'MDU' if s[mdu_id]['sequence_data']["Sequence_source"] == 'internal' else 'UNK', 
                                "Seq_owner": 'MDU',
                                "Species_expected":s[mdu_id]['sequence_data']['Species_exp'], 
                                "Seq_instrument": s[mdu_id]['sequence_data']['Sequencer_model'],
                                "voc_status_mdu": s[mdu_id]['sequence_data']['VOC_STATUS'],
                                # "Lineage_family": fams[s[mdu_id]['sequence_data']["Pangolin_lineage"]]['Lineage_family'] if s[mdu_id]['sequence_data']["Pangolin_lineage"] in fams else ''
                                }
                        
                        results.append(_d)
                        tech.add(seq_model)
            except:
                LOGGER.info(f"An error occured opening the file {j}")
    tech_return = 'ONT' if 'ONT' in list(tech) else list(tech)[0]
    if results != []:
        tmp_isos = generate_temp()
        pathlib.Path(tmp_isos).write_text('\n'.join(isolates)) # write isolates to tmp file for removal from consensus and db.
        LOGGER.info(f"Getting SARS-CoV-2 QC db")
        LOGGER.info(f"Cleaning QC db")
        _clean_qc(tmp_isos = tmp_isos, sars_db = sars_db)
        LOGGER.info(f"Checking for data duplication.")
        to_add = _check_for_data_duplication(sars_db, results)
        with open(sars_db, 'a') as f:
            LOGGER.info(f"Updating SARS-CoV-2 QC db")
            tb = pandas.read_csv(sars_db)
            tb = tb.append(results)
            tb.to_csv(sars_db, index = False)
        LOGGER.info(f"SARS-CoV-2 QC db updated at {sars_db}")
        LOGGER.info(f"Writing backup {sars_db}.backup")
        _run_cmd(f"cp {sars_db} {sars_db}.backup")
        return tmp_isos,tech_return
    else:
        LOGGER.info(f"No SARS-CoV-2 samples found.")
        return False
        
def _update_consensus(path_to_isos,runid, master_consensus, data_dir, sars_db):

    LOGGER.info(f"Cleaning consensus")
    _clean_consensus(path_to_isos, master_consensus)
    LOGGER.info(f"Appending to: {master_consensus}")
    _cns = sorted(pathlib.Path(data_dir,runid).glob(f"20*/consensus/current/cns.fa"))
    print(_cns)
    if _cns != []:
        for c in _cns:
            cmd = f"cat {c} >> {master_consensus}"
            _run_cmd(cmd)
            
        LOGGER.info(f"Backing up consensus ")
        _run_cmd(f"cp {master_consensus} {master_consensus}.backup")
    else:
        LOGGER.critical(f"Something went wrong updating {master_consensus}. Please try again.")
        raise SystemExit


def link_files(data_dir, runid):
    
    LOGGER.info(f"Linking current analysis outputs to sample directories.")
    p = pathlib.Path(data_dir, runid)
    for sample in p.iterdir():
        if sample.is_dir():
            if not sample.name.startswith('NTC'):
                sample_dir = pathlib.Path(sample) # get the sample directory - this is where things will be linked to.
                LOGGER.info(f"Working on {sample_dir}")
                for tests in sample_dir.iterdir():
                    if tests.is_dir():
                        if 'consensus' == tests.name:
                            target = f"{tests.name}/current/cns.fa"
                            cmd = f"cd {sample_dir} && sudo ln -sf {target} cns.fa"
                            LOGGER.info(f"Linking {target} to {sample_dir.name} : {cmd}")
                            subprocess.run(cmd, shell = True)
                        # elif 'species' in tests.name:

                        elif 'voc' not in tests.name:
                            print(tests)
                            td = pathlib.Path(tests)
                            jsn = sorted(td.rglob(f'{tests.name}*.json'))
                            if jsn != []:
                                jsn = jsn[0]
                                _dict = json.load(open(jsn, 'r'))
                                if 'filename' in _dict[_dict['current']]:
                                    fn = _dict[_dict['current']]['filename']
                                
                                    for f in fn:
                                        if f == 'shovill.fa':
                                            x = 'contigs.fa'
                                        elif f == 'spades.fa':
                                            x = 'contigs.fasta'
                                        else:
                                            x = f"{f}"
                                        target = f"{td.name}/current/{x}"
                                        cmd = f"cd {sample_dir} && sudo -u khhor ln -sf {target} {f}"
                                        LOGGER.info(f"Linking {target} to {sample_dir.name} : {cmd}")
                                        subprocess.run(cmd, shell = True)

def get_max_id(ids):
    pat = re.compile('[0-9]*$')
    ids_list = []
    for i in ids:
        if i != '':
            x = re.search(pat,i)
            num = x.group(0)
            ids_list.append(int(num))
    mx = max(ids_list) if ids_list != [] else 1
    return mx

def increment_id(mx):
    return mx + 1

def subset_db(df, col, _dict):
    
    tab = df
    for val in _dict:

        subd = tab[tab[col] == val]
        subd_to_add = subd[(~subd['Seq_category'].isin(['PTC', 'NTC'])) & (subd['AT_ID'] == '')]
        if not subd_to_add.empty:
            mx = get_max_id(list(subd['AT_ID']))
            for row in subd_to_add.iterrows():
                _id = row[1]['Seq_ID']
                mx = increment_id(mx)
                vid = f"{_dict[val]}{mx}"
                
                tab.loc[df['Seq_ID'] == _id, 'AT_ID'] = vid
                
    return tab

def get_owner(x):

    if x[0] in OWNERS:
        return OWNERS[x[0]]
    elif x[1] in OWNERS:
        return OWNERS[x[1]]
    else:
        return "MDU"

def _update_pango():

    LOGGER.info(f"Updating pangolin lineage and lineage family.")
    cmd = f"kovid-pangolin.pl -p pangolin -j 250 {os.environ.get('SARS_HOME')}/mdu.ffn > {os.environ.get('SARS_HOME')}"
    LOGGER.info(f"Updating pangolin lineage and lineage family. Running: {cmd}")
    p = subprocess.run(cmd, shell = True)
    if p.returncode == 0:
        cmd_2 = f"csvtk join --left-join -f 'lineage;Lineage' {os.environ.get('SARS_HOME')}/lineage_report.csv {os.environ.get('KOVID_HOME')}/refs/VOC-VUI-VOI_latest.csv | csvtk cut -f 'taxon,lineage,note,scorpio_call,Lineage_family' | csvtk rename -f 'taxon,lineage,note,scorpio_call' -n 'Seq_ID,Lineage,Lineage_note,Scorpio' > {os.environ.get('SARS_HOME')}/updated_lineage_report.csv"
        LOGGER.info(f"Pangolin update ran successfully, now adding in Lineage family. Running : {cmd_2}")
        prc = subprocess.run(cmd_2, shell= True)
        if prc.returncode == 0:
            cmd_3 = f"csvtk join --left-join -f 'Seq_ID;Seq_ID' {os.environ.get('SARS_HOME')}/QC2.csv.backup {os.environ.get('SARS_HOME')}/updated_lineage_report.csv > {os.environ.get('SARS_HOME')}/QC2.csv.tmp"
            prc = subprocess.run(cmd_3, shell= True)

def _update_at():

    qc = pandas.read_csv(f"{os.environ.get('SARS_HOME')}/QC2.csv", dtype = str)
    print(qc.shape)
    try:
        LOGGER.info(f"utf-8 encoding - no problems here.")
        db = pandas.read_csv(f"{os.environ.get('SARS_HOME')}/DB-ids.csv", dtype = str)
    except UnicodeDecodeError:
        LOGGER.info(f"There was a unicode error, trying to use 'latin-1' encoding.")
        db = pandas.read_csv(f"{os.environ.get('SARS_HOME')}/DB-ids.csv", dtype = str, encoding = 'latin-1')
    db = db.fillna('')
    db_country = subset_db(df = db, col = 'Country', _dict = COUNTRIES)
    db_state = subset_db(df = db_country, col = 'State', _dict = STATES)
    
    LOGGER.info('Updating AT_ID.csv')
    db[['Seq_ID', 'AT_ID']].to_csv(f"{os.environ.get('SARS_HOME')}/AT_ID.csv", index = False)
    LOGGER.info(f"Updating DB.csv")
    db_state['Owner_org'] = db_state[['State', 'Country']].apply(lambda x: get_owner(x), axis = 1)
    
    db_state.to_csv(f"{os.environ.get('SARS_HOME')}/DB.csv", index = False)
    LOGGER.info(f"Generating json file.")
    _run_cmd(f"csvtk csv2json -k Seq_ID {os.environ.get('SARS_HOME')}/DB.csv > {os.environ.get('SARS_HOME')}/DB.json")

def _merge_sars_db(sars_db, epi_home):

    LOGGER.info(f"Looking for current epi data")
    p = subprocess.run(f"ls -1t {epi_home}/EPI* | head -n 1", shell = True, capture_output = True, encoding = 'utf-8')
    current_epi = p.stdout.strip()
    if current_epi != '':
        LOGGER.info(f"Found : {current_epi}")
    else:
        LOGGER.critical(f"There is something wrong with epi data, please contact epi team. Exiting")
        raise SystemExit
    LOGGER.info(f"Cleaning up epi data.")
    if '.xlsx' in current_epi:
        pre =f"xlsx2csv -i -f '%Y-%m-%d' {current_epi}"
    else:
        LOGGER.info(f"Running dos2unix")
        subprocess.run(f"dos2unix {current_epi}", shell = True)
        pre = f"cat {current_epi}"
    clean_cmd = f" {pre}  | csvtk sort -k Date_coll:r | csvtk uniq -f Sample_ID | csvtk sort -k Sample_ID > $SARS_HOME/EPI.csv"
    LOGGER.info(f"Cleaning up epi data. Running {clean_cmd} ")
    cleaning = subprocess.run(clean_cmd, shell = True, capture_output = True, encoding = 'utf-8')
    if cleaning.returncode == 0:
        LOGGER.info(f"Epi data successfully cleaned.")
    else:
        LOGGER.critical(f"Something is wrong with {current_epi}. Please contact epi team")
        raise SystemExit
    merge_cmd_1 = f"csvtk join --left-join -f 'Sample_ID;Sample_ID' {sars_db}.tmp $SARS_HOME/EPI.csv > $SARS_HOME/DB-intermediate.csv"
    LOGGER.info(f'Merging epi and QC data: {merge_cmd_1}')
    first_merge = subprocess.run(merge_cmd_1, shell = True, capture_output = True, encoding = "utf-8")
    if first_merge.returncode == 0:
        LOGGER.info(f"QC2 and epi data successfully merged.")
    else:
        LOGGER.critical(f"Something is wrong with merging. Please check your input files and try again.")
        raise SystemExit
    merge_cmd_2 = f"csvtk join --left-join -f 'Seq_ID;Seq_ID' $SARS_HOME/DB-intermediate.csv $SARS_HOME/AT_ID.csv > $SARS_HOME/DB-ids.csv"
    LOGGER.info(f'Merging DB with AT IDs: {merge_cmd_2}')
    second_merge = subprocess.run(merge_cmd_2, shell = True, capture_output = True, encoding = "utf-8")
    if second_merge.returncode == 0:
        LOGGER.info(f"QC2 and AT IDs data successfully merged.")
    else:
        LOGGER.critical(f"Something is wrong with merging. Please check your input files and try again.")
        raise SystemExit
    LOGGER.info(f"Updating AT IDs")
    
    _update_at()

def _assign_dict_val(_dict, key, val):
    if key not in _dict:
        _dict[key] = [val]
    else:
        _dict[key].append(val)
    return _dict

def _get_channels(path_to_isos):
    _dict = {}
    # channel : string
    with open(path_to_isos, 'r') as f:
        ids = f.read().strip().split('\n')
    tab = pandas.read_csv(f"{os.environ.get('SARS_HOME')}/DB.csv", dtype = str)
    idcol = tab.columns[0]
    tab = tab[tab[idcol].isin(ids)]
    tab = tab.fillna('')
    # get possible channels
    for row in tab.iterrows():
        if row[1]['Country'] == 'Australia' and row[1]['State'] in CHANNELS:
            _dict = _assign_dict_val(_dict = _dict, key =row[1]['State'], val =  row[1][idcol])
        elif row[1]['Country'] in CHANNELS:
            _dict = _assign_dict_val(_dict = _dict, key = row[1]['Country'], val =  row[1][idcol])
        else:
            _dict = _assign_dict_val(_dict = _dict, key = 'Victoria', val =  row[1][idcol])
    return tab

def _slacker(msg, channel):

    my_command = f"curl -X POST -H 'Content-type: application/json' --data '{{\"blocks\": [ {{\"type\": \"section\",\"text\": {{ \"type\": \"mrkdwn\", \"text\": \"{msg}\"}} }} ] }}'" 
    my_command +=f" {HOOKS[channel]}"
    LOGGER.info(f"Posting update to slack channel : # slack.")
    p = subprocess.run(my_command, shell = True, capture_output = True, encoding = 'utf-8')
    # print(p)

def _send(tmp_df, runid, tech,channel,_type = 'first', passes = 0, fails = 0):

    if _type == 'first':
        line = f"QC2 update for SARS on run *{runid}* ({tech}) \nPASS: {passes} FAIL: {fails}"
    else:
        line = f"QC2 update for SARS on run *{runid}* continued."
    p = subprocess.run(f"csvtk pretty {tmp_df}", shell = True, capture_output = True, encoding = 'utf-8')
    data = [f"<!channel> {line}", f"```{p.stdout.strip()}```"]
    
    
    msg = "\n".join(data)

    _slacker(msg = msg, channel = CHANNELS[channel])

def _construct_msg(df, runid, tech, channel, passes, fails):
    # base message
    tmp_df = generate_temp()
    df[0] = df[0].rename(columns = {'Coverage': 'CovX5'})
    df[0][['Seq_ID','AT_ID','CovX5','Lineage','Seq_QC']].to_csv( tmp_df, index = False)
    LOGGER.info(f"Data saved at : {tmp_df}")
    _send(tmp_df = tmp_df, runid=runid, tech = tech,channel = channel,_type = 'first', passes = passes, fails = fails)

    if len(df)>1:
        for d in range(1,len(df)):
            tmp_df = generate_temp()
            df[d] = df[d].rename(columns = {'Coverage': 'CovX5'})
            df[d][['Seq_ID','AT_ID','CovX5','Lineage','Seq_QC']].to_csv( tmp_df, index = False)
            _send(tmp_df = tmp_df, runid=runid, tech = tech,channel = channel,_type = 'second')
    
    msg = f"<@U1B7G166L> `DB.csv`, `DB.json` and `mdu.ffn` updated."
    _slacker(msg = msg, channel = "qc")


def _send_msg(tab, runid, tech):

    # for c in channels:
    #     isos = channels[c]
        # x = tab[tab[tab.columns[0]].isin(isos)]
    fails = tab[tab['Seq_QC'] == 'FAIL'].shape[0]
    passes = tab[tab['Seq_QC'] == 'PASS'].shape[0]
    n = 54 # max size of run
    _df_list = [tab[i:i+n] for i in range(0,tab.shape[0],n)]
    _construct_msg(df = _df_list, runid = runid, tech = tech, passes = passes, fails = fails, channel = 'qc')
        # _slacker(msg = msg, channel = CHANNELS[c])


def  _send_qc_slack(workdir, path_to_isos, runid,tech):

    tab = _get_channels(path_to_isos)
    _send_msg(tab, runid, tech)
    
def _check_tools():

    check_csvtk = subprocess.run('csvtk -h', shell=True, capture_output = True, encoding='utf-8')
    check_seqkit = subprocess.run('seqkit -h', shell=True, capture_output = True, encoding='utf-8')

    if (check_seqkit.returncode != 0) or (check_csvtk.returncode != 0):
        LOGGER.critical(f"Something is wrong with your env, please make sure both csvtk and seqkit are available.")
        raise SystemExit
    else:
        LOGGER.info(f"seqkit and csvtk are available.")

def collate(args):

    # master = pathlib.Path(args.db_dir, args.db_file)
    # _dict = get_master(master)
    jsons = get_current_jsons(args.data, args.runid)
    LOGGER.info(f"Checking that all files are in expected locations.")
    if args.qc == 'sars':
        _check_tools()
        path_to_isos,tech = _update_sars_db(jsons = jsons , sars_db = args.sars_db, runid =args.runid)
        _update_consensus(path_to_isos = path_to_isos, runid = args.runid, master_consensus = args.master_consensus, 
                            data_dir = args.data, sars_db = args.sars_db)
        _update_pango()
        _merge_sars_db(sars_db = args.sars_db, epi_home = args.epi_home)
        if args.send_slack:
            _send_qc_slack(workdir = args.sars_workdir, path_to_isos = path_to_isos, runid = args.runid, tech = tech)
        LOGGER.info(f"Cleaning up")
        _run_cmd(f"rm -rf {path_to_isos}")
    else:
        LOGGER.info(f"Finalising files for : {args.runid}")
        # tmp_master = update_master(_dict, jsons, master, args.runid)
        change_permissions(args.data, args.reads, args.runid)
        link_files(args.data, args.runid)
        # move_master(tmp_master, master)
        _update_dbs(args.runid)
        

def set_parsers():
    # setup the parser
    parser = argparse.ArgumentParser(description='Update and finalise MDU qc',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--data',
        help='',
        default = os.environ.get('MDU_DATA'))
    parser.add_argument('--sars_db',
        help='',
        default = f"{os.environ.get('SARS_HOME')}/QC2.csv")
    parser.add_argument('--reads',
        help='',
        default = os.environ.get('MDU_READS'))
    parser.add_argument('--db_dir',
        help=f'',
        default = os.environ.get('MDU_DB'))
    parser.add_argument('--db_file', 
        help='',
        default = os.environ.get('MDU_DB_FILE'))
    parser.add_argument('--runid',
        help='',
        default = '')
    parser.add_argument('--qc',
        help = '',
        default = 'standard_bacteria')
    parser.add_argument('--master_consensus',
        help = '',
        default = f"{os.environ.get('SARS_HOME')}/mdu.ffn")
    parser.add_argument('--epi_home',
        help = '',
        default = f"/home/mdu/epi/covid")
    parser.add_argument('--sars_workdir',
        help = '',
        default = f"")
    parser.add_argument("--send_slack",
        action = "store_true")
        
    
    
    parser.set_defaults(func=collate)
    args = parser.parse_args()
    print(args)
    if vars(args) == {}:
        parser.print_help(sys.stderr)
    else:
        # print(args)
        args.func(args)
	

def main():
    """
    run pipeline
    """

    args = set_parsers()
    

if __name__ == "__main__":
    main()


