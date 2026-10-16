import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# PRVNÍ ÚLOHA 
# Detekce anomálií pomocí Z-skore pro EU trh
# Pomocí vztahu pro Z-skore (hodnota-průměr)/směrodatná odchylka
# Intuitivní význam vztahu je o kolik směrodatných odchylek se evropské prodeje odchylují od průměru

df = pd.read_csv("vgsales.csv")

eu_prumer = df["EU_Sales"].mean()
eu_odchylka = df["EU_Sales"].std()
df['EU_Z_Score'] = (df['EU_Sales'] - eu_prumer)/ eu_odchylka

anomalie = df[df['EU_Z_Score'] > 10]
anomalie.set_index('Name')['EU_Z_Score'].plot(kind='bar', color ='#00ffcc')
print(anomalie[['Name', 'EU_Sales', 'EU_Z_Score']])

plt.show()