import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score,precision_score,recall_score,f1_score,confusion_matrix)
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import ConfusionMatrixDisplay

#nacteni souboru
df = pd.read_csv("weatherAUS.csv")
#vyber pouze jednoho mesta (Darwin)
df_Darwin = df[df["Location"] == "Darwin"].copy()

#zahodim prazdne radky v raintomorrow
features = ["MinTemp", "MaxTemp", "Rainfall", "Humidity9am", "Humidity3pm", "Pressure9am", "Pressure3pm", "WindSpeed9am", "WindSpeed3pm", "Temp9am", "Temp3pm"]

#prazdne radky v raintomorrow zahodim
df_Darwin = df_Darwin.dropna(subset=["RainTomorrow"]).copy()

#postaveni prostoru
x = df_Darwin[features]
y = df_Darwin["RainTomorrow"]

# 10-fold cross validace, zachova priblizny pomer trid Yes/No, shuffle nahodne promicha data, random state zajistuje reprodukovatelnsot
cv = StratifiedKFold(n_splits=10,shuffle=True,random_state=42)
accuracy_list: list = []
precision_list : list = []
recall_list : list = []
f1_list : list = [] 

confusion_total = np.zeros((2, 2), dtype=int)

#cross validace
for train_index, test_index in cv.split(x,y):
    #testovaci a trenovaci hodnoty, pro kazdou iteraci (cross)
    X_train_fold = x.iloc[train_index]
    X_test_fold  = x.iloc[test_index]
    y_train_fold = y.iloc[train_index]
    y_test_fold = y.iloc[test_index]
    
    #mediam na prazdne hodnoty (vypln hodnot)
    imputer = SimpleImputer(strategy="median")
    #inicializace klasifikatoru
    gnb = GaussianNB()
    
    # vypocet medianu pouze z trenovacich dat 
    imputer.fit(X_train_fold)
    #doplneni chybejicich hodnot stejnymi mediany
    X_train_imputed = imputer.transform(X_train_fold)
    X_test_imputed = imputer.transform(X_test_fold)

    #trenovani modelu
    gnb.fit(X_train_imputed,y_train_fold)
    # vysledek modelu
    y_pred = gnb.predict(X_test_imputed)

    #uz jenom vypis urcitych hodnot a konfuzni matice samostatne
    confusion_total += confusion_matrix(y_test_fold, y_pred, labels=["No", "Yes"])
    accuracy_list.append(accuracy_score(y_test_fold, y_pred))
    precision_list.append(precision_score(y_test_fold, y_pred, pos_label="Yes"))
    recall_list.append(recall_score(y_test_fold, y_pred, pos_label="Yes"))
    f1_list.append(f1_score(y_test_fold, y_pred, pos_label="Yes"))

# uz jen print... a vyzobrazeni konfuzni matice
print("Gaussian Naive Bayes — Darwin")

print("Accuracy:", np.mean(accuracy_list))
print("Precision:", np.mean(precision_list))
print("Recall:", np.mean(recall_list))
print("F1-score:", np.mean(f1_list))

print("Směrodatná odchylka accuracy:",
      np.std(accuracy_list, ddof=1))

print("Souhrnná konfuzní matice:")
print(confusion_total)

disp = ConfusionMatrixDisplay(confusion_matrix=confusion_total,display_labels=["No", "Yes"])
disp.plot(cmap="Blues")
plt.title("Darwin — Gaussian Naive Bayes (10-fold CV)")
plt.show()