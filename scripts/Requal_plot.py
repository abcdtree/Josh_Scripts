import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
#Import data
data_orig = pd.read_csv("cov_2014-02457orig.csv", sep=",")
df = pd.DataFrame(data_orig)
#Dataset was large so I grouped by every 10000 and summed up coverage
df_sum = df.set_index(df.index // 10000).sum(level=0)
#Initialise lists for x and y Have tried many different ways
X = list(df_sum.iloc[:, 1])#iloc helps select specific row/column
#X = np.arange(0, 55, 1)
#X = list(range(-10, 150))
Y = list(df_sum.iloc[:, 2])#[Rstart:Rend,C]
#Plot the data into a bar chart
plt.bar(X, Y)
plt.title('Original coverage')
plt.xlabel('Position')
plt.ylabel('Depth of coverage')
#Show the plot
plt.show()
