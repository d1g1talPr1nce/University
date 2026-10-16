import numpy 
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("vgsales.csv")

df_sports = df[df['Genre'] == 'Sports'].copy()
df_sports['NA_EU_rozdil'] = df_sports['NA_Sales'] - df_sports['EU_Sales']

rozdil = df_sports['NA_EU_rozdil']

prumer = rozdil.mean()
odchylka = rozdil.std()
minimum = rozdil.min()
maximum = rozdil.max()

min_hra = df_sports.loc[rozdil.idxmin(), 'Name']
max_hra = df_sports.loc[rozdil.idxmax(), 'Name']


print("! Výpis hodnot !")
print(f"Pruměr: {prumer:.6f}")
print(f"Odchylka: {odchylka:.6f}")
print(f"Maximum u {max_hra} s: {maximum:.2f}")
print(f"Minimum u {min_hra} s: {minimum:.2f}")