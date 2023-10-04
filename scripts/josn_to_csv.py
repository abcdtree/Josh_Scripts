import pandas as pd

id_list = []
with open("ids.txt", 'r') as myids:
    for line in myids:
        info = line.strip()
        if len(info) > 0:
            id_list.append(info)

print(len(id_list))

df = pd.read_json("ausmduid.json")
df_filter = df[df["mdu_id"].isin(id_list)]

print(df_filter.mdu_id.count())

df_filter.to_csv("ids.tab", sep="\t", index=False)

with_aus_ids = df_filter["mdu_id"].tolist()

rest_id = sorted(list(set(id_list) - set(with_aus_ids)))
with open("ids.tab", "a") as myout2:
    for mid in rest_id:
        myout2.write(f"{mid}\t{mid}\n")
