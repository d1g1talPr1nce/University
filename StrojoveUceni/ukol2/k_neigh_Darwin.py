import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#median
from sklearn.impute import SimpleImputer
# minmax norm
from sklearn.preprocessing import MinMaxScaler
#knn
from sklearn.neighbors import KNeighborsClassifier
#kontrola presnosti
from sklearn.metrics import accuracy_score
# konfuzni matice
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay

# jednotlive outputy
from sklearn.metrics import (precision_score, recall_score, f1_score)
#cross validace
from sklearn.model_selection import StratifiedKFold

#nacteni souboru
df = pd.read_csv("weatherAUS.csv")

#pouze pro mesto Darwin
df_Darwin = df[df["Location"] == "Darwin"].copy()

#vyber 11 vstupnich atributu definujicich prostor priznaku
features = ["MinTemp", "MaxTemp", "Rainfall", "Humidity9am", "Humidity3pm", "Pressure9am", "Pressure3pm", "WindSpeed9am", "WindSpeed3pm", "Temp9am", "Temp3pm"]

#zahodim prazdne radky v raintomorrow
df_Darwin = df_Darwin.dropna(subset=["RainTomorrow"]).copy()

x = df_Darwin[features]
y = df_Darwin["RainTomorrow"]

k_values = [1, 3, 5, 7, 9, 11]
results = []
# 10-fold cross validace, zachova priblizny pomer trid Yes/No, shuffle nahodne promicha data, random state zajistuje reprodukovatelnsot
cv = StratifiedKFold(n_splits=10,shuffle=True,random_state=42)

#ruzne hodnoty k (mensi "optimalizace", pokus vybrat tu nejlepsi)
for k in k_values:

    accuracy_list = []
    precision_list = []
    recall_list = []
    f1_list = []
    confusion_total = np.zeros((2, 2), dtype=int)

    #cross validace
    for train_index, test_index in cv.split(x, y):
        #testovaci a trenovaci hodnoty, pro kazdou iteraci (cross)
        X_train_fold = x.iloc[train_index]
        X_test_fold = x.iloc[test_index]
        y_train_fold = y.iloc[train_index]
        y_test_fold = y.iloc[test_index]

        #mediam na prazdne hodnoty (vypln hodnot)
        imputer = SimpleImputer(strategy="median")
        #min max normalizace hodnot kvuli euklidovske vzdalenosti (aby atributy s vetsim ciselnym rozsahem nedominovaly)
        scaler = MinMaxScaler()
        # vytvoreni klasifikatoru
        knn = KNeighborsClassifier(n_neighbors=k)

        # vypocet medianu pouze z trenovacich dat
        imputer.fit(X_train_fold)
        #doplneni chybejicich hodnot stejnymi mediany
        X_train_imputed = imputer.transform(X_train_fold)
        X_test_imputed = imputer.transform(X_test_fold)

        #vypocet minima a maxima pouze z trenovacich dat
        scaler.fit(X_train_imputed)
        #doplneni normalizace do obou dat
        X_train_normalized = scaler.transform(X_train_imputed)
        X_test_normalized = scaler.transform(X_test_imputed)

        #klasifikator
        knn.fit(X_train_normalized, y_train_fold)
        y_pred = knn.predict(X_test_normalized)

        #vysledky jednotlivych iteraci
        accuracy_list.append(accuracy_score(y_test_fold, y_pred))
        precision_list.append(precision_score(y_test_fold, y_pred, pos_label="Yes"))
        recall_list.append(recall_score(y_test_fold, y_pred, pos_label="Yes"))
        f1_list.append(f1_score(y_test_fold, y_pred, pos_label="Yes"))
        #vypocet konfuzni matice pro aktualni fold, a nasledne pricteni do k celkove matici
        cm = confusion_matrix(y_test_fold, y_pred, labels=["No", "Yes"])
        confusion_total += cm

    results.append({"k": k,"accuracy_mean": np.mean(accuracy_list),"accuracy_std": np.std(accuracy_list, ddof=1),"precision_mean": np.mean(precision_list),"recall_mean": np.mean(recall_list),"f1_mean": np.mean(f1_list),"confusion_matrix": confusion_total})

#vykreseni 6 konfuznich matic vedle sebe
fig, axes = plt.subplots(2, 3, figsize=(15, 9))

for ax, result in zip(axes.flat, results):

    cm = result["confusion_matrix"]
    k = result["k"]
    #kazda ta jedna matice
    disp = ConfusionMatrixDisplay(confusion_matrix=cm,display_labels=["No", "Yes"])

    disp.plot(ax=ax,cmap="Blues",colorbar=False)

    ax.set_title(f"k = {k}\n"f"Accuracy = {result['accuracy_mean']:.3f}\n"f"F1 = {result['f1_mean']:.3f}")

plt.suptitle("Darwin — kNN (10-fold cross-validation)",fontsize=16)


df_results = pd.DataFrame([{"k": r["k"],"Accuracy": r["accuracy_mean"],"Precision": r["precision_mean"],"Recall": r["recall_mean"],"F1": r["f1_mean"]} for r in results])

print(df_results.round(4))
# vybira nejlepsi k, podle f1score
best = max(results, key=lambda r: r["f1_mean"])
print("Nejlepší k:", best["k"])
print("F1-score:", best["f1_mean"])
plt.tight_layout()
plt.show()


