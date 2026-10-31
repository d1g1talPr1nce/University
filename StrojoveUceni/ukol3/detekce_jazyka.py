import matplotlib.pyplot as plt
import unicodedata
from collections import Counter
import numpy as np
import random
import math
from sklearn.metrics import (confusion_matrix,ConfusionMatrixDisplay,accuracy_score)
import csv

# Za jazyky si vybírám Češtinu, Slovenštinu, Ruštinu, Angličtinu a Ukrajinšitnu

#filtrace textu
def normalizuj(text : str)-> str:
    # prevedeno na male pismena, cisla a jine znaky vyhozeny, mezera zustala
    text = unicodedata.normalize("NFC", text)
    text = text.casefold()
    znaky : list = []
    novy_text : str = ""
    for i in text:
        if i.isalpha():
            znaky.append(i)
        else:
            znaky.append(" ")
    novy_text = "".join(znaky)
    novy_text = " ".join(novy_text.split())
    return novy_text

#vytvorení ngramu
def vytvor_ngramy(text : str, n : int)-> Counter:
    #ngram musi byt vetsi nez nula
    if n <= 0:
        raise ValueError("Délka n-gramu musí být kladná!")
    #ulozeni do Counter. Diky tomu mame dvojici ngram : vyskyt
    cetnosti = Counter()
    for i in range(len(text) - n +1):
        ngram = text[i:(n+i)]
        cetnosti[ngram] += 1
    return cetnosti


#analyza korpusu
def analyzuj_korpus(jazyk: str) -> dict:
    jazyky = {
        "cs": "Čeština",
        "sk": "Slovenština",
        "en": "Angličtina",
        "ru": "Ruština",
        "uk": "Ukrajinština"
    }

     
    pozadovany_jazyk: str | None = None
    # vybrani spravneho jazyka
    for znak, nazev in jazyky.items():
        if nazev == jazyk:
            pozadovany_jazyk = znak
            break

    if pozadovany_jazyk is None:
        raise ValueError("Nepodporovaný jazyk!")

    # Nacteni korpusu
    with open(f"corpus/{pozadovany_jazyk}.txt",mode="r",encoding="utf-8") as soubor:
        text = soubor.read()

    # Normalizace textu
    normalizovany_text = normalizuj(text)

    if not normalizovany_text:
        raise ValueError(f"Korpus jazyka {jazyk} je prázdný!")

    # Pravdepodobnost model
    model = {}
    #vytvoreni 1gram, 2gram , 3gram a vypocitani jejich pravdepdobnost pomoci Naivni definice...
    for n in range(1, 4):
        ngramy = vytvor_ngramy(normalizovany_text, n)
        celkem = sum(ngramy.values())
        if celkem == 0:
            raise ValueError(f"Nedostatek znaků pro {n}-gramy!")

        mapa = {}
        for gram, cetnost in ngramy.items():
            mapa[gram] = cetnost / celkem

        model[n] = mapa
    return model

jazyky = [
    "Čeština",
    "Slovenština",
    "Angličtina",
    "Ruština",
    "Ukrajinština"
]

modely = {}
#uddelame to pro vsechny jazyky
for jazyk in jazyky:
    modely[jazyk] = analyzuj_korpus(jazyk)

#vykresleni konkretni n-gramu
def vykresli_ngramy(modely: dict, jazyk : str, n: int):
    mapa = modely[jazyk][n]
    serazene = sorted(mapa.items(), key = lambda polozka: polozka[1], reverse=True)[:10]
    #symbolicka ukazka mezery pomoci znaku ␠
    znaky = [gram.replace(" ", "␠") for gram, p in serazene]
    hodnoty = [p for gram, p in serazene]
    #vykrelseni pomoci bar grafu
    fig, ax = plt.subplots(figsize=(8,4))
    ax.bar(znaky, hodnoty)
    ax.set_title(f"Pravděpodobnost jedlotlivých {n}-gramů - {jazyk}")
    ax.set_xlabel("Znaky")
    ax.set_ylabel(("Relativní četnost"))
    plt.tight_layout()
    plt.show()

#porovnani dvou jazyku a konrketniho n-gramu
def porovnej_jazyky(modely : dict, jazyk1 : str, jazyk2: str, n : int):
    mapa1 = modely[jazyk1][n]
    mapa2 = modely[jazyk2][n]
    top10 = sorted(mapa1.items(), key = lambda polozka : polozka[1],reverse=True)[:10]
    gramy = [gram for gram, p in top10]
    hodnoty1 = [mapa1.get(gram,0) for gram in gramy]
    hodnoty2 = [mapa2.get(gram, 0) for gram in gramy]
    x = np.arange(len(gramy))
    sirka = 0.4
    fig,ax = plt.subplots(figsize=(12,7))
    ax.bar(x-sirka / 2, hodnoty1, sirka , label = jazyk1)
    ax.bar(x + sirka / 2 , hodnoty2, sirka, label = jazyk2)
    ax.set_xticks(x)
    ax.set_xticklabels([g.replace(" ", "␠")for g in gramy])
    ax.set_title(f"Srovnání {n}-gramů: {jazyk1} vs {jazyk2}")
    ax.set_xlabel(f"{n}-gram")
    ax.set_ylabel("Relativní četnost")
    ax.legend()
    plt.tight_layout()
    fig.savefig("srovnani.png", dpi = 300, bbox_inches="tight")
    plt.show()

def vyber_ngramy(text: str, N: int) -> dict:
    if type(N) is not int or N <= 0:
        raise ValueError("N musí být kladné celé číslo!")

    text = normalizuj(text)
    m = len(text)
    if m < 3 * N:
        raise ValueError(f"Text je příliš krátký! "f"Počet znaků: {m}, požadováno alespoň {3 * N}.")

    vysledek = {}
    pouzite_pozice = set()
    for n in (3, 2, 1):
        dostupne_pozice = [i for i in range(m - n + 1)if i not in pouzite_pozice]
        
        vybrane_pozice = random.sample(dostupne_pozice, N)

        pouzite_pozice.update(vybrane_pozice)
        
        ngramy = [text[i:i+n]for i in vybrane_pozice]
        vysledek[n] = ngramy

    return {n: vysledek[n] for n in (1, 2, 3)}

#klasifikator postaveny na bazi Bayese
def klasifikuj(text: str, modely: dict, N: int = 5):
    
    vybrane = vyber_ngramy(text, N)
    #pro nulove hodnoty, protoze log diverguje do nekonecna pro  log 0
    epsilon = 1e-8
    skore = {}
    #konkretni vztah prevede na dva loopy (dvojita suma... pres log...)
    for jazyk, model in modely.items():
        suma = 0.0
        for n, ngramy in vybrane.items():
            for gram in ngramy:
                pravdepodobnost = model[n].get(gram, epsilon)
                suma += math.log(pravdepodobnost)

        skore[jazyk] = suma

    nejlepsi_jazyk = max(skore, key=skore.get)
    return nejlepsi_jazyk, skore

#vytvoreni konfuzni matice
def vytvor_matici(modely: dict,testy: list,N: int = 10,opakovani: int = 100):

    if opakovani <= 0:
        raise ValueError("Počet opakování musí být kladný!")

    jazyky = list(modely.keys())
    skutecne = []
    predikovane = []

  
    for skutecny_jazyk, text in testy:
        if skutecny_jazyk not in modely:
            raise ValueError(f"Neznámý jazyk: {skutecny_jazyk}")
        for _ in range(opakovani):
            detekovany_jazyk, _ = klasifikuj(text, modely, N)
            skutecne.append(skutecny_jazyk)
            predikovane.append(detekovany_jazyk)
    matice = confusion_matrix(skutecne,predikovane,labels=jazyky)
    presnost = accuracy_score(skutecne,predikovane)

    # Vizualizace matice
    fig, ax = plt.subplots(figsize=(10, 8))

    disp = ConfusionMatrixDisplay(confusion_matrix=matice,display_labels=jazyky)

    disp.plot(ax=ax,cmap="Blues",values_format="d",xticks_rotation=45,colorbar=True)
    ax.set_title(f"Matice záměn jazykového klasifikátoru\n"f"N = {N}, opakování = {opakovani}")
    ax.set_xlabel("Predikovaný jazyk")
    ax.set_ylabel("Skutečný jazyk")
    plt.tight_layout()
    fig.savefig(f"matice_zamen_N{N}.png",dpi=300,bbox_inches="tight")
    plt.show()
    return matice, presnost

#Testovani modelu
with open("test_data/testy.tsv",mode="r",encoding="utf-8",newline="") as soubor:

    reader = csv.DictReader(soubor, delimiter="\t")
    testy = [(radek["jazyk"], radek["text"])for radek in reader]

print("Počet testovacích textů:", len(testy))
rozdeleni = Counter(jazyk for jazyk, text in testy)
print("Rozdělení jazyků:", rozdeleni)

assert len(testy) == 100
assert all(rozdeleni[jazyk] == 20 for jazyk in modely)

random.seed(42)
# Jedna klasifikace pro kazdy testovaci text
matice, presnost = vytvor_matici(modely=modely,testy=testy,N=10,opakovani=1)

