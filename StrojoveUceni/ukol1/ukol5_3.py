import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd

# TRETI ULOHA
# Mezirocni procentualni rust celosvetoveho trhu
# Vypocet : (soucasny rok - predchozi rok) / predchozi rok
# Zjistit jaky rok zaznamel nejvetsi procentualni narust prodeju global sales oproti predchozimu roku

df = pd.read_csv('vgsales.csv')

seskupeni_podle_roku = df.groupby('Year')['Global_Sales'].sum().sort_index()

mezirocni_rust = seskupeni_podle_roku.pct_change()
nejvetsi_rust_rok = mezirocni_rust.idxmax()
hodnota_rustu = mezirocni_rust.max()*100

print(f"Největší nárust byl v roce {nejvetsi_rust_rok:.0f} a to o {hodnota_rustu:.1f} %.")