import matplotlib.pyplot as plt 
import string
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


def eukliduv_rozsireny_algotimus(a : int, b : int, n : int) -> int:
    # Euklidův Algoritmus a rozšířený Euklidův algortimus pro inverzi a v okruhu Z(dve binarni operace)..
    
    alpha : int = a; beta : int = n; q : int = 0; r : int = 1;  inter_val :int = 0; a_inverze : int = 0; r_vysledek : int = 0; r_0 = 0; r_1 = 1;
    while(1):
        #soudělnost
        if(alpha == 0 or beta % alpha == 0 or r == 0):
            break
        #euklid algoritmus 
        r = beta % alpha
        inter_val = (beta -r)
        q = inter_val // alpha 
        beta = alpha*q + r
            
        #algoritmus inverze
        r_vysledek = r_0 - q *r_1
        r_0 = r_1
        r_1 = r_vysledek
         
        if(r != 0):
            beta = alpha
            alpha = r    
        if(0 < r < beta):
            continue
        else:
            return None  
    if(alpha != 1):
        return None    
    
    a_inverze = r_1 % 26
    return a_inverze


def sifrovani(vstupni_text : string, a : int , b : int , n :int) -> string:
    abeceda : list = list(string.ascii_lowercase)
    diakritia : list = ['ě','š','č','ř','ž','ý','á','í','é','ó']
    bezdiakritiky : list = ['e', 's', 'c', 'r', 'z', 'y', 'a', 'i', 'e', 'o']
    cislo : list = [str(i) for i in range(0,10)]    
    cislo_slovne : list = ["xnulax", "xjednax", "xdvax", "xtrix", "xctyrix", "xpetx", "xsestx", "xsedmx", "xosmx", "xdevetx", "xdesetx"]
    vstupni_text_lower = vstupni_text.lower()
    list_OT : string = []
    list_ST : string = []
    list_FL : string = ""
    mezi_vypocet : int = 0
    
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
        
    for znak in string_OT:
        for i in range(len(abeceda)):
            if(znak == abeceda[i]):
                mezi_vypocet = (a*i + b) % 26
                list_ST.append(abeceda[mezi_vypocet])
    string_ST = "".join(list_ST)
   
    blok_ST : string = ""
    for i in range(0, len(string_ST), 5):
        blok_ST += string_ST[i:i+5] + " "
        blok_ST =  blok_ST.upper()
    return  list_FL, blok_ST
                

def desifrovani(blok_ST : str, a : int, b : int,  n : int ) -> str:
    abeceda : list = list(string.ascii_lowercase)
    cislo_slovne : list = ["xnulax", "xjednax", "xdvax", "xtrix", "xctyrix", "xpetx", "xsestx", "xsedmx", "xosmx", "xdevetx", "xdesetx"]
    list_OT : list = []
    string_OT : str = ""
    a_inverze = eukliduv_rozsireny_algotimus(a,b,n)
    string_ST_bez_mezer : str = ""
    for znak in blok_ST:
        if (znak == " "):
            continue
        else:
            string_ST_bez_mezer = blok_ST.replace(" ", "")
    for znak in string_ST_bez_mezer:
        for i in range(len(abeceda)):
            if(znak == abeceda[i]):
                mezi_vypocet = (a_inverze*(i-b)) % 26
                list_OT.append(abeceda[mezi_vypocet])
    string_OT = "".join(list_OT)
    string_OT = string_OT.replace("xmezerax", " ")
    for znak in cislo_slovne:
        if(znak in string_OT):
            index = cislo_slovne.index(znak)
            string_OT = string_OT.replace(znak, f"{index}")
    string_OT = string_OT.upper()
    return string_OT
    

def sifrovani_tlacitko():
    abeceda : str = str(string.ascii_lowercase)
    sifrovana_abeceda = ""

    try:
        a = int(vstup_a.get())
        b = int(vstup_b.get())
    except ValueError:
        messagebox.showerror("Chyba", "Klíče 'a' a 'b' musí být celá čísla!")
        return 
    
    inverze = eukliduv_rozsireny_algotimus(a,b,26)
    if(a >26 or a < 0):
        messagebox.showerror("Chyba", "Špatně zvolený rozsah pro šifrovací klíč a!! a je platné pouze v rozmezí 0 < a <= 26.")
        okno.destroy()
        return
    if(b >26 or b < 0):
            messagebox.showerror("Chyba", "Špatně zvolený rozsah pro šifrovací klíč b!! b je platné pouze v rozmezí 0 < b <= 26.")
            okno.destroy()
            return
    if inverze is None:
            messagebox.showerror("Chyba", "Špatný výběr klíče a. Je soudělný s modulem, výsledek algoritmu je neplatný a kryptograficky není bezpečný! Zadejte nový klíč!")
            okno.destroy()
            return
    if(inverze < 0 or inverze > 26):
            messagebox.showerror("Chyba", "Problematické číslo pro inverzi a v okruhu Z, program se vypne.")
            okno.destroy()
            return              
     
    #sifrovaci abeceda pomocí ASCII
    for znak in abeceda:
            cislo_znaku_ascii = ord(znak) - 97
            nove_cislo = (a*cislo_znaku_ascii + b) % 26
            sifrovana_abeceda += chr(nove_cislo + 97)
    
    text_k_uprave = vstupni_text_sifrovani.get('1.0', tk.END).strip()
    if len(text_k_uprave) == 0:
        messagebox.showwarning("Pozor", "Není zadán žadný text k šifrování!")
        return
    filtr_text ,vysledek = sifrovani(text_k_uprave,a,b,26)
    
    vypis = (
        "! Výsledek šifrování !\n"
        f"Standardní abeceda: {abeceda}\n"
        f"Šifrovácí abeceda:  {sifrovana_abeceda}\n"
        f"Vyfiltrovaný text:  {filtr_text}\n"
        f"Zašifrovaný text:   {vysledek}\n"
    )
    
    text_vystup.delete("1.0", tk.END)
    text_vystup.insert(tk.END, vypis)


def desifrovani_tlacitko():
    try:
        a = int(vstup_a.get())
        b = int(vstup_b.get())
    except ValueError:
        messagebox.showerror("Chyba", "Klíče 'a' a 'b' musí být celá čísla!")
        return
    text_k_zasifrovani = vstupni_text_desifrovani.get("1.0", tk.END).strip()
    
    if len(text_k_zasifrovani) == 0:
        messagebox.showwarning("Pozor","Není zadán žadný text k dešifrování!")
        return
    vysledek_desifrovani = desifrovani(text_k_zasifrovani, a, b, 26)
    
    text_vystup.delete("1.0", tk.END)
    text_vystup.insert(tk.END, f"Výsledek dešifrování -- Dešifrovaný text:\n{vysledek_desifrovani} ")
    


BG_cerna = "#0d0d0d"
FG_neon = "#00ff41"
BG_pole = "#000000"
Border_zelena = "#008f11"
Font_Title = ("Courier New", 11, "bold")
FONT_TEXT = ("Consolas", 10)

okno = tk.Tk()
okno.title("Šifrovací algortimus - Afinní šifra")
okno.geometry("600x700")
okno.configure(bg="#0d0d0d")
#Rámec pro klíče
ramec_klice = tk.Frame(okno,bg=BG_cerna)
ramec_klice.pack(pady=10)

# Klíč A
tk.Label(ramec_klice, text="Klíč a:", bg=BG_cerna, fg = FG_neon, font=Font_Title).grid(row = 0, column=0)
vstup_a = tk.Entry(ramec_klice, width=10,bg = BG_pole,fg = FG_neon, font=Font_Title, insertbackground = FG_neon, relief="flat",highlightbackground =Border_zelena,highlightthickness=1 )
vstup_a.grid(row = 0, column = 1, padx = 5)

# Klíč B
tk.Label(ramec_klice, text="Klíč b:",bg=BG_cerna, fg = FG_neon, font=Font_Title).grid(row = 0, column=8)
vstup_b = tk.Entry(ramec_klice, width=10, bg = BG_pole,fg = FG_neon, font=Font_Title, insertbackground = FG_neon, relief="flat",highlightbackground =Border_zelena,highlightthickness=1)
vstup_b.grid(row =0, column =10, padx =5)

#Rámec pro text - šifrování
ramec_sifrovani = tk.LabelFrame(okno, text = "Zadejte text, který chcete zašifrovat:", bg = BG_cerna, fg= FG_neon, font=Font_Title,bd=1, relief="solid")
ramec_sifrovani.pack(fill = "x", padx = 20, pady = 5)

#Vstupní textové pole pro OT
vstupni_text_sifrovani = tk.Text(ramec_sifrovani, height=4, width=60,bg=BG_pole, fg =FG_neon, font=Font_Title, insertbackground=FG_neon,relief="flat") #proměná
vstupni_text_sifrovani.pack(pady=5)

#Tlačítko pro šifrování
tlacitko_sifrovat = tk.Button(ramec_sifrovani, text = "Zašifrovat text", bg=BG_cerna,fg = FG_neon,font = Font_Title,activebackground= FG_neon,activeforeground=BG_cerna, relief="solid",bd=1, command=sifrovani_tlacitko)
tlacitko_sifrovat.pack()

#Rámec pro text - dešifrování
ramec_desifrovani = tk.LabelFrame(okno, text = "Zadejte text, který chcete dešifrovat", padx=10, pady=10,bg = BG_cerna, fg= FG_neon, font=Font_Title,bd=1, relief="solid")
ramec_desifrovani.pack(fill = "x", padx=20, pady= 5)

#Textové pole, kde uživatel zadá, konrkétní text k dešifrování
vstupni_text_desifrovani = tk.Text(ramec_desifrovani, height=4, width=60,bg=BG_pole, fg =FG_neon, font=Font_Title, insertbackground=FG_neon,relief="flat") #proměná
vstupni_text_desifrovani.pack(pady=5)

#Tlacitko pro desifrovaní
tlacitko_desifrovat = tk.Button(ramec_desifrovani, text="Dešifrovat text", bg=BG_cerna,fg = FG_neon,font = Font_Title,activebackground= FG_neon,activeforeground=BG_cerna, relief="solid",bd=1, command= desifrovani_tlacitko)
tlacitko_desifrovat.pack()

#Ramec pro výstupní pole, kde budou všechny požadované věci vypsány
ramec_vystup = tk.LabelFrame(okno, text="Pole pro zobrazení výstupů:", padx=10, pady=10,bg=BG_cerna, fg=FG_neon, font=Font_Title, bd =1, relief="solid")
ramec_vystup.pack(fill="both", expand=True, padx=20, pady=10)

#Textové pole pro výsledek
text_vystup = tk.Text(ramec_vystup, height=10, width=60, bg=BG_pole, fg =FG_neon, font=Font_Title, insertbackground=FG_neon,relief="flat") #proměná
text_vystup.pack(fill="both", expand=True)

ascii_zamek = """
      .--------.
     / .------. \\
    / /        \\ \\
    | |        | |
   _| |________| |_
 .' |_|        |_| '.
 '._____ ____ _____.'
 |     .'____'.     |
 '.__.'.'    '.'.__.'
 '.__  |      |  __.'
 |   '.'.____.'.'   |
 '.____'.____.'____.'
 '.________________.'
 
   > Algoritmus pro zašifrovaní textu pomocí afinní šifry...
   > Autor: Jaroslav Zvoníček...
"""
text_vystup.insert(tk.END, ascii_zamek)
okno.mainloop()