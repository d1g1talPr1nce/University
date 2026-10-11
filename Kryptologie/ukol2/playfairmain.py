import numpy as np
import matplotlib as plt 
import tkinter as tk
import string

def filtrace_textu(vstupni_text : str, parametr_CZ_EN : int) -> str:
    if type(parametr_CZ_EN) != int:
        raise TypeError("Špatně, nezadali jste číslo 0 nebo 1!!!")
    if parametr_CZ_EN not in (0,1):
        raise ValueError("Neplatný výběr jazyka!")
    
    abeceda : list = list(string.ascii_lowercase)
    diakritia : list = ['ě','š','č','ř','ž','ý','á','í','é','ó', 'ů', 'ú', 'ď', 'ť', 'ň']
    bezdiakritiky : list = ['e', 's', 'c', 'r', 'z', 'y', 'a', 'i', 'e', 'o', 'u', 'u', 'd', 't', 'n']
    cislo : list = [str(i) for i in range(0,10)]    
    cislo_slovne : list = ["xnulax", "xjednax", "xdvax", "xtrax", "xctyrax", "xpetx", "xsestx", "xsedmx", "xosmx", "xdevetx"]
    vstupni_text_lower = vstupni_text.lower()
    list_OT : list[str] = []
    list_FL : str = ""
    
    #uprava textu na povolený    
    for znak in vstupni_text_lower:
        if znak  in diakritia:
            index = diakritia.index(znak)
            novy_znak = bezdiakritiky[index]
            list_OT.append(novy_znak)
        elif(znak == " "):
            list_OT.append("xmezerax")
        elif(znak in cislo):
            index_cislo = cislo.index(znak)
            list_OT.append(cislo_slovne[index_cislo])
        elif(znak not in diakritia and znak not in abeceda):
            continue
        else:
            list_OT.append(znak) 
    string_OT = "".join(list_OT)
    list_FL += string_OT
    list_FL_map = []
    if(parametr_CZ_EN == 0):
        for znak in list_FL:
            if znak == 'i':
                list_FL_map.append('y')
            else:
                list_FL_map.append(znak)
    else:
        for znak in list_FL:
            if znak == 'w':
                list_FL_map.append('v')
            else:
                list_FL_map.append(znak)          
    list_FL_String_map = "".join(list_FL_map)          
    return list_FL_String_map

# filtrace klice, a povolene parametry klice
def ziskta_klic(vstup_klic : str, parametr_CZ_EN : int) -> str:
    if not isinstance(vstup_klic, str):
        print("Nezadali jste string, nebo se snažíte poškodit algoritmus! Program se vypne!")
        raise TypeError
        
    #filtr na klic
    abeceda : list = list(string.ascii_lowercase)
    diakritia : list     = ['ě','š','č','ř','ž','ý','á','í','é','ó', 'ů', 'ú', 'ď', 'ť', 'ň']
    bezdiakritiky : list = ['e', 's', 'c', 'r', 'z', 'y', 'a', 'i', 'e', 'o', 'u', 'u', 'd', 't', 'n']
    vstup_klic = vstup_klic.lower()
    vstup_klic_dovolene_znaky: str = ""
    for i in vstup_klic:
        if i in diakritia:
            index = diakritia.index(i)
            vstup_klic_dovolene_znaky = vstup_klic_dovolene_znaky + bezdiakritiky[index]
        elif(i not in abeceda):
            continue
        else:
            vstup_klic_dovolene_znaky = vstup_klic_dovolene_znaky + i
    
    unikatni_znaky_klic : str = ""
    vstup_klic_mapovani:  str = ""
    
    # mapovani i na y pokud je to anglicka, pokud je to ceska tak w na v.
    if type(parametr_CZ_EN) != int:
        raise TypeError("Špatně, nezadali jste číslo 0 nebo 1!!!")
    if parametr_CZ_EN not in (0,1):
        raise ValueError("Neplatný výběr jazyka!")
    
    for k in vstup_klic_dovolene_znaky:
        if(parametr_CZ_EN == 0): 
            if(k == 'i'):  
                k = 'y'
            vstup_klic_mapovani = vstup_klic_mapovani + k
        elif(parametr_CZ_EN == 1): 
            if(k == 'w'):
                k = 'v'
            vstup_klic_mapovani = vstup_klic_mapovani + k
        
    # odstraneni duplicit
    for znak in vstup_klic_mapovani: 
        if(znak not in unikatni_znaky_klic):
            unikatni_znaky_klic= unikatni_znaky_klic + znak
        else:
            continue
    
    return unikatni_znaky_klic


def tabulka(klic: str, parametr_CZ_EN : int)-> list:
    if type(parametr_CZ_EN) != int:
        raise TypeError("Špatně, nezadali jste číslo 0 nebo 1!!!")
    if parametr_CZ_EN not in (0,1):
        raise ValueError("Neplatný výběr jazyka!")
    
    # vytvoreni 1D posloupnosti
    abeceda : list = list(string.ascii_lowercase)
    posloupnost_znaku = klic
    
    if parametr_CZ_EN == 0:
        zakazany_znak = 'i'
    else:
        zakazany_znak = 'w'
    
    #nasledna transofmrace na matici
    for i in range(len(abeceda)):
        if abeceda[i] == zakazany_znak:
            continue
        
        if abeceda[i] in posloupnost_znaku:
            continue
        
        posloupnost_znaku += abeceda[i]
                        
    matice = []
    for i in range(0,5):
        radek = posloupnost_znaku[5*i:5 + (5*i)]
        matice.append(radek)
    
    return matice 
    
# mapuji znak na dvojici v ploše
def najdi_souradnice(matice:list[str], znak:str)-> tuple[int, int]:
    #brute force pro najiti zobrazeni
    for i in range(5):
        for j in range(5):
            if(matice[i][j] == znak):
                return (i,j)
    raise ValueError(f"Znak '{znak}' nebyl nalezen v šifrovací tabulce.")

# transformace dvojic
def zasifruj_dvojici(matice, znak1, znak2)-> str:
    dvojice_1 = najdi_souradnice(matice, znak1)
    dvojice_2 = najdi_souradnice(matice, znak2)
    if(dvojice_1[0] == dvojice_2[0]):
        dvojice_1 = (dvojice_1[0], (dvojice_1[1]+1) % 5)
        dvojice_2 = (dvojice_2[0], (dvojice_2[1]+1) % 5)
    elif(dvojice_1[1] == dvojice_2[1]):
        dvojice_1 = ((dvojice_1[0]+1)% 5, dvojice_1[1])
        dvojice_2 = ((dvojice_2[0]+1)% 5, dvojice_2[1])
    else:
       mezistav = dvojice_1
       dvojice_1 = (dvojice_1[0], dvojice_2[1])
       dvojice_2 = (dvojice_2[0], mezistav[1])
    
    znaky: str = matice[dvojice_1[0]][dvojice_1[1]] + matice[dvojice_2[0]][dvojice_2[1]]
    return znaky

# de-transformace dvojic
def desifruj_dvojici(matice, znak1, znak2)->str:
    dvojice_1 = najdi_souradnice(matice,znak1)
    dvojice_2 = najdi_souradnice(matice, znak2)
    if(dvojice_1[0] == dvojice_2[0]):
        dvojice_1 = (dvojice_1[0], (dvojice_1[1]-1) % 5)
        dvojice_2 = (dvojice_2[0], (dvojice_2[1]-1) % 5)
    elif(dvojice_1[1] == dvojice_2[1]):
        dvojice_1 = ((dvojice_1[0]-1)% 5, dvojice_1[1])
        dvojice_2 = ((dvojice_2[0]-1)% 5, dvojice_2[1])
    else:
        mezistav = dvojice_1
        dvojice_1 = (dvojice_1[0], dvojice_2[1])
        dvojice_2 = (dvojice_2[0], mezistav[1])
    znaky_desifrovane : str = matice[dvojice_1[0]][dvojice_1[1]] + matice[dvojice_2[0]][dvojice_2[1]]
    return znaky_desifrovane


def bigramy(text : str)-> tuple[list[str], list[str]]:
    bigramy = []
    metadata = []
    i = 0
    while i < len(text):
        #posledni znak bez dvojice
        if(i == (len(text)-1)):
            znak = text[i]
            vypln = 'q' if znak == 'x' else 'x'
            bigramy.append(znak+vypln)
            #znaci vypln na konci
            metadata.append('xqx')
            i += 1
        # dva ruzne znaky (bez vyplne)
        elif text[i] != text[i+1]:
            bigramy.append(text[i:i+2])
            metadata.append('n')
            i += 2
        # dva stejne znaky 
        else:
            znak = text[i]
            vypln = 'q' if znak == 'x' else 'x'
            bigramy.append(znak+vypln)
            metadata.append('qxq')
            i += 1
    return bigramy, metadata
 
def sifrovaci_algoritmus(text: str,klic: str,parametr_CZ_EN: int) -> str:

    normalizovany_klic = ziskta_klic(klic, parametr_CZ_EN)
    filtrovany_text = filtrace_textu(text, parametr_CZ_EN)

    dvojice, metadata = bigramy(filtrovany_text)
    matice = tabulka(normalizovany_klic, parametr_CZ_EN)

    # zasifrovani pouze bigramu 
    sifrovane_telo = ""

    #prvni sifruje bigramy(oznacene jako dvojice)
    for dva in dvojice:
        sifrovane_telo += zasifruj_dvojici(matice, dva[0], dva[1])

    # kodovani metadat jednim znakem, vytvoreni hlavicky k poznani toho, jestli se jedna o vypln nebo ne
    # normalizace na jeden znak
    kodovani = {"n": "a","qxq": "b","xqx": "c"}


    zakodovana_metadata = "".join(kodovani[znacka] for znacka in metadata)

    # zde do hlavicky vlazim pocet bigramu a pocet zakodovanych metadat
    hlavicka = (zakoduj_pocet(len(dvojice), parametr_CZ_EN)+ zakodovana_metadata)

    # hlavicka musi mit sudy pocet
    if len(hlavicka) % 2 != 0:
        hlavicka += "z"

    # sifrovani hlavicky
    sifrovana_hlavicka = ""

    for i in range(0, len(hlavicka), 2):
        sifrovana_hlavicka += zasifruj_dvojici(matice, hlavicka[i], hlavicka[i+1])

    return sifrovana_hlavicka + sifrovane_telo
    
def desifrovaci_algoritmus(sifrovany_text: str, klic: str, parametr_CZ_EN: int) -> str:

    telo = "".join(sifrovany_text.split()).lower()

    if len(telo) < 4 or len(telo) % 2 != 0:
        raise ValueError("Neplatná délka šifrové zprávy.")

    normalizovany_klic = ziskta_klic(klic, parametr_CZ_EN)
    matice = tabulka(normalizovany_klic, parametr_CZ_EN)

    # prvni ctyry znaky urcuji pocet bigramu
    uvod = ""

    for i in range(0, 4, 2):
        uvod += desifruj_dvojici(matice, telo[i], telo[i+1])

    pocet = dekoduj_pocet(uvod, parametr_CZ_EN)

    # delka hlavicka v pripade dodatecneho doplneni
    delka_hlavicky = 4 + pocet + (pocet % 2)

    if len(telo) != delka_hlavicky + 2 * pocet:
        raise ValueError("Neplatná délka zprávy nebo nesprávný klíč.")

    # desifrovani zbyvale hlavicky
    hlavicka = uvod

    for i in range(4, delka_hlavicky, 2):
        hlavicka += desifruj_dvojici(matice, telo[i], telo[i+1])

    # dekodovani metadat
    reverzni_kodovani = {"a": "n","b": "qxq","c": "xqx"}

    kodovana_metadata = hlavicka[4:4+pocet]

    if any(z not in reverzni_kodovani for z in kodovana_metadata):
        raise ValueError("Poškozená metadata nebo nesprávný klíč.")

    if pocet % 2 and hlavicka[-1] != "z":
        raise ValueError("Neplatné zakončení hlavičky.")

    metadata = [reverzni_kodovani[z] for z in kodovana_metadata]

    # desifrovani samotneho textu
    sifrovane_telo = telo[delka_hlavicky:]
    surovy_text = ""

    for i in range(0, len(sifrovane_telo), 2):
        surovy_text += desifruj_dvojici(matice, sifrovane_telo[i], sifrovane_telo[i+1])

    # rekonstrukce vyplni
    obnoveny_text = odstran_Vyplne_podle_metadat(surovy_text, metadata)

    # obnoveni mezer a cislic
    return obnov_znaky(obnoveny_text)

#odstraneni vyplne
def odstran_Vyplne_podle_metadat(text: str, metadata: list[str])-> str:
    if len(text) != 2* len(metadata):
        raise ValueError("Počet metadat neodpovídá počtu bigramů.")
    vysledek = ""
    for i, znacka in enumerate(metadata):
        bigram = text[2*i:2*i+2]
        if znacka == 'n':
            vysledek += bigram
        elif znacka == "qxq" or znacka == "xqx":
            #druhy znak byl vlozen umele
            vysledek += bigram[0]
        else:
            raise ValueError("Neznámá značka metadat.")
    return vysledek

# obnoveni znaku
def obnov_znaky(text: str) -> str:
    cisla = ["xnulax", "xjednax", "xdvax", "xtrax","xctyrax", "xpetx", "xsestx","xsedmx", "xosmx", "xdevetx"]

    text = text.replace("xmezerax", " ")

    for i, reprezentace in enumerate(cisla):
        text = text.replace(reprezentace, str(i))

    return text
# po 5 tici
def formatovat_sifru(text: str) -> str:
    bloky = []

    for i in range(0, len(text), 5):
        bloky.append(text[i:i+5].upper())

    return " ".join(bloky)

def zakoduj_pocet(pocet: int, jazyk: int) -> str:
    vynechany = "i" if jazyk == 0 else "w"
    abeceda = "".join(z for z in string.ascii_lowercase if z != vynechany)

    if not 0 <= pocet < 25**4:
        raise ValueError("Příliš mnoho bigramů.")
    vysledek = ""
    #veta o delenio se zbytkem n = 25q +r,
    for _ in range(4):
        pocet, zbytek = divmod(pocet, 25)
        vysledek = abeceda[zbytek] + vysledek
    return vysledek


def dekoduj_pocet(text: str, jazyk: int) -> int:
    vynechany = "i" if jazyk == 0 else "w"
    abeceda = "".join(z for z in string.ascii_lowercase if z != vynechany)
    #hornerovo schema
    pocet = 0
    for znak in text:
        if znak not in abeceda:
            raise ValueError("Neplatný znak v hlavičce.")
        pocet = pocet * 25 + abeceda.index(znak)

    return pocet

