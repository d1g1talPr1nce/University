import tkinter as tk
from tkinter import messagebox
import random
from adfgvx import (vytvoreni_matice,filtrace_textu,ziskta_klic,substituce_difuze,transpozice_difuze,inverze_transpozice_difuze,inverze_substituce_difuze,obnov_znaky, povolena_abeceda)
import string
root = tk.Tk()
root.title("ADFG(V)X")
root.geometry("1100x740")
root.configure(bg="#0A100D")


# Rainfall 

canvas = tk.Canvas(root, bg="#0A100D", highlightthickness=0)
canvas.place(x=0, y=0, relwidth=1, relheight=1)

znaky = "ADFGVX0123456789"
barvy = ["#22C55E", "#A3E635", "#FACC15"]
sloupce = []

def vytvor_rainfall():
    sirka = canvas.winfo_width()
    vyska = canvas.winfo_height()

    for i in range(55):
        x = random.randint(10, max(10, sirka - 10))
        y = random.randint(-vyska, vyska)
        rychlost = random.uniform(2, 6)
        barva = random.choice(barvy)
        symboly = []

        for j in range(10):
            symbol = canvas.create_text(x, y - j * 20, text=random.choice(znaky), fill=barva if j == 0 else "#294533", font=("DejaVu Sans Mono", 13))
            symboly.append(symbol)

        sloupce.append((symboly, rychlost))


def animace():
    vyska = canvas.winfo_height()
    sirka = canvas.winfo_width()
    for symboly, rychlost in sloupce:
        for symbol in symboly:
            canvas.move(symbol, 0, rychlost)

            if random.random() < 0.04:
                canvas.itemconfig(symbol, text=random.choice(znaky))

        x, y = canvas.coords(symboly[0])

        if y > vyska + 200:
            nove_x = random.randint(10, max(10, sirka - 10))
            nove_y = random.randint(-300, -20)

            for j, symbol in enumerate(symboly):
                canvas.coords(symbol, nove_x, nove_y - j * 20)

    root.after(40, animace)

def spust_rainfall():
    vytvor_rainfall()
    animace()
    

def aktualizuj_zbyvajici_znaky(event=None):
    velikost = varianta.get()

    abeceda = povolena_abeceda(velikost, jazyk.get())

    pouzite = set()

    for radek in matrix_entries:
        for entry in radek:
            znak = entry.get().lower()

            if len(znak) == 1 and znak in abeceda:
                pouzite.add(znak)

    zbyvajici = [znak.upper() for znak in abeceda if znak not in pouzite]

    if zbyvajici:
        zbyvajici_label.config(text=" ".join(zbyvajici))
    else:
        zbyvajici_label.config(text="Žádné zbývající znaky")


def prepni_rezim():
    rezim = rezim_matice.get()

    for radek in matrix_entries:
        for entry in radek:
            if rezim == "random":
                entry.config(state="readonly")
            else:
                entry.config(state="normal")

    if rezim == "random":
        seed_entry.config(state="normal")
        generate_button.config(state="normal")
    else:
        seed_entry.config(state="disabled")
        generate_button.config(state="disabled")

    aktualizuj_zbyvajici_znaky()


def matice_gui():
    velikost = varianta.get()
    n = 5 if velikost == 0 else 6
    souradnice = "ADFGX" if velikost == 0 else "ADFGVX"

    for widget in matrix_frame.winfo_children():
        widget.destroy()

    matrix_entries.clear()

    for index, znak in enumerate(souradnice):
        tk.Label(matrix_frame, text=znak, bg="#214630",fg="#A3E635",width=3,font=("DejaVu Sans Mono", 12, "bold"),padx=3,pady=3).grid(row=index+1, column=0)

        tk.Label(matrix_frame,text=znak,bg="#214630",fg="#A3E635",width=3,font=("DejaVu Sans Mono", 12, "bold"),padx=3, pady=3).grid(row=0, column=index+1)

    for i in range(n):
        radek = []

        for j in range(n):
            entry = tk.Entry(matrix_frame,width=3,justify="center",bg="#0A100D",fg="#DCEBDD",readonlybackground="#0A100D",font=("DejaVu Sans Mono", 12, "bold"),state="readonly" if rezim_matice.get() == "random" else "normal")

            entry.grid(row=i+1, column=j+1, padx=3, pady=3)

            entry.bind("<KeyRelease>", aktualizuj_zbyvajici_znaky)
            entry.bind("<FocusOut>", aktualizuj_zbyvajici_znaky)

            radek.append(entry)

        matrix_entries.append(radek)

    aktualizuj_zbyvajici_znaky()


def generuj_matici():
    if rezim_matice.get() != "random":
        return

    try:
        seed = int(seed_entry.get())
    except ValueError:
        messagebox.showerror("Chyba", "Seed musí být celé číslo!")
        return

    velikost = varianta.get()
    matice = vytvoreni_matice(seed, velikost,jazyk.get())

    for i in range(len(matice)):
        for j in range(len(matice[i])):
            entry = matrix_entries[i][j]

            entry.config(state="normal")
            entry.delete(0, "end")
            entry.insert(0, matice[i][j])
            entry.config(state="readonly")

    aktualizuj_zbyvajici_znaky()

    return matice  


def nacist_matici():
    matice = []
    velikost = int(varianta.get())
    abeceda = povolena_abeceda(velikost, jazyk.get())
    pouzite = set()
    n = 5 if velikost == 0 else 6
    for i in range(0,n):
        radek : list = []
        for j in range(0,n):
            znak = matrix_entries[i][j].get().lower()

            if len(znak) != 1:
                messagebox.showerror("Chyba",f"Buňka [{i+1}, {j+1}] musí obsahovat právě jeden znak!" )
                return None
                
            if znak not in abeceda:
                messagebox.showerror("Chyba", f"Znak '{znak}' není povolený!")
                return None
            if znak in pouzite:
                messagebox.showerror("Chyba", f"Znak '{znak}' se v matici opakuje!")
                return None
            
            pouzite.add(znak)
            radek.append(znak)
        matice.append(radek)
    return matice
            
                
def zobraz_text(pole, text):
    pole.config(state="normal")
    pole.delete("1.0", "end")
    pole.insert("1.0", text)
    
def sifrovani_text():
    velikost = varianta.get()
    text = input_text.get("1.0", "end-1c")
    klic = ziskta_klic(klic_entry.get(), velikost, jazyk.get())
    
    if not text.strip():
        messagebox.showerror("Chyba", "Zadejte otevřený text!")
        return
    if not klic:
        messagebox.showerror("Chyba", "Zadejte platný klíč!")
        return
    
    matice = nacist_matici()
    
    if matice is None:
        return
    
    try: 
        filtrovany = filtrace_textu(text, velikost, jazyk.get())
        if not filtrovany:
            messagebox.showerror("Chyba", "Text neobsahuje povolené znaky")
            return
        
        substituce = substituce_difuze(matice, filtrovany, velikost)
        sifrovany = transpozice_difuze(substituce, klic)
        sifrovany_format = formatuj_sifrovany_text(sifrovany, klic)
        zobraz_text(filtered_text, filtrovany)
        zobraz_text(output_text, sifrovany_format)
        
    except (ValueError, IndexError) as e:
        messagebox.showerror("Chyba šifrovaní", str(e))


def desifrovani_text():
    velikost = varianta.get()
    text = input_text.get("1.0", "end-1c")
    klic = ziskta_klic(klic_entry.get(), velikost, jazyk.get())
    
    sifrovany = "".join(text.split()).upper()
    
    if not sifrovany:
        messagebox.showerror("Chyba", "Zadejte šifrovaný text!")
        return
    if not klic:
        messagebox.showerror("Chyba", "Zadejte klíč!")
        return

    souradnice = "ADFGX" if velikost == 0 else "ADFGVX"
    
    if any(znak not in souradnice for znak in sifrovany):
        messagebox.showerror("Chyba", "Šifrovaný text obsahuje nepovolené znaky!")
        return
    
    if(len(sifrovany) % 2 != 0):
        messagebox.showerror("Chyba", "Délka šifrového textu musí být sudá!")
        return
        
    matice = nacist_matici()
    
    if matice is None:
        return
    try:
        inverze_transpozice = inverze_transpozice_difuze(sifrovany, klic)
        filtrovany = inverze_substituce_difuze(inverze_transpozice, matice, velikost)
        otevreny_text = obnov_znaky(filtrovany, velikost, jazyk.get())
        zobraz_text(filtered_text, filtrovany)
        zobraz_text(output_text, otevreny_text)
    except (ValueError, IndexError) as e:
        messagebox.showerror("Chyba šifrování", str(e))
        
def zmena_varianty():
    stav = "normal" if varianta.get() == 0 else "disabled"

    cz_radio.config(state=stav)
    en_radio.config(state=stav)

    matice_gui()
    
    
def formatuj_sifrovany_text(sifrovany: str, klic: str) -> str:
    delka_klice = len(klic)

    if delka_klice == 0:
        raise ValueError("Klíč nesmí být prázdný!")

    pocet_radku, zbytek = divmod(len(sifrovany), delka_klice)

    # Puvodni indexy sloupcu v abecednim poradi klice
    serazene_indexy = sorted(range(delka_klice),key=lambda i: klic[i])

    sloupce = []
    pozice = 0

    for index in serazene_indexy:
        delka_sloupce = pocet_radku

        if index < zbytek:
            delka_sloupce += 1

        sloupec = sifrovany[pozice:pozice + delka_sloupce]

        if sloupec:
            sloupce.append(sloupec)

        pozice += delka_sloupce

    return " ".join(sloupce)
    
#hlavni framy

main_frame = tk.Frame(root, bg="#0A100D")
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.86, relheight=0.90)

header_frame = tk.Frame(main_frame, bg = "#0A100D")
header_frame.pack(fill="x", padx=20, pady=10)

config_frame = tk.Frame(main_frame, bg="#121D17", height=70)
content_frame = tk.Frame(main_frame, bg ="#121D17")
config_frame.pack(fill="x")
content_frame.pack(fill="both",expand=True)  


logo = """ █████╗ ██████╗ ███████╗ ██████╗ ██╗   ██╗██╗  ██╗
██╔══██╗██╔══██╗██╔════╝██╔════╝ ██║   ██║╚██╗██╔╝
███████║██║  ██║█████╗  ██║  ███╗██║   ██║ ╚███╔╝
██╔══██║██║  ██║██╔══╝  ██║   ██║╚██╗ ██╔╝ ██╔██╗
██║  ██║██████╔╝██║     ╚██████╔╝ ╚████╔╝ ██╔╝ ██╗
╚═╝  ╚═╝╚═════╝ ╚═╝      ╚═════╝   ╚═══╝  ╚═╝  ╚═╝"""

logo_label = tk.Label(header_frame, text = logo, font=("DejaVu Sans Mono", 8), fg="#A3E635", bg="#0A100D", justify="left")
logo_label.pack()

#klic a matice

config_inner = tk.Frame(config_frame, bg="#121D17")
config_inner.pack(anchor="w", padx=25, pady=12)
seed_frame = tk.Frame(config_frame, bg="#121D17")
seed_frame.pack(anchor="w", padx = 25, pady=(0,12))

tk.Label(config_inner, text="Key", bg="#121D17", fg="#A3E635", font=("DejaVu Sans Mono", 11, "bold")).pack(side="left", padx=(0,10))
klic_entry = tk.Entry(config_inner, width=28, bg="#0A100D", fg="#DCEBDD", insertbackground="#A3E635",font=("DejaVu Sans Mono", 11),relief="flat",bd=0,highlightthickness=1,highlightbackground="#294533",highlightcolor="#A3E635")
klic_entry.pack(side="left", ipady=8, padx=(0,25))

tk.Label(config_inner, text="Matrix Choose", bg="#121D17", fg="#A3E635", font=("DejaVu Sans Mono", 11, "bold")).pack(side="left", padx=(0,10))

varianta = tk.IntVar(value=0)
rezim_matice = tk.StringVar(value="random")
jazyk = tk.StringVar(value="CZ")

tk.Radiobutton(config_inner, text="ADFGX", command=zmena_varianty, variable=varianta, value=0,bg="#121D17",fg="#A3E635",activebackground="#121D17", activeforeground="#FACC15",selectcolor="#0A100D", font=("DejaVu Sans Mono", 10), highlightthickness=0, bd=0).pack(side="left", padx = 5)
tk.Radiobutton(config_inner, text="ADFGVX",command=zmena_varianty, variable=varianta, value=1, bg="#121D17", fg="#A3E635", activebackground="#121D17", activeforeground="#FACC15", selectcolor="#0A100D", font=("DejaVu Sans Mono", 10),highlightthickness=0, bd=0).pack(side="left", padx=5)

tk.Label(seed_frame, text = "Seed",bg="#121D17", fg="#A3E635", font=("DejaVu Sans Mono", 11, "bold")).pack(side="left", padx=(0,10))
seed_entry = tk.Entry(seed_frame, width=28, bg="#0A100D", fg="#DCEBDD", insertbackground="#A3E635",font=("DejaVu Sans Mono", 11),relief="flat",bd=0,highlightthickness=1,highlightbackground="#294533",highlightcolor="#A3E635")
seed_entry.pack(side="left", ipady=8, padx=(0,25))

generate_button = tk.Button(seed_frame, text="Generate", command=generuj_matici, bg="#214630", fg="#A3E635", activebackground="#306B42", activeforeground="#FACC15", relief="flat", cursor="hand2",font=("DejaVu Sans Mono", 10, "bold"))
generate_button.pack(side="left", padx=(0,10))

tk.Label(seed_frame, text="Language:", bg="#121D17", fg ="#A3E635", font=("DejaVu Sans Mono",10, "bold")).pack(side="left", padx=(15,5))
cz_radio = tk.Radiobutton(seed_frame,text="CZ",variable=jazyk,value="CZ",command=matice_gui,bg="#121D17",fg="#A3E635",selectcolor="#0A100D",activebackground="#121D17")
cz_radio.pack(side="left", padx=5)

en_radio = tk.Radiobutton(seed_frame,text="EN",variable=jazyk,value="EN",command=matice_gui,bg="#121D17",fg="#A3E635",selectcolor="#0A100D",activebackground="#121D17")
en_radio.pack(side="left", padx=5)

left_frame = tk.Frame(content_frame, bg="#121D17")
left_frame.pack(side="left", fill = "both", expand=True, padx=(10,5))

tk.Label(left_frame, text="Input Open Text", bg="#A3E635", fg="#0A100D", font=("DejaVu Sans Mono", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
input_text = tk.Text(left_frame, height=3, width=1, bg="#0A100D", fg ="#DCEBDD", insertbackground="#A3E635", font = ("DejaVu Sans Mono",11), relief="flat", padx=10, pady=10,wrap = "word")
input_text.pack(fill="x", padx = 15, pady=(0,10))

tk.Label(left_frame, text="Filtered Open Text", bg="#A3E635", fg="#0A100D", font=("DejaVu Sans Mono", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
filtered_text = tk.Text(left_frame, height=2, width=1, bg="#0A100D", fg ="#DCEBDD", insertbackground="#A3E635", font = ("DejaVu Sans Mono",11), relief="flat", padx=10, pady=10,wrap = "word")
filtered_text.pack(fill = "x", padx=15, pady=(0,10))

tk.Label(left_frame, text="Output Text", bg ="#FACC15", fg = "#0A100D",font=("DejaVu Sans Mono", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
output_text = tk.Text(left_frame,height=3, width=1, bg="#0A100D", fg ="#DCEBDD", insertbackground="#A3E635", font = ("DejaVu Sans Mono",11), relief="flat", padx=10, pady=10,wrap = "word")
output_text.pack(fill = "x", padx=15, pady=(0,10))

button_frame = tk.Frame(left_frame, bg= "#121D17")
button_frame.pack(fill="x", padx=15, pady=8)

tk.Button(button_frame, text="Encrypt",command=sifrovani_text, bg="#214630", fg="#A3E635", activebackground="#306B42", activeforeground="#FACC15",relief="flat", cursor = "hand2",font=("DejaVu Sans Mono", 10, "bold")).pack(side="left", fill="x", expand=True)
tk.Button(button_frame, text ="Decrypt",command=desifrovani_text,bg="#493D18", fg="#FACC15", activebackground="#695522", activeforeground="#FFFFFF",relief="flat", cursor = "hand2",font=("DejaVu Sans Mono", 10, "bold")).pack(side="left", fill="x", expand=True)

right_frame = tk.Frame(content_frame, bg= "#121D17")
right_frame.pack(side="left", fill = "both", expand=True, padx=(10,5))

tk.Label(right_frame, text= "Substitution Matrix", bg="#121D17", fg="#A3E635", font=("DejaVu Sans Mono", 11, "bold")).pack(anchor="w", padx=15, pady=(10,5))
matrix_frame = tk.Frame(right_frame, bg= "#121D17")
matrix_frame.pack(anchor="center", padx=15, pady=(0, 10))

mode_frame = tk.Frame(right_frame, bg="#121D17")
mode_frame.pack(anchor="center", pady=(10, 15))

tk.Label(mode_frame, text="Matrix Mode:", bg="#121D17", fg="#A3E635", font=("DejaVu Sans Mono", 11, "bold")).pack(side="left", padx=10)
tk.Radiobutton(mode_frame, text="Random", variable=rezim_matice, value="random", command=prepni_rezim,bg = "#121D17", fg="#A3E635", selectcolor="#0A100D", activebackground="#121D17", activeforeground="#FACC15").pack(side="left", padx=5)
tk.Radiobutton(mode_frame,text="Manual",variable=rezim_matice, value="manual",command=prepni_rezim,bg="#121D17",fg="#FACC15",selectcolor="#0A100D",activebackground="#121D17",activeforeground="#FACC15").pack(side="left", padx=5)

tk.Label(right_frame,text="REMAINING CHARACTERS",bg="#121D17",fg="#A3E635",font=("DejaVu Sans Mono", 11, "bold")).pack(anchor="w", padx=20, pady=(10, 5))

zbyvajici_label = tk.Label(right_frame,text="",bg="#0A100D",fg="#FACC15",font=("DejaVu Sans Mono", 11),wraplength=380,justify="left", padx=10, pady=10)
zbyvajici_label.pack(fill="x", padx=20)

matrix_entries = []
matice_gui()

root.after(100, spust_rainfall)
root.mainloop()
