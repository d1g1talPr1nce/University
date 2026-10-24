import random 
import string 
import math

def povolena_abeceda(velikost : int, jazyk : str = "CZ")-> str:
    if velikost == 0:
        vynechany = "w" if jazyk == "CZ" else "j"
        return string.ascii_lowercase.replace(vynechany, "")
    if velikost == 1:
        return string.ascii_lowercase + string.digits
    
    

def vytvoreni_matice(seed, velikost : int, jazyk: str = "CZ")->list:
    if(velikost == 0):#kontrola jestli se jedná o int
        #5x5
        if not isinstance(seed, int):
            raise ValueError("Nezadali jste INT!")
        #vytvoreni konkretniho seedu
        random.seed(seed)
        dovolene_znaky_matice = povolena_abeceda(velikost, jazyk)
        
        matice : list = []
        znaky_matice : list = random.sample(dovolene_znaky_matice, k= 25)
        #naplneni matice
        for i in range(0,5):
            matice.append(znaky_matice[i*5: 5 + (i*5)])
        return matice
    elif(velikost == 1):
        #6x6
        if not isinstance(seed, int):
            raise ValueError("Nezadali jste INT!")
        #vytvoreni konkretniho seedu
        random.seed(seed)
        dovolene_znaky : str = string.ascii_lowercase + "0123456789"
          
        matice : list = []
        znaky_matice : list = random.sample(dovolene_znaky, k= 36)
        #naplneni matice
        for i in range(0,6):
            matice.append(znaky_matice[i*6: 6 + (i*6)])
        return matice
    else:
        raise ValueError("Nepltaný výběr velikosti!")

def filtrace_textu(vstupni_text : str, velikost : int,jazyk: str = "CZ") -> str:
    if(velikost == 0):
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
        nahrazovany = "w" if jazyk == "CZ" else "j"
        nahrada = "v" if jazyk == "CZ" else "i"
        list_FL_map = [
        nahrada if znak == nahrazovany else znak for znak in list_FL    ]

        return "".join(list_FL_map)

    elif(velikost == 1):
        abeceda : list = list(string.ascii_lowercase)
        diakritia : list = ['ě','š','č','ř','ž','ý','á','í','é','ó', 'ů', 'ú', 'ď', 'ť', 'ň']
        bezdiakritiky : list = ['e', 's', 'c', 'r', 'z', 'y', 'a', 'i', 'e', 'o', 'u', 'u', 'd', 't', 'n']
        cislo : list = [str(i) for i in range(0,10)]

        #rozsireni abecedy o cislice pro matici 6x6
        abeceda = abeceda + cislo

        #inicializace promennych
        vstupni_text_lower = vstupni_text.lower()
        list_OT : list[str] = []
        list_FL : str = ""

        #uprava textu na povolene znaky
        for znak in vstupni_text_lower:
            if znak in diakritia:
                index = diakritia.index(znak)
                novy_znak = bezdiakritiky[index]
                list_OT.append(novy_znak)
            elif(znak == " "):
                list_OT.append("xmezerax")
            elif(znak not in diakritia and znak not in abeceda):
                continue
            else:
                list_OT.append(znak)

        string_OT = "".join(list_OT)
        list_FL += string_OT

        return list_FL
    else:
        raise ValueError("Nezadali jste správné číslo!")
        


def ziskta_klic(vstup_klic : str, velikost : int,jazyk: str = "CZ") -> str:
    if(velikost == 0):
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
        #substituce w za v
        for k in vstup_klic_dovolene_znaky:
            if k == ("w" if jazyk == "CZ" else "j"):
                k = "v" if jazyk == "CZ" else "i"
            vstup_klic_mapovani = vstup_klic_mapovani + k
            
        # odstraneni duplicit
        for znak in vstup_klic_mapovani: 
            if(znak not in unikatni_znaky_klic):
                unikatni_znaky_klic= unikatni_znaky_klic + znak
            else:
                continue
        
        return vstup_klic_mapovani
    elif(velikost == 1):
        if not isinstance(vstup_klic, str):
            print("Nezadali jste string, nebo se snažíte poškodit algoritmus! Program se vypne!")
            raise TypeError
                
        #filtr na klic
        abeceda : list = list(string.ascii_lowercase + string.digits)
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
                
        # odstraneni duplicit
        for znak in vstup_klic_dovolene_znaky: 
            if(znak not in unikatni_znaky_klic):
                unikatni_znaky_klic= unikatni_znaky_klic + znak
            else:
                continue
            
        return vstup_klic_dovolene_znaky
    else:
        raise ValueError("Nesprávné zadání velikosti")

def substituce_difuze(matice : list, otevreny_text_filtrovany : str,velikost : int)->str:
    if(velikost == 0):
        substituce_text : str = "ADFGX"
        zasubstituovany_text : str = ""
        for znak in otevreny_text_filtrovany:
            for i in range(0,5):
                for j in range(0,5):
                    if matice[i][j] == znak:
                        zasubstituovany_text = zasubstituovany_text + substituce_text[i] + substituce_text[j]
        return zasubstituovany_text
    elif(velikost == 1):
        substituce_text : str = "ADFGVX"
        zasubstituovany_text : str = ""
        for znak in otevreny_text_filtrovany:
            for i in range(0,6):
                for j in range(0,6):
                    if matice[i][j] == znak:
                        zasubstituovany_text = zasubstituovany_text + substituce_text[i] + substituce_text[j]
        return zasubstituovany_text
    else:
        raise ValueError("Neplatná velikost!")     

def transpozice_difuze(zasubstituovany_text : str, klic_filtrovany : str)->str:
    delka_klicoveho_slova : int = len(klic_filtrovany)
    if(delka_klicoveho_slova == 0):
        raise ValueError("Nezadali jste klíč!")
    delka_zasubstituovaneho_textu : int = len(zasubstituovany_text)
    pocet_radku = math.ceil(delka_zasubstituovaneho_textu / delka_klicoveho_slova)
    transpozicni_matice : list = []
    i : int = 0
    transpozicni_text : str = ""
    
    #presne rozdeleni do "matice" (grupa_[delka_klicoveho_slova]...)
    while i < delka_zasubstituovaneho_textu:
        transpozicni_text = transpozicni_text + zasubstituovany_text[i]
        #tohle nam garantuje to, ze se to vzdy appendne po delce klicoveho slova
        if(delka_klicoveho_slova == (len(transpozicni_text)) % (delka_klicoveho_slova+1)):
            transpozicni_matice.append(transpozicni_text)
            transpozicni_text :str = ""
        i += 1
    #kvuli tomu, ze pri poslednim doplneni, pokud to neni exaktni rovnost, tak if nikdy nenastane a tim padem bychom nedostali ten posledni retezec
    if(len(transpozicni_text) != 0):
        transpozicni_matice.append(transpozicni_text)
    
    #mapovani zmenenych indexu mezi filtrovanych klicem a klicem serazenym podle abecedy
    i = 0
    klic_podle_abecedy : str = "".join(sorted(klic_filtrovany))
    zmenene_indexy = dict(enumerate(sorted(range(len(klic_filtrovany)),key=lambda i: klic_filtrovany[i]
        )
    )
    )
    i =0
    j = 0
    vysledny_text : str = ""
    #prohozeni slupco podle abecedne serazeneho klice
    for j in range(delka_klicoveho_slova):
        #puvodni index sloupce z dictu
        index_sloupce = zmenene_indexy[j]
        #prochozeni vsech radku daneho sloupce
        for i in range(pocet_radku):
            #ochrana proti neexsitujicimu znaku
            if index_sloupce < len(transpozicni_matice[i]):
                vysledny_text += transpozicni_matice[i][index_sloupce]
    return vysledny_text

def inverze_transpozice_difuze(sifrovany_text : str, klic_filtrovany :str)->str:
        # opet dostanu stejnou permutaic jako u sifrovani pomoc transpozice, a diky tomu, ze permutace je vlastne bijektivni zobrazeni na stejno mnozine, existuje zde inverze        
        if(len(klic_filtrovany) == 0):
            raise ValueError("Nezadali jste klic!")
        
        vysledek_inverze : list[str] = [""] * len(klic_filtrovany)
        pozice = 0
        
        zmenene_indexy = dict(enumerate(sorted(range(len(klic_filtrovany)),key=lambda i: klic_filtrovany[i])))
        
        # Urceni pocet rozdeleni
        #pocet takovych radku, ktere maji vsechny hodnoty zaplnene (tedy jsou velikost stejne jako klic)
        i = 0
        # pocet prvku posledniho radku, tedy maji mensi pocet prvku nez klic a cislo j udava ten pocet (bude vzdycky jeden)
        j = 0
        while(True):
            if(len(sifrovany_text) >= len(klic_filtrovany)*(i+1)):
                i +=1
            else:
                #dopocitani poctu znaku na poslednim radku
                while(True):
                    if(len(sifrovany_text) != len(klic_filtrovany)*i + j):
                        j += 1
                    else:
                        break
                break
        pocet_radku = i if j == 0 else i+1 
        pocet_prvku_posledni_radek = j
        #obvnoveni puvodnich sloupco podle permutace
        for k in range(len(klic_filtrovany)):

            # zjisteni puvodniho indexu sloupce
            index_sloupce_nahradit = zmenene_indexy[k]

            # urceni poctu znaku konkretniho sloupce
            if index_sloupce_nahradit < j:
                pocet_znaku_sloupce = i + 1
            else:
                pocet_znaku_sloupce = i

            # vybrani prislusne casti sifrovaneho textu
            vysledek_inverze[index_sloupce_nahradit] = sifrovany_text[
                pozice:pozice + pocet_znaku_sloupce
            ]

            # posunuti pozice o pocet zpracovanych znaku
            pozice += pocet_znaku_sloupce
        
        konec_transpozice_text = ""
        #prochazeni jednotlivych radku
        for l in range(pocet_radku):
            #prochazeni sloupcu v puvodnim poradi
            for h in range(len(klic_filtrovany)):
                #kontrola existence znaku v danem sloupci
                if(l < len(vysledek_inverze[h])):
                    konec_transpozice_text += vysledek_inverze[h][l]    
        return konec_transpozice_text   
            
def inverze_substituce_difuze(konec_transpozice_text : str, matice : list,velikost : int)-> str:
    if(velikost == 0):
        substituce_text : str = "ADFGX"
        prepinani : int = 0
        otevreny_text : str = ""
        if(len(konec_transpozice_text) % 2 != 0):
            raise ValueError("Šifrovaný text není sudý!" )
        #najdu index radku a sloupce, to vlozim do matice a dostanu vystup
        for znak in konec_transpozice_text:
            if(prepinani == 0):
                index_radku = substituce_text.index(znak)
                prepinani = 1
                continue
            elif(prepinani == 1):
                index_sloupce = substituce_text.index(znak)
                otevreny_text = otevreny_text + matice[index_radku][index_sloupce]
                prepinani = 0
        return otevreny_text
    elif(velikost == 1):
        substituce_text : str = "ADFGVX"
        prepinani : int = 0
        otevreny_text : str = ""
        if(len(konec_transpozice_text) % 2 != 0):
            raise ValueError("Šifrovaný text není sudý!" )
        #najdu index radku a sloupce, to vlozim do matice a dostanu vystup
        for znak in konec_transpozice_text:
            if(prepinani == 0):
                index_radku = substituce_text.index(znak)
                prepinani = 1
                continue
            elif(prepinani == 1):
                index_sloupce = substituce_text.index(znak)
                otevreny_text = otevreny_text + matice[index_radku][index_sloupce]
                prepinani = 0
        return otevreny_text
    else:
        raise ValueError("Neplatná velikost!")
        
# obnoveni znaku
def obnov_znaky(text: str,velikost : int,jazyk: str = "CZ") -> str:
        if(velikost == 0):
            cisla = ["xnulax", "xjednax", "xdvax", "xtrax","xctyrax", "xpetx", "xsestx","xsedmx", "xosmx", "xdevetx"]
            if jazyk == "EN":
                cisla = [reprezentace.replace("j", "i") for reprezentace in cisla]
            text = text.replace("xmezerax", " ")

            for i, reprezentace in enumerate(cisla):
                text = text.replace(reprezentace, str(i))
        
            text = text.upper()
            return text
        elif(velikost == 1):
            text = text.replace("xmezerax", " ")
            text = text.upper()
            return text
        else:
            raise ValueError("Neplatná velikost!")
        
        

