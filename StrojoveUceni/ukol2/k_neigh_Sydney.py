import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
from sklearn.neighbors import KNeighborsClassifier 
from sklearn.metrics import confusion_matrix 
from sklearn.model_selection import StratifiedKFold
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import (accuracy_score, recall_score, f1_score, precision_score )
from sklearn.metrics import ConfusionMatrixDisplay

#nacteni souboru
df = pd.read_csv("weatherAUS.csv")
#pouze kde je sydney
df_Sydney = df[df["Location"] == "Sydney"].copy()
#vychozeni prazdnych/nedefinovanych pozic v RainTomorrow
df_Sydney = df_Sydney.dropna(subset="RainTomorrow").copy()

directions = ["WindGustDir", "WindDir9am", "WindDir3pm"]

#kodovani ze stringu na float, pro svetove strany a prislusnou ciselnou reprezentaci
wind_angles = {"N" : 0, "NNE" : 22.5, "NE" : 45, "ENE" : 67.5, "E" : 90, "ESE" : 112.5, "SE" : 135, "SSE" : 157.5, "S" : 180, "SSW" : 202.5, "SW" : 225, "WSW" : 247.5, "W" : 270, "WNW" : 292.5, "NW" : 315, "NNW" : 337.5}

#features, kde jsem pridal smer vetru
features = ["MinTemp","MaxTemp","Rainfall","Humidity9am","Humidity3pm","Pressure9am","Pressure3pm","WindSpeed9am","WindSpeed3pm","Temp9am","Temp3pm"]

#Rozsireni seznamu vstupnich atributu o sin/cos slozky smeru vetru,samotne sloupce budou vytvoreny pozdeji uvnitr cross-validace
for direction in directions:
    features.append(direction + "_sin")
    features.append(direction + "_cos")
    

y = df_Sydney["RainTomorrow"]
# 10-fold cross validace, zachova priblizny pomer trid Yes/No, shuffle nahodne promicha data, random state zajistuje reprodukovatelnsot
cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

results = []
k_values = [1,3,5,7,9,11]
#ruzne hodnoty k (mensi "optimalizace", pokus vybrat tu nejlepsi)
for k in k_values:
    accuracy_list : list = []
    precision_list : list = []
    recall_list : list   = []
    f1_list : list = []
    confusion_total = np.zeros((2,2), dtype=int)
    #cross validace
    for train_index, test_index in cv.split(df_Sydney,y):
        #testovaci a trenovaci hodnoty, pro kazdou iteraci (cross)
        train_fold = df_Sydney.iloc[train_index].copy()
        test_fold = df_Sydney.iloc[test_index].copy()
        #imputace chybejicich kategorickych smeru nejcastejsi hodnotou, imputace uhlu by nemusela respektovat jejich cyklicnost - median neni pro puvodni retezce definovan a bezna ciselna
        direction_imputer = SimpleImputer(strategy="most_frequent")
        #zjisteni nejcastejsiho smeru pouze z trenovacich dat
        direction_imputer.fit(train_fold[directions])
        #doplneni chybejicich kategorii v obou mnozinach
        train_fold[directions] = direction_imputer.transform(train_fold[directions])
        test_fold[directions] = direction_imputer.transform(test_fold[directions])
        #prevod kategorickych smeru na uhly ve stupnich, nasledne na radiany a cyklickou reprezentaci sin/cos
        for direction in directions:

            train_radians = np.deg2rad(train_fold[direction].map(wind_angles))

            test_radians = np.deg2rad(test_fold[direction].map(wind_angles))

            train_fold[direction + "_sin"] = np.sin(train_radians)
            train_fold[direction + "_cos"] = np.cos(train_radians)

            test_fold[direction + "_sin"] = np.sin(test_radians)
            test_fold[direction + "_cos"] = np.cos(test_radians)
        
        X_train_fold = train_fold[features]
        X_test_fold = test_fold[features]

        y_train_fold = y.iloc[train_index]
        y_test_fold = y.iloc[test_index]
        
        # vytvoreni klasifikatoru
        knn = KNeighborsClassifier(n_neighbors=k)
        
        #mediam na prazdne hodnoty (vypln hodnot)
        imputer = SimpleImputer(strategy="median")
        # vypocet medianu pouze z trenovacich dat
        imputer.fit(X_train_fold)
        #doplneni chybejicich hodnot stejnymi mediany
        X_train_imputed = imputer.transform(X_train_fold)
        X_test_imputed = imputer.transform(X_test_fold)
        #min max normalizace hodnot kvuli euklidovske vzdalenosti (aby atributy s vetsim ciselnym rozsahem nedominovaly)
        scaler = MinMaxScaler()
        #vypocet minima a maxima pouze z trenovaich dat
        scaler.fit(X_train_imputed)
        #doplneni normalizace do obou dat
        X_train_normalized = scaler.transform(X_train_imputed)
        X_test_normalized = scaler.transform(X_test_imputed)
        knn.fit(X_train_normalized, y_train_fold)
        y_pred = knn.predict(X_test_normalized)
        #vysledky jednotlivych iteraci
        accuracy_list.append(accuracy_score(y_test_fold, y_pred))
        precision_list.append(precision_score(y_test_fold, y_pred, pos_label="Yes"))
        recall_list.append(recall_score(y_test_fold, y_pred, pos_label="Yes"))
        f1_list.append(f1_score(y_test_fold, y_pred, pos_label="Yes"))

        #vypocet konfuzni matice pro aktualni fold, a nasledne pricteni do k celkove matici
        confusion_total += confusion_matrix(y_test_fold, y_pred, labels=["No", "Yes"])
    results.append({"k": k,"accuracy_mean": np.mean(accuracy_list),"accuracy_std": np.std(accuracy_list, ddof=1),"precision_mean": np.mean(precision_list),"recall_mean": np.mean(recall_list),"f1_mean": np.mean(f1_list),"confusion_matrix": confusion_total.copy()})
    
df_results = pd.DataFrame(results)

print(df_results.drop(columns=["confusion_matrix"]).round(4))
best = max(results, key=lambda r: r["f1_mean"])

print("Nejlepší k:", best["k"])
print("Průměrné F1:", best["f1_mean"])

fig, axes = plt.subplots(2, 3, figsize=(15, 9))

for ax, result in zip(axes.flat, results):

    disp = ConfusionMatrixDisplay(confusion_matrix=result["confusion_matrix"],display_labels=["No", "Yes"])
    disp.plot(ax=ax, cmap="Blues", colorbar=False)

    ax.set_title(f"k = {result['k']}\n"f"F1 = {result['f1_mean']:.3f}")

plt.suptitle("Sydney — kNN (10-fold CV)")
plt.tight_layout()
plt.show()