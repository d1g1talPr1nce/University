import tkinter as tk
from tkinter import messagebox
import random
import time
from rsa2 import (generovani_klicu, text_na_cisla, cisla_na_text, sifruj, desifruj, over_verejny_klic, over_soukromy_klic, parametry_bloku, pocet_kol_mr, P_UNICODE)

#Barvy (cerno-bila paleta)
#pozadi okna
BG = "#000000"
#pozadi panelu
PANEL = "#0F0F0F"
#pozadi vstupnich poli
POLE = "#050505"
#okraje, ztlumene prvky
OKRAJ = "#3A3A3A"
#bezny text
TEXT = "#E6E6E6"
#nadpisy, zvyrazneni
AKCENT = "#FFFFFF"
FONT = "DejaVu Sans Mono"

#verejny exponent podle FIPS 186-5
E_STANDARD = 65537
#velikosti klice v bitech: v prisnem rezimu jen hodnoty pro FIPS 186-5 (nlen >= 2048),
#mimo prisny rezim nabidka + libovolna hodnota napsana rucne
VELIKOSTI_FIPS = (2048, 3072, 4096)
VELIKOSTI_VSE = (128, 256, 512, 1024, 2048, 3072, 4096, 6144, 8192)
#minimum dane rsa2.generuj_pq; nad touto hranici se GUI zepta, protoze generovani trva dlouho
NLEN_MIN = 128
NLEN_VAROVANI = 8192

root = tk.Tk()
root.title("RSA 2")
root.geometry("1360x880")
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


#Pomocne funkce pro praci s hodnotami v polich

def nastav_pole(entry, hodnota):
    #zapis do Entry (i readonly): odemknout, prepsat, vratit puvodni stav
    puvodni_stav = entry.cget("state")
    entry.config(state="normal")
    entry.delete(0, "end")
    entry.insert(0, str(hodnota))
    entry.config(state=puvodni_stav)


def zobraz_text(pole, text):
    #zapis do Text widgetu (i disabled), puvodni stav se zachova
    puvodni_stav = pole.cget("state")
    pole.config(state="normal")
    pole.delete("1.0", "end")
    pole.insert("1.0", text)
    pole.config(state=puvodni_stav)


def nacti_cislo(pole, nazev):
    #prevede obsah Text widgetu na cele cislo
    #velka cisla se v poli zalamuji, proto se odstrani vsechny mezery a konce radku
    hodnota = "".join(pole.get("1.0", "end-1c").split())
    if not hodnota:
        raise ValueError(f"Pole {nazev} je prázdné.")
    try:
        return int(hodnota)
    except ValueError:
        raise ValueError(f"Pole {nazev} musí obsahovat celé číslo.")


def rozdel_bity(bity, delka):
    #"0000000100000100000001101000" -> "00000001000001 00000001101000"
    return " ".join(bity[i:i + delka] for i in range(0, len(bity), delka))


def bity_bloku(m, P):
    #stejny postup jako cisla_na_text: binarne a doplnit nuly na nasobek P
    bity = format(m, "b")
    delka = (len(bity) + P - 1) // P * P
    return bity.zfill(delka)


#Obsluha tlacitek

def zmena_prisnosti():
    #prisny rezim: vyber jen z velikosti podle FIPS, pole nejde prepsat
    #volny rezim: nabidka vsech velikosti a do pole lze napsat libovolne cislo
    if prisne_var.get():
        velikost_spin.config(values=VELIKOSTI_FIPS, state="normal")
        velikost_spin.delete(0, "end")
        velikost_spin.insert(0, "2048")
        velikost_spin.config(state="readonly")
    else:
        aktualni = velikost_spin.get()
        velikost_spin.config(state="normal", values=VELIKOSTI_VSE)
        velikost_spin.delete(0, "end")
        velikost_spin.insert(0, aktualni)


def nacti_velikost():
    #precte velikost klice z pole a overi ji, jinak ValueError
    hodnota = velikost_spin.get().strip()
    try:
        nlen = int(hodnota)
    except ValueError:
        raise ValueError("Velikost klíče musí být celé číslo (počet bitů).")
    if nlen < NLEN_MIN:
        raise ValueError(f"Velikost klíče musí být alespoň {NLEN_MIN} bitů.")
    if nlen % 2 != 0:
        raise ValueError("Velikost klíče musí být sudá (p a q mají každé nlen/2 bitů).")
    if prisne_var.get() and nlen < 2048:
        raise ValueError("FIPS 186-5 vyžaduje velikost klíče alespoň 2048 bitů.\nPro menší klíče vypněte přísný režim.")
    return nlen


def generuj_klice_gui():
    try:
        nlen = nacti_velikost()
    except ValueError as chyba:
        messagebox.showerror("Chyba", str(chyba))
        return
    if nlen > NLEN_VAROVANI:
        if not messagebox.askyesno("Velký klíč", f"Generování {nlen}bitového klíče může trvat i minuty a okno mezitím nebude reagovat.\nPokračovat?"):
            return
    prisne = prisne_var.get()

    #generovani velkych klicu trva i sekundy, zobrazime stav hned
    cas_label.config(text="generuji ...")
    root.update_idletasks()

    start = time.perf_counter()
    klic = generovani_klicu(nlen, E_STANDARD, prisne)
    trvani = (time.perf_counter() - start) * 1000

    n = klic["n"]
    z, P = parametry_bloku(n)
    kola = pocet_kol_mr(nlen // 2)
    rezim_text = "FIPS 186-5" if prisne else "experiment (není podle FIPS)"
    cas_label.config(text=f"čas: {trvani:.1f} ms  |  n: {n.bit_length()} bitů  |  MR kol: {kola}  |  blok: {z} znaků × {P} bitů  |  {rezim_text}")

    #vypis klicovych paru a mezivypoctu generovani
    radky = [f"p ({klic['p'].bit_length()} bitů):", str(klic["p"]), "", f"q ({klic['q'].bit_length()} bitů):", str(klic["q"]), "", f"n = p·q ({n.bit_length()} bitů):", str(n), "", "φ(n) = (p-1)(q-1):", str(klic["phi"]), "", "λ(n) = lcm(p-1, q-1):", str(klic["lambda"]), "", f"e: {klic['e']}", "", f"d = e^(-1) mod λ(n) ({klic['d'].bit_length()} bitů):", str(klic["d"]), "", f"veřejný klíč: (n, e)", f"soukromý klíč: (n, d)"]
    zobraz_text(klice_text, "\n".join(radky))

    #predvyplneni poli pro sifrovani a desifrovani
    zobraz_text(sif_n_text, str(n))
    nastav_pole(sif_e_entry, klic["e"])
    zobraz_text(des_n_text, str(n))
    zobraz_text(des_d_text, str(klic["d"]))


def zmena_rezimu():
    if rezim.get() == "sifrovani":
        vstup_label.config(text="Otevřený text")
        vystup_label.config(text="Šifrový text (čísla po blocích)")
    else:
        vstup_label.config(text="Šifrový text (čísla bloků oddělená mezerou)")
        vystup_label.config(text="Otevřený text")


def presun_vystup_do_vstupu():
    #vysledek se presune do vstupu a prepne se rezim
    vystup = vystup_text.get("1.0", "end-1c")
    zobraz_text(vstup_text, vystup)
    zobraz_text(vystup_text, "")
    if rezim.get() == "sifrovani":
        rezim.set("desifrovani")
    else:
        rezim.set("sifrovani")
    zmena_rezimu()


def sifrovani_gui():
    text = vstup_text.get("1.0", "end-1c")
    if not text:
        raise ValueError("Zadejte otevřený text.")

    n = nacti_cislo(sif_n_text, "n (veřejný klíč)")
    e = int(sif_e_entry.get())
    over_verejny_klic(n, e)

    #velikost bloku se odvodi z n: blok ma nejvyse nlen-1 bitu, tedy vzdy m < n
    z, P = parametry_bloku(n)

    cisla = text_na_cisla(text, z, P)
    sifra = sifruj(cisla, n, e)

    #kazdy blok na vlastni radek, at je videt deleni na bloky
    zobraz_text(vystup_text, "\n\n".join(str(c) for c in sifra))

    #mezivypocty: blok -> kody -> bity -> m -> c
    radky = [f"ŠIFROVÁNÍ   c = m^e mod n", f"z = {z} znaků/blok, P = {P} bitů/znak, blok = {z * P} bitů, n = {n.bit_length()} bitů", f"počet bloků: {len(cisla)}", ""]
    for i, (m, c) in enumerate(zip(cisla, sifra)):
        blok = text[i * z:(i + 1) * z]
        bity = "".join(format(ord(znak), f"0{P}b") for znak in blok)
        radky.append(f"Blok {i + 1}: {blok!r}")
        radky.append(f"  kódy : {' '.join(str(ord(znak)) for znak in blok)}")
        radky.append(f"  bity : {rozdel_bity(bity, P)}")
        radky.append(f"  m    : {m}")
        radky.append(f"  c    : {c}")
        radky.append("")
    zobraz_text(mezivypocty_text, "\n".join(radky))


def desifrovani_gui():
    vstup = vstup_text.get("1.0", "end-1c")
    casti = vstup.replace(",", " ").split()
    if not casti:
        raise ValueError("Zadejte šifrový text (čísla bloků oddělená mezerou).")
    try:
        sifra = [int(cast) for cast in casti]
    except ValueError:
        raise ValueError("Šifrový text musí obsahovat pouze celá čísla oddělená mezerou.")

    n = nacti_cislo(des_n_text, "n (soukromý klíč)")
    d = nacti_cislo(des_d_text, "d (soukromý klíč)")
    over_soukromy_klic(n, d)

    P = P_UNICODE
    cisla = desifruj(sifra, n, d)
    text = cisla_na_text(cisla, P)

    zobraz_text(vystup_text, text)

    #mezivypocty: c -> m -> bity -> kody -> text
    radky = [f"DEŠIFROVÁNÍ   m = c^d mod n", f"P = {P} bitů/znak, n = {n.bit_length()} bitů", f"počet bloků: {len(sifra)}", ""]
    for i, (c, m) in enumerate(zip(sifra, cisla)):
        bity = bity_bloku(m, P)
        blok = cisla_na_text([m], P)
        radky.append(f"Blok {i + 1}")
        radky.append(f"  c    : {c}")
        radky.append(f"  m    : {m}")
        radky.append(f"  bity : {rozdel_bity(bity, P)}")
        radky.append(f"  kódy : {' '.join(str(ord(znak)) for znak in blok)}")
        radky.append(f"  text : {blok!r}")
        radky.append("")
    zobraz_text(mezivypocty_text, "\n".join(radky))


def spust():
    #jedno tlacitko, rezim urcuje prepinac (zadani: prepinac sifrovani / desifrovani)
    try:
        if rezim.get() == "sifrovani":
            sifrovani_gui()
        else:
            desifrovani_gui()
    except ValueError as chyba:
        zobraz_text(mezivypocty_text, "")
        messagebox.showerror("Chyba", str(chyba))


#Rozvrzeni okna

main_frame = tk.Frame(root, bg=BG)
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.94, relheight=0.95)

#Hlavicka s logem
header_frame = tk.Frame(main_frame, bg=BG)
header_frame.pack(fill="x", pady=(0, 6))

logo = """██████╗ ███████╗ █████╗     ██████╗
██╔══██╗██╔════╝██╔══██╗    ╚════██╗
██████╔╝███████╗███████║     █████╔╝
██╔══██╗╚════██║██╔══██║    ██╔═══╝
██║  ██║███████║██║  ██║    ███████╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚══════╝"""

logo_label = tk.Label(header_frame, text=logo, font=(FONT, 7), fg=AKCENT, bg=BG, justify="left")
logo_label.pack()


#Ovladani generovani: velikost klice, prisny rezim, tlacitko, cas
gen_frame = tk.Frame(main_frame, bg=PANEL)
gen_frame.pack(fill="x", pady=(0, 6))

velikost_label = tk.Label(gen_frame, text="Velikost klíče (bity)", bg=PANEL, fg=AKCENT, font=(FONT, 10, "bold"))
velikost_label.pack(side="left", padx=(10, 5), pady=8)

#Spinbox: sipkami se listuje nabidkou, ve volnem rezimu se do nej da i psat
velikost_spin = tk.Spinbox(gen_frame, values=VELIKOSTI_FIPS, width=7, bg=POLE, fg=TEXT, readonlybackground=POLE, buttonbackground=OKRAJ, insertbackground=AKCENT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 10), justify="center", wrap=True)
velikost_spin.pack(side="left", padx=(0, 15), ipady=3)
velikost_spin.delete(0, "end")
velikost_spin.insert(0, "2048")
velikost_spin.config(state="readonly")

prisne_var = tk.BooleanVar(value=True)
prisne_check = tk.Checkbutton(gen_frame, text="Přísně podle FIPS 186-5", variable=prisne_var, command=zmena_prisnosti, bg=PANEL, fg=TEXT, selectcolor=POLE, activebackground=PANEL, activeforeground=AKCENT, font=(FONT, 10), highlightthickness=0, bd=0)
prisne_check.pack(side="left", padx=(0, 15))

generovat_button = tk.Button(gen_frame, text="Generovat klíče", command=generuj_klice_gui, bg=OKRAJ, fg=AKCENT, activebackground="#5A5A5A", activeforeground=AKCENT, relief="flat", cursor="hand2", font=(FONT, 10, "bold"))
generovat_button.pack(side="left", padx=(0, 15))

cas_label = tk.Label(gen_frame, text="", bg=PANEL, fg=TEXT, font=(FONT, 9))
cas_label.pack(side="left")


#Obsah: tri sloupce (klice | text | mezivypocty)
content_frame = tk.Frame(main_frame, bg=PANEL)
content_frame.pack(fill="both", expand=True)

klice_frame = tk.Frame(content_frame, bg=PANEL)
klice_frame.pack(side="left", fill="both", expand=True, padx=(5, 5))

text_frame = tk.Frame(content_frame, bg=PANEL)
text_frame.pack(side="left", fill="both", expand=True, padx=(5, 5))

mezi_frame = tk.Frame(content_frame, bg=PANEL)
mezi_frame.pack(side="left", fill="both", expand=True, padx=(5, 5))


#Sloupec 1: vypis klicovych paru a pole klicu

#vypis vygenerovanych hodnot (p, q, n, phi, lambda, e, d)
klice_label = tk.Label(klice_frame, text="Klíčové páry a mezivýpočty generování", bg=AKCENT, fg=BG, font=(FONT, 10, "bold"), padx=6)
klice_label.pack(anchor="w", padx=10, pady=(10, 5))

klice_vypis_frame = tk.Frame(klice_frame, bg=PANEL)
klice_vypis_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))
klice_text = tk.Text(klice_vypis_frame, height=10, width=1, bg=POLE, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 9), padx=8, pady=8, wrap="char", state="disabled")
klice_scroll = tk.Scrollbar(klice_vypis_frame, command=klice_text.yview, bg=PANEL, troughcolor=POLE, relief="flat")
klice_text.config(yscrollcommand=klice_scroll.set)
klice_scroll.pack(side="right", fill="y")
klice_text.pack(side="left", fill="both", expand=True)

#verejny klic (n, e)
verejny_label = tk.Label(klice_frame, text="Veřejný klíč (šifrování)", bg=PANEL, fg=AKCENT, font=(FONT, 10, "bold"))
verejny_label.pack(anchor="w", padx=10, pady=(6, 2))

sif_n_label = tk.Label(klice_frame, text="n", bg=PANEL, fg=AKCENT, font=(FONT, 10, "bold"))
sif_n_label.pack(anchor="w", padx=10)
sif_n_text = tk.Text(klice_frame, height=3, width=1, bg=POLE, fg=TEXT, insertbackground=AKCENT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 9), padx=6, pady=4, wrap="char")
sif_n_text.pack(fill="x", padx=10, pady=(0, 3))

#e je pevne podle FIPS 186-5, pole je jen pro cteni
sif_e_frame = tk.Frame(klice_frame, bg=PANEL)
sif_e_frame.pack(anchor="w", padx=10, pady=(0, 3))
sif_e_label = tk.Label(sif_e_frame, text="e", bg=PANEL, fg=AKCENT, font=(FONT, 10, "bold"))
sif_e_label.pack(side="left", padx=(0, 8))
sif_e_entry = tk.Entry(sif_e_frame, width=10, bg=POLE, fg=TEXT, readonlybackground=POLE, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 10), state="readonly")
sif_e_entry.pack(side="left")
nastav_pole(sif_e_entry, E_STANDARD)

#soukromy klic (n, d)
soukromy_label = tk.Label(klice_frame, text="Soukromý klíč (dešifrování)", bg=PANEL, fg=AKCENT, font=(FONT, 10, "bold"))
soukromy_label.pack(anchor="w", padx=10, pady=(6, 2))

des_n_label = tk.Label(klice_frame, text="n", bg=PANEL, fg=AKCENT, font=(FONT, 10, "bold"))
des_n_label.pack(anchor="w", padx=10)
des_n_text = tk.Text(klice_frame, height=3, width=1, bg=POLE, fg=TEXT, insertbackground=AKCENT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 9), padx=6, pady=4, wrap="char")
des_n_text.pack(fill="x", padx=10, pady=(0, 3))

des_d_label = tk.Label(klice_frame, text="d", bg=PANEL, fg=AKCENT, font=(FONT, 10, "bold"))
des_d_label.pack(anchor="w", padx=10)
des_d_text = tk.Text(klice_frame, height=3, width=1, bg=POLE, fg=TEXT, insertbackground=AKCENT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 9), padx=6, pady=4, wrap="char")
des_d_text.pack(fill="x", padx=10, pady=(0, 10))


#Sloupec 2: prepinac, vstup a vystup
rezim = tk.StringVar(value="sifrovani")

ovladani_frame = tk.Frame(text_frame, bg=PANEL)
ovladani_frame.pack(fill="x", padx=10, pady=(10, 0))

sifrovat_radio = tk.Radiobutton(ovladani_frame, text="Šifrovat", variable=rezim, value="sifrovani", command=zmena_rezimu, bg=PANEL, fg=TEXT, selectcolor=POLE, activebackground=PANEL, activeforeground=AKCENT, font=(FONT, 10), highlightthickness=0, bd=0)
sifrovat_radio.pack(side="left", padx=(0, 10))

desifrovat_radio = tk.Radiobutton(ovladani_frame, text="Dešifrovat", variable=rezim, value="desifrovani", command=zmena_rezimu, bg=PANEL, fg=TEXT, selectcolor=POLE, activebackground=PANEL, activeforeground=AKCENT, font=(FONT, 10), highlightthickness=0, bd=0)
desifrovat_radio.pack(side="left", padx=(0, 15))

spustit_button = tk.Button(ovladani_frame, text="Spustit", command=spust, bg=AKCENT, fg=BG, activebackground="#BFBFBF", activeforeground=BG, relief="flat", cursor="hand2", font=(FONT, 10, "bold"), padx=14)
spustit_button.pack(side="left", padx=(0, 10))

presun_button = tk.Button(ovladani_frame, text="Výstup → vstup", command=presun_vystup_do_vstupu, bg=OKRAJ, fg=AKCENT, activebackground="#5A5A5A", activeforeground=AKCENT, relief="flat", cursor="hand2", font=(FONT, 10, "bold"))
presun_button.pack(side="left")

#vstup
vstup_label = tk.Label(text_frame, text="Otevřený text", bg=AKCENT, fg=BG, font=(FONT, 10, "bold"), padx=6)
vstup_label.pack(anchor="w", padx=10, pady=(10, 5))

vstup_frame = tk.Frame(text_frame, bg=PANEL)
vstup_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))
vstup_text = tk.Text(vstup_frame, height=6, width=1, bg=POLE, fg=TEXT, insertbackground=AKCENT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 10), padx=8, pady=8, wrap="word")
vstup_scroll = tk.Scrollbar(vstup_frame, command=vstup_text.yview, bg=PANEL, troughcolor=POLE, relief="flat")
vstup_text.config(yscrollcommand=vstup_scroll.set)
vstup_scroll.pack(side="right", fill="y")
vstup_text.pack(side="left", fill="both", expand=True)

#vystup
vystup_label = tk.Label(text_frame, text="Šifrový text (čísla po blocích)", bg="#BFBFBF", fg=BG, font=(FONT, 10, "bold"), padx=6)
vystup_label.pack(anchor="w", padx=10, pady=(10, 5))

vystup_frame = tk.Frame(text_frame, bg=PANEL)
vystup_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
vystup_text = tk.Text(vystup_frame, height=6, width=1, bg=POLE, fg=TEXT, insertbackground=AKCENT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 10), padx=8, pady=8, wrap="char")
vystup_scroll = tk.Scrollbar(vystup_frame, command=vystup_text.yview, bg=PANEL, troughcolor=POLE, relief="flat")
vystup_text.config(yscrollcommand=vystup_scroll.set)
vystup_scroll.pack(side="right", fill="y")
vystup_text.pack(side="left", fill="both", expand=True)


#Sloupec 3: mezivypocty sifrovani / desifrovani
mezivypocty_label = tk.Label(mezi_frame, text="Mezivýpočty", bg=AKCENT, fg=BG, font=(FONT, 10, "bold"), padx=6)
mezivypocty_label.pack(anchor="w", padx=10, pady=(10, 5))

mezivypocty_frame = tk.Frame(mezi_frame, bg=PANEL)
mezivypocty_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
mezivypocty_text = tk.Text(mezivypocty_frame, height=20, width=1, bg=POLE, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 9), padx=8, pady=8, wrap="char", state="disabled")
mezivypocty_scroll = tk.Scrollbar(mezivypocty_frame, command=mezivypocty_text.yview, bg=PANEL, troughcolor=POLE, relief="flat")
mezivypocty_text.config(yscrollcommand=mezivypocty_scroll.set)
mezivypocty_scroll.pack(side="right", fill="y")
mezivypocty_text.pack(side="left", fill="both", expand=True)


#Spusteni
root.after(100, spust_rainfall)
root.mainloop()
