import pandas
import numpy
import sys
import datetime
import logging
import os
import click

OFN_API_URL = "http://172.30.48.230:703/listeria/ofn"
LISTERIA_PATH = os.getcwd()


def load_api(url):
    tab = pandas.read_json(path_or_buf=url,
                           orient='records')
    tab = tab.set_index('seq_id')
    tab = tab[tab.gmlst != '-']
    return tab


def load_db(filename):
    tab = pandas.read_table(filepath_or_buffer=filename,
                            delimiter=None,
                            engine='python',
                            index_col=0)
    #tab = tab.set_index('seq_id')
    return tab


def new_samples(tab, db):
    '''
    Identify samples in the main DB that are not in the local DB

    >>> main_db = [{'seq_id': i} for i in range(1,6)]
    >>> local_db = [{'seq_id': i} for i in range(1,4)]
    >>> main_db = pandas.DataFrame(main_db)
    >>> local_db = pandas.DataFrame(local_db)
    >>> new_samples(main_db, local_db)
    {4, 5}
    '''
    new_id = set(tab.index).difference(db.index)
    return list(new_id)

def gmlst_handle(a):
    result = 0
    try:
    	result = int(a)
    except:
    	result = 0
    return result

def update_db(samples, main_db, local_db):
    '''
    Add the new rows to the local DB.

    >>> main_db = [{'seq_id': i} for i in range(1,6)]
    >>> local_db = [{'seq_id': i} for i in range(1,4)]
    >>> main_db = pandas.DataFrame(main_db)
    >>> local_db = pandas.DataFrame(local_db)
    >>> new_samples(main_db, local_db)
    {4, 5}
    '''
    new_rows = main_db[main_db.index.isin(samples)]
    new_rows = new_rows[new_rows['gmlst'] != '']
    new_db = new_rows.append(local_db)
    new_db.update(main_db)
    new_db = new_db[new_db.index.isin(main_db.index)]
    #new_db[['gmlst']] = new_db[['gmlst']].astype(int, errors='ignore')
    new_db[['gmlst']] = new_db[['gmlst']].apply(gmlst_handle, axis=1)
    return new_db


def new_mlst(samples, tab):
    new_rows = tab[tab.index.isin(samples)]
    new_mlst = new_rows['gmlst'].unique()
    mlst_list = []
    for st in new_mlst:
        try:
            st = int(st)
            total_isolates = sum(tab['gmlst'] == st)
            if total_isolates > 2:
                mlst_list += [st]
            else:
                logging.warning(f'Only found {total_isolates} for ST {st}.')
        except:
            logging.warning(f'{st} failed to coerce to int.')
    return numpy.sort(mlst_list)


def issue_cmd(updated_db):
    today = datetime.datetime.today()
    today = today.strftime('%Y-%m-%d')
    todaycol = today.replace('-', '')
    new_db_name = os.path.join(LISTERIA_PATH, f'Lm_master{todaycol}.txt')
    updated_db[['gmlst']] = updated_db[['gmlst']].apply(gmlst_handle, axis=1)
    updated_db.to_csv(new_db_name, sep='\t')
    print(f'Lm_master{todaycol}.txt')


@click.command()
@click.argument("local_db")
def run_update_db(local_db):
    main_db = load_api(OFN_API_URL)
    local_db_fn = local_db
    #local_db = load_db(local_db)
    #new_id = new_samples(main_db, local_db)
    #new_local_db = update_db(new_id, main_db, local_db)
    #list_mlst = new_mlst(new_id, new_local_db)
    issue_cmd(main_db)


if __name__ == "__main__":
    run_update_db()
