import os
import random
import time
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox
from rsa import generovani_klicu
from podpis import hashSouboru, rozdeleniHasheBloky, podepsaniHashe
from soubory import (exportKlicu, nactiSoukromyKlic, nactiVerejnyKlic, podpisNaText,
                     vytvorZip, overZip, informaceOSouboru, citelnaVelikost)

#Barvy (cerno-bila paleta)
#pozadi okna
BG = "#000000"
#pozadi panelu
PANEL = "#0F0F0F"
#pozadi textovych poli
POLE = "#050505"
#okraje, ztlumene prvky
OKRAJ = "#3A3A3A"
#bezny text
TEXT = "#E6E6E6"
#popisky
TLUMENY = "#8C8C8C"
#nadpisy, zvyrazneni
AKCENT = "#FFFFFF"
#vysledek overeni
PLATNY = "#7DFFA0"
NEPLATNY = "#FF6B6B"
FONT = "DejaVu Sans Mono"

#verejny exponent podle FIPS 186-5
E_STANDARD = 65537

#co je prave nacteno (None = zatim nic)
stav = {"soukromy": None, "verejny": None, "soubor": None, "zip": None}

root = tk.Tk()
root.title("Elektronický podpis")
root.geometry("1280x900")
root.configure(bg=BG)


#Rainfall
canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
canvas.place(x=0, y=0, relwidth=1, relheight=1)

znaky = "01"
barvy = ["#FFFFFF", "#BFBFBF", "#8C8C8C"]
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
            symbol = canvas.create_text(x, y - j * 20, text=random.choice(znaky), fill=barva if j == 0 else "#2A2A2A", font=(FONT, 13))
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


#Pomocne funkce

def zobraz_text(pole, text):
    #zapis do Text widgetu (i disabled), puvodni stav se zachova
    puvodni_stav = pole.cget("state")
    pole.config(state="normal")
    pole.delete("1.0", "end")
    pole.insert("1.0", text)
    pole.config(state=puvodni_stav)


def slovnik_na_text(udaje):
    #{"Název": "a.txt", ...} -> "Název      a.txt\n..."
    return "\n".join(f"{klic:<26}{hodnota}" for klic, hodnota in udaje.items())


def popis_klice(cesta, n):
    return f"{os.path.basename(cesta)}   (n: {n.bit_length()} bitů)"


#Obsluha tlacitek: klice

def generuj_klice_gui():
    cesta = filedialog.asksaveasfilename(title="Uložit klíčový pár (vznikne .priv a .pub)", initialfile="klic")
    if not cesta:
        return
    zaklad = os.path.splitext(cesta)[0]

    start = time.perf_counter()
    klic = generovani_klicu(E_STANDARD)
    trvani = (time.perf_counter() - start) * 1000
    try:
        exportKlicu(klic, zaklad)
    except OSError as chyba:
        messagebox.showerror("Chyba", str(chyba))
        return

    stav["soukromy"] = (klic["n"], klic["d"])
    stav["verejny"] = (klic["n"], klic["e"])
    soukromy_stav.config(text=popis_klice(zaklad + ".priv", klic["n"]), fg=AKCENT)
    verejny_stav.config(text=popis_klice(zaklad + ".pub", klic["n"]), fg=AKCENT)

    radky = ["GENEROVÁNÍ KLÍČŮ", f"čas: {trvani:.1f} ms", "",
             f"p    = {klic['p']}",
             f"q    = {klic['q']}",
             f"n    = {klic['n']}   ({klic['n'].bit_length()} bitů)",
             f"φ(n) = {klic['phi']}",
             f"e    = {klic['e']}",
             f"d    = {klic['d']}", "",
             f"uloženo: {zaklad}.priv  (n, d)",
             f"         {zaklad}.pub   (n, e)"]
    zobraz_text(protokol_text, "\n".join(radky))


def nacti_soukromy_gui():
    cesta = filedialog.askopenfilename(title="Načíst soukromý klíč", filetypes=[("Soukromý klíč", "*.priv"), ("Všechny soubory", "*")])
    if not cesta:
        return
    try:
        n, d = nactiSoukromyKlic(cesta)
    except (ValueError, OSError) as chyba:
        messagebox.showerror("Chyba", str(chyba))
        return
    stav["soukromy"] = (n, d)
    soukromy_stav.config(text=popis_klice(cesta, n), fg=AKCENT)


def nacti_verejny_gui():
    cesta = filedialog.askopenfilename(title="Načíst veřejný klíč", filetypes=[("Veřejný klíč", "*.pub"), ("Všechny soubory", "*")])
    if not cesta:
        return
    try:
        n, e = nactiVerejnyKlic(cesta)
    except (ValueError, OSError) as chyba:
        messagebox.showerror("Chyba", str(chyba))
        return
    stav["verejny"] = (n, e)
    verejny_stav.config(text=popis_klice(cesta, n), fg=AKCENT)


#Obsluha tlacitek: podpis

def vyber_soubor_gui():
    cesta = filedialog.askopenfilename(title="Vybrat soubor k podepsání")
    if not cesta:
        return
    try:
        udaje = informaceOSouboru(cesta)
    except OSError as chyba:
        messagebox.showerror("Chyba", str(chyba))
        return
    stav["soubor"] = cesta
    zobraz_text(soubor_text, slovnik_na_text(udaje))


def podepis_gui():
    if stav["soubor"] is None:
        messagebox.showwarning("Chybí soubor", "Nejdřív vyberte soubor k podepsání.")
        return
    if stav["soukromy"] is None:
        messagebox.showwarning("Chybí klíč", "Nejdřív vygenerujte nebo načtěte soukromý klíč (.priv).")
        return

    nazev = os.path.basename(stav["soubor"])
    cesta_zipu = filedialog.asksaveasfilename(title="Uložit podepsaný archiv", initialfile=nazev + ".zip", defaultextension=".zip", filetypes=[("ZIP archiv", "*.zip")])
    if not cesta_zipu:
        return

    n, d = stav["soukromy"]
    try:
        h = hashSouboru(stav["soubor"])
        podpis = podepsaniHashe(h, n, d)
        podpis_text = podpisNaText(podpis)
        vytvorZip(stav["soubor"], podpis_text, cesta_zipu)
    except (ValueError, OSError) as chyba:
        messagebox.showerror("Chyba", str(chyba))
        return

    #mezivypocty: hash -> bloky m -> podpis s -> obsah .sign
    radky = ["PODPIS   s = m^d mod n", "", f"soubor   : {nazev}", f"SHA3-512 : {h.hex()}", ""]
    for k, (m, s) in enumerate(zip(rozdeleniHasheBloky(h), podpis)):
        radky.append(f"blok {k}:  m = {m}")
        radky.append(f"         s = {s}")
    radky += ["", f"{nazev}.sign:", podpis_text, "", f"uloženo: {cesta_zipu}"]
    zobraz_text(protokol_text, "\n".join(radky))

    #podepsany archiv se rovnou nabidne k overeni
    nastav_zip(cesta_zipu)
    messagebox.showinfo("Podepsáno", f"Archiv uložen:\n{cesta_zipu}")


#Obsluha tlacitek: overeni

def nastav_zip(cesta):
    #nacte obsah zipu a zobrazi ho; neplatny zip -> zipfile.BadZipFile
    with zipfile.ZipFile(cesta) as zf:
        obsah = zf.infolist()
    stav["zip"] = cesta
    udaje = {"Název": os.path.basename(cesta),
             "Cesta": os.path.abspath(cesta),
             "Velikost": citelnaVelikost(os.path.getsize(cesta))}
    radky = slovnik_na_text(udaje) + "\n\nObsah archivu:\n"
    radky += "\n".join(f"  {p.filename}  ({citelnaVelikost(p.file_size)})" for p in obsah)
    zobraz_text(zip_text, radky)
    vysledek_label.config(text="", bg=PANEL)


def vyber_zip_gui():
    cesta = filedialog.askopenfilename(title="Vybrat podepsaný archiv", filetypes=[("ZIP archiv", "*.zip"), ("Všechny soubory", "*")])
    if not cesta:
        return
    try:
        nastav_zip(cesta)
    except zipfile.BadZipFile:
        messagebox.showerror("Chyba", "Vybraný soubor není platný zip.")
    except OSError as chyba:
        messagebox.showerror("Chyba", str(chyba))


def over_gui():
    if stav["zip"] is None:
        messagebox.showwarning("Chybí archiv", "Nejdřív vyberte podepsaný archiv (.zip).")
        return
    if stav["verejny"] is None:
        messagebox.showwarning("Chybí klíč", "Nejdřív načtěte veřejný klíč (.pub).")
        return

    n, e = stav["verejny"]
    try:
        platny = overZip(stav["zip"], n, e)
    except (ValueError, OSError) as chyba:
        messagebox.showerror("Chyba", str(chyba))
        return

    if platny:
        vysledek_label.config(text="✔  PODPIS JE PLATNÝ", bg=PLATNY, fg=BG)
        zaver = "dokument je pravý a nezměněný"
    else:
        vysledek_label.config(text="✘  PODPIS NENÍ PLATNÝ", bg=NEPLATNY, fg=BG)
        zaver = "dokument byl změněn, nebo nebyl podepsán k tomuto veřejnému klíči"

    radky = ["OVĚŘENÍ   m = s^e mod n  ->  složený hash == SHA3-512(dokument) ?", "",
             f"archiv : {os.path.basename(stav['zip'])}",
             f"klíč   : n = {n}",
             f"         e = {e}", "",
             f"výsledek: {zaver}"]
    zobraz_text(protokol_text, "\n".join(radky))


#Rozvrzeni okna

main_frame = tk.Frame(root, bg=BG)
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.95)

#Hlavicka s logem
header_frame = tk.Frame(main_frame, bg=BG)
header_frame.pack(fill="x", padx=20, pady=(5, 8))

logo = """██████╗ ███████╗ █████╗
██╔══██╗██╔════╝██╔══██╗
██║  ██║███████╗███████║
██║  ██║╚════██║██╔══██║
██████╔╝███████║██║  ██║
╚═════╝ ╚══════╝╚═╝  ╚═╝"""

logo_label = tk.Label(header_frame, text=logo, font=(FONT, 8), fg=AKCENT, bg=BG, justify="left")
logo_label.pack()
podtitul_label = tk.Label(header_frame, text="SHA3-512 · ELEKTRONICKÝ PODPIS", font=(FONT, 10, "bold"), fg=TLUMENY, bg=BG)
podtitul_label.pack(pady=(4, 0))


#Panel klice
klice_frame = tk.Frame(main_frame, bg=PANEL, padx=12, pady=10)
klice_frame.pack(fill="x", pady=(0, 8))

klice_label = tk.Label(klice_frame, text=" KLÍČE ", bg=AKCENT, fg=BG, font=(FONT, 11, "bold"))
klice_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

tlacitka_klice_frame = tk.Frame(klice_frame, bg=PANEL)
tlacitka_klice_frame.grid(row=0, column=1, sticky="w", padx=15, pady=(0, 8))

generovat_button = tk.Button(tlacitka_klice_frame, text="Vygenerovat a uložit pár", command=generuj_klice_gui, bg=AKCENT, fg=BG, activebackground="#BFBFBF", activeforeground=BG, relief="flat", cursor="hand2", font=(FONT, 10, "bold"), padx=12, pady=4)
generovat_button.pack(side="left", padx=(0, 8))

nacti_priv_button = tk.Button(tlacitka_klice_frame, text="Načíst .priv", command=nacti_soukromy_gui, bg=OKRAJ, fg=AKCENT, activebackground="#5A5A5A", activeforeground=AKCENT, relief="flat", cursor="hand2", font=(FONT, 10, "bold"), padx=12, pady=4)
nacti_priv_button.pack(side="left", padx=(0, 8))

nacti_pub_button = tk.Button(tlacitka_klice_frame, text="Načíst .pub", command=nacti_verejny_gui, bg=OKRAJ, fg=AKCENT, activebackground="#5A5A5A", activeforeground=AKCENT, relief="flat", cursor="hand2", font=(FONT, 10, "bold"), padx=12, pady=4)
nacti_pub_button.pack(side="left")

soukromy_label = tk.Label(klice_frame, text="Soukromý klíč", bg=PANEL, fg=TLUMENY, font=(FONT, 10))
soukromy_label.grid(row=1, column=0, sticky="w")
soukromy_stav = tk.Label(klice_frame, text="— nenačten —", bg=PANEL, fg=OKRAJ, font=(FONT, 10, "bold"))
soukromy_stav.grid(row=1, column=1, sticky="w", padx=15)

verejny_label = tk.Label(klice_frame, text="Veřejný klíč", bg=PANEL, fg=TLUMENY, font=(FONT, 10))
verejny_label.grid(row=2, column=0, sticky="w")
verejny_stav = tk.Label(klice_frame, text="— nenačten —", bg=PANEL, fg=OKRAJ, font=(FONT, 10, "bold"))
verejny_stav.grid(row=2, column=1, sticky="w", padx=15)


#Stred: vlevo podpis, vpravo overeni
stred_frame = tk.Frame(main_frame, bg=BG)
stred_frame.pack(fill="x", pady=(0, 8))
stred_frame.columnconfigure(0, weight=1, uniform="sloupec")
stred_frame.columnconfigure(1, weight=1, uniform="sloupec")

#Panel podpis
podpis_frame = tk.Frame(stred_frame, bg=PANEL, padx=12, pady=10)
podpis_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

podpis_label = tk.Label(podpis_frame, text=" PODPIS ", bg=AKCENT, fg=BG, font=(FONT, 11, "bold"))
podpis_label.pack(anchor="w", pady=(0, 8))

vyber_soubor_button = tk.Button(podpis_frame, text="Vybrat soubor…", command=vyber_soubor_gui, bg=OKRAJ, fg=AKCENT, activebackground="#5A5A5A", activeforeground=AKCENT, relief="flat", cursor="hand2", font=(FONT, 10, "bold"), padx=12, pady=4)
vyber_soubor_button.pack(anchor="w")

soubor_text = tk.Text(podpis_frame, height=8, width=1, bg=POLE, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, font=(FONT, 10), padx=8, pady=8, wrap="char", state="disabled")
soubor_text.pack(fill="x", pady=8)
zobraz_text(soubor_text, "Žádný soubor nevybrán.")

podepsat_button = tk.Button(podpis_frame, text="Podepsat a uložit .zip", command=podepis_gui, bg=AKCENT, fg=BG, activebackground="#BFBFBF", activeforeground=BG, relief="flat", cursor="hand2", font=(FONT, 10, "bold"), padx=12, pady=4)
podepsat_button.pack(anchor="w")

#Panel overeni
overeni_frame = tk.Frame(stred_frame, bg=PANEL, padx=12, pady=10)
overeni_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

overeni_label = tk.Label(overeni_frame, text=" OVĚŘENÍ ", bg=AKCENT, fg=BG, font=(FONT, 11, "bold"))
overeni_label.pack(anchor="w", pady=(0, 8))

vyber_zip_button = tk.Button(overeni_frame, text="Vybrat .zip…", command=vyber_zip_gui, bg=OKRAJ, fg=AKCENT, activebackground="#5A5A5A", activeforeground=AKCENT, relief="flat", cursor="hand2", font=(FONT, 10, "bold"), padx=12, pady=4)
vyber_zip_button.pack(anchor="w")

zip_text = tk.Text(overeni_frame, height=8, width=1, bg=POLE, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, font=(FONT, 10), padx=8, pady=8, wrap="char", state="disabled")
zip_text.pack(fill="x", pady=8)
zobraz_text(zip_text, "Žádný archiv nevybrán.")

overeni_spodek_frame = tk.Frame(overeni_frame, bg=PANEL)
overeni_spodek_frame.pack(fill="x")

overit_button = tk.Button(overeni_spodek_frame, text="Ověřit podpis", command=over_gui, bg=AKCENT, fg=BG, activebackground="#BFBFBF", activeforeground=BG, relief="flat", cursor="hand2", font=(FONT, 10, "bold"), padx=12, pady=4)
overit_button.pack(side="left")

vysledek_label = tk.Label(overeni_spodek_frame, text="", bg=PANEL, font=(FONT, 12, "bold"), padx=10, pady=3)
vysledek_label.pack(side="left", padx=12)


#Protokol (mezivypocty posledni operace)
protokol_frame = tk.Frame(main_frame, bg=PANEL, padx=12, pady=10)
protokol_frame.pack(fill="both", expand=True)

protokol_label = tk.Label(protokol_frame, text=" PROTOKOL ", bg=AKCENT, fg=BG, font=(FONT, 11, "bold"))
protokol_label.pack(anchor="w", pady=(0, 8))

protokol_obal = tk.Frame(protokol_frame, bg=PANEL)
protokol_obal.pack(fill="both", expand=True)
protokol_text = tk.Text(protokol_obal, height=10, width=1, bg=POLE, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, font=(FONT, 10), padx=10, pady=10, wrap="char", state="disabled")
protokol_scroll = tk.Scrollbar(protokol_obal, command=protokol_text.yview, bg=PANEL, troughcolor=POLE, relief="flat")
protokol_text.config(yscrollcommand=protokol_scroll.set)
protokol_scroll.pack(side="right", fill="y")
protokol_text.pack(side="left", fill="both", expand=True)


#Spusteni
if __name__ == "__main__":
    root.after(100, spust_rainfall)
    root.mainloop()
