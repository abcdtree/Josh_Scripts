import pandas as pd

df_tamr = pd.read_csv("tbtamr.csv")
df_PHESS = pd.read_excel("TBsharepoint.xlsx")[["PHESS ID", "MDU ID"]]
df_PHESS.columns = ["PHESS ID", "Seq_ID"]

#rint(df_tamr.columns)
#print("---")
#print(df_PHESS.columns)

df_tamr = df_tamr.merge(df_PHESS, on="Seq_ID", how="left")
columns = list(df_tamr.columns)
df_tamr = df_tamr[[columns[0], columns[-1]]+ columns[1:-1]]
df_tamr.to_csv("2023-18-AMR-table.csv",index=None)
