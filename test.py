import pandas as pd

df = {"name": ["chichi"], "height": ["130cm"]}
df = pd.DataFrame(df)
rows = len(df)
row = ["Simon", "201cm"]
df.loc[rows] = row
print(df)