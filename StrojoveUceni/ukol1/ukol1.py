import numpy
import matplotlib.pyplot as plt
import pandas as pd

#Zobrazte graf s četnostmi žánrů her mezi lety 1990 (včetně) a 2000 (vyjma). 

plt.style.use('dark_background')

df = pd.read_csv("vgsales.csv")

df_1990_2000_year = df[(df['Year'] >= 1990)&(df['Year']< 2000)]

zanry_pocet = df_1990_2000_year['Genre'].value_counts().plot(kind='bar', color = '#ff0044')


plt.title("Četnost žánrů her (1990-1999)", fontsize = 14, fontweight = 'bold')
plt.xlabel('Žánr', fontsize = 12)
plt.ylabel('Počet vydaných her', fontsize = 12)
plt.grid(axis='y', alpha = 0.2)
plt.show()


