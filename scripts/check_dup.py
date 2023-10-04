import pandas
OFN_API_URL = "http://172.30.48.230:703/listeria/ofn"

def load_api(url):
    tab = pandas.read_json(path_or_buf=url,
                           orient='records')
    tab = tab.set_index('seq_id')
    tab = tab[tab.gmlst != '-']
    return tab

df = load_api(OFN_API_URL)
print(df[df.index.duplicated()])

print(df[df.index == "2021-056455"])
