import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd

# DRUHY UKOL
# Ověření Paketova pravidla na trhu her
# Vypocet pomoci kumulativniho součti a podíly celku
# Zjisti jake procento vydavetlu generuje 80% veskerych globalnich prodeju 

df= pd.read_csv('vgsales.csv')


soucet_vydavetelu = df.groupby('Publisher')['Global_Sales'].sum().sort_values(ascending=False)

hranice_80 = soucet_vydavetelu.sum()*0.8
komulativni = soucet_vydavetelu.cumsum()
top_vydavatele = komulativni[komulativni <= hranice_80]
print(len(top_vydavatele))
