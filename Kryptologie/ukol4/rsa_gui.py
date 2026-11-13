import tkinter as tk
from tkinter import messagebox
import random
import time
from rsa import (generovani_klicu, text_na_cisla, cisla_na_text, sifruj, desifruj, over_verejny_klic, over_soukromy_klic)

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

#Parametry prevodu textu
#znaku v bloku (zadani)
Z = 8
#bitu na znak (zvoleno, 8 * 14 = 112 bitu < n)
P = 14
#verejny exponent podle FIPS 186-5
E_STANDARD = 65537

root = tk.Tk()
root.title("RSA")
root.geometry("1280x860")
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


def nacti_cislo(entry, nazev):
    #prevede obsah pole na cele cislo, jinak ValueError se srozumitelnou hlaskou
    hodnota = entry.get().strip()
    if not hodnota:
        raise ValueError(f"Pole {nazev} je prázdné.")
    try:
        return int(hodnota)
    except ValueError:
        raise ValueError(f"Pole {nazev} musí obsahovat celé číslo.")


def rozdel_bity(bity, delka):
    #"0000000100000100000001101000" -> "00000001000001 00000001101000"
    return " ".join(bity[i:i + delka] for i in range(0, len(bity), delka))


def bity_bloku(m):
    #stejny postup jako cisla_na_text: binarne a doplnit nuly na nasobek P
    bity = format(m, "b")
    delka = (len(bity) + P - 1) // P * P
    return bity.zfill(delka)


#Obsluha tlacitek

def generuj_klice_gui():
    start = time.perf_counter()
    klic = generovani_klicu(E_STANDARD)
    trvani = (time.perf_counter() - start) * 1000

    #vypis klicovych paru a mezivypoctu generovani
    nastav_pole(p_entry, klic["p"])
    nastav_pole(q_entry, klic["q"])
    nastav_pole(n_entry, klic["n"])
    nastav_pole(phi_entry, klic["phi"])
    nastav_pole(e_entry, klic["e"])
    nastav_pole(d_entry, klic["d"])
    cas_label.config(text=f"čas: {trvani:.1f} ms   |   n má {klic['n'].bit_length()} bitů")

    #predvyplneni poli pro sifrovani a desifrovani
    nastav_pole(sif_n_entry, klic["n"])
    nastav_pole(sif_e_entry, klic["e"])
    nastav_pole(des_n_entry, klic["n"])
    nastav_pole(des_d_entry, klic["d"])


def zmena_rezimu():
    if rezim.get() == "sifrovani":
        vstup_label.config(text="Otevřený text")
        vystup_label.config(text="Šifrový text (čísla po blocích)")
    else:
        vstup_label.config(text="Šifrový text (čísla po blocích, oddělená mezerou)")
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

    n = nacti_cislo(sif_n_entry, "n (veřejný klíč)")
    e = nacti_cislo(sif_e_entry, "e (veřejný klíč)")
    over_verejny_klic(n, e)
    if n.bit_length() <= Z * P:
        raise ValueError(f"Modul n musí mít víc než {Z * P} bitů, aby platilo m < n pro každý blok.")

    cisla = text_na_cisla(text, Z, P)
    sifra = sifruj(cisla, n, e)

    zobraz_text(vystup_text, " ".join(str(c) for c in sifra))

    #mezivypocty: blok -> kody -> bity -> m -> c
    radky = [f"ŠIFROVÁNÍ   c = m^e mod n", f"z = {Z} znaků/blok, P = {P} bitů/znak, blok = {Z * P} bitů, n = {n.bit_length()} bitů", f"počet bloků: {len(cisla)}", ""]
    for i, (m, c) in enumerate(zip(cisla, sifra)):
        blok = text[i * Z:(i + 1) * Z]
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

    n = nacti_cislo(des_n_entry, "n (soukromý klíč)")
    d = nacti_cislo(des_d_entry, "d (soukromý klíč)")
    over_soukromy_klic(n, d)

    cisla = desifruj(sifra, n, d)
    text = cisla_na_text(cisla, P)

    zobraz_text(vystup_text, text)

    #mezivypocty: c -> m -> bity -> kody -> text
    radky = [f"DEŠIFROVÁNÍ   m = c^d mod n", f"P = {P} bitů/znak, n = {n.bit_length()} bitů", f"počet bloků: {len(sifra)}", ""]
    for i, (c, m) in enumerate(zip(sifra, cisla)):
        bity = bity_bloku(m)
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
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.90, relheight=0.94)

#Hlavicka s logem
header_frame = tk.Frame(main_frame, bg=BG)
header_frame.pack(fill="x", padx=20, pady=(5, 10))

logo = """██████╗ ███████╗ █████╗
██╔══██╗██╔════╝██╔══██╗
██████╔╝███████╗███████║
██╔══██╗╚════██║██╔══██║
██║  ██║███████║██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝"""

logo_label = tk.Label(header_frame, text=logo, font=(FONT, 8), fg=AKCENT, bg=BG, justify="left")
logo_label.pack()


#Panel generovani klicu (vypis klicovych paru a mezivypoctu p, q, phi)
gen_frame = tk.Frame(main_frame, bg=PANEL)
gen_frame.pack(fill="x", pady=(0, 8))

generovat_button = tk.Button(gen_frame, text="Generovat klíče", command=generuj_klice_gui, bg=OKRAJ, fg=AKCENT, activebackground="#5A5A5A", activeforeground=AKCENT, relief="flat", cursor="hand2", font=(FONT, 10, "bold"))
generovat_button.grid(row=0, column=0, columnspan=2, padx=10, pady=8, sticky="w")

cas_label = tk.Label(gen_frame, text="", bg=PANEL, fg=TEXT, font=(FONT, 10))
cas_label.grid(row=0, column=2, columnspan=2, sticky="w")

#p
p_label = tk.Label(gen_frame, text="p", bg=PANEL, fg=AKCENT, font=(FONT, 11, "bold"))
p_label.grid(row=1, column=0, sticky="e", padx=(10, 5), pady=3)
p_entry = tk.Entry(gen_frame, width=24, bg=POLE, fg=TEXT, readonlybackground=POLE, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 11), state="readonly")
p_entry.grid(row=1, column=1, sticky="w", pady=3)

#q
q_label = tk.Label(gen_frame, text="q", bg=PANEL, fg=AKCENT, font=(FONT, 11, "bold"))
q_label.grid(row=1, column=2, sticky="e", padx=(10, 5), pady=3)
q_entry = tk.Entry(gen_frame, width=24, bg=POLE, fg=TEXT, readonlybackground=POLE, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 11), state="readonly")
q_entry.grid(row=1, column=3, sticky="w", pady=3)

#n
n_label = tk.Label(gen_frame, text="n", bg=PANEL, fg=AKCENT, font=(FONT, 11, "bold"))
n_label.grid(row=2, column=0, sticky="e", padx=(10, 5), pady=3)
n_entry = tk.Entry(gen_frame, width=40, bg=POLE, fg=TEXT, readonlybackground=POLE, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 11), state="readonly")
n_entry.grid(row=2, column=1, columnspan=3, sticky="w", pady=3)

#phi(n)
phi_label = tk.Label(gen_frame, text="φ(n)", bg=PANEL, fg=AKCENT, font=(FONT, 11, "bold"))
phi_label.grid(row=3, column=0, sticky="e", padx=(10, 5), pady=3)
phi_entry = tk.Entry(gen_frame, width=40, bg=POLE, fg=TEXT, readonlybackground=POLE, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 11), state="readonly")
phi_entry.grid(row=3, column=1, columnspan=3, sticky="w", pady=3)

#e
e_label = tk.Label(gen_frame, text="e", bg=PANEL, fg=AKCENT, font=(FONT, 11, "bold"))
e_label.grid(row=4, column=0, sticky="e", padx=(10, 5), pady=3)
e_entry = tk.Entry(gen_frame, width=24, bg=POLE, fg=TEXT, readonlybackground=POLE, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 11), state="readonly")
e_entry.grid(row=4, column=1, sticky="w", pady=3)

#d
d_label = tk.Label(gen_frame, text="d", bg=PANEL, fg=AKCENT, font=(FONT, 11, "bold"))
d_label.grid(row=4, column=2, sticky="e", padx=(10, 5), pady=3)
d_entry = tk.Entry(gen_frame, width=40, bg=POLE, fg=TEXT, readonlybackground=POLE, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 11), state="readonly")
d_entry.grid(row=4, column=3, sticky="w", pady=3)


#Obsah: vlevo klice a text, vpravo mezivypocty
content_frame = tk.Frame(main_frame, bg=PANEL)
content_frame.pack(fill="both", expand=True)

left_frame = tk.Frame(content_frame, bg=PANEL)
left_frame.pack(side="left", fill="both", expand=True, padx=(5, 5))

right_frame = tk.Frame(content_frame, bg=PANEL)
right_frame.pack(side="left", fill="both", expand=True, padx=(5, 5))


#Klice pro sifrovani a desifrovani
klice_frame = tk.Frame(left_frame, bg=PANEL)
klice_frame.pack(fill="x", pady=(8, 0))

#verejny klic (n, e)
verejny_label = tk.Label(klice_frame, text="Veřejný klíč (šifrování)", bg=PANEL, fg=AKCENT, font=(FONT, 10, "bold"))
verejny_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10)

sif_n_label = tk.Label(klice_frame, text="n", bg=PANEL, fg=AKCENT, font=(FONT, 11, "bold"))
sif_n_label.grid(row=1, column=0, sticky="e", padx=(10, 5), pady=3)
sif_n_entry = tk.Entry(klice_frame, width=40, bg=POLE, fg=TEXT, insertbackground=AKCENT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 11))
sif_n_entry.grid(row=1, column=1, sticky="w", pady=3)

#e je pevne podle FIPS 186-5, pole je jen pro cteni
sif_e_label = tk.Label(klice_frame, text="e", bg=PANEL, fg=AKCENT, font=(FONT, 11, "bold"))
sif_e_label.grid(row=2, column=0, sticky="e", padx=(10, 5), pady=3)
sif_e_entry = tk.Entry(klice_frame, width=10, bg=POLE, fg=TEXT, readonlybackground=POLE, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 11), state="readonly")
sif_e_entry.grid(row=2, column=1, sticky="w", pady=3)
nastav_pole(sif_e_entry, E_STANDARD)

#soukromy klic (n, d)
soukromy_label = tk.Label(klice_frame, text="Soukromý klíč (dešifrování)", bg=PANEL, fg=AKCENT, font=(FONT, 10, "bold"))
soukromy_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(6, 0))

des_n_label = tk.Label(klice_frame, text="n", bg=PANEL, fg=AKCENT, font=(FONT, 11, "bold"))
des_n_label.grid(row=4, column=0, sticky="e", padx=(10, 5), pady=3)
des_n_entry = tk.Entry(klice_frame, width=40, bg=POLE, fg=TEXT, insertbackground=AKCENT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 11))
des_n_entry.grid(row=4, column=1, sticky="w", pady=3)

des_d_label = tk.Label(klice_frame, text="d", bg=PANEL, fg=AKCENT, font=(FONT, 11, "bold"))
des_d_label.grid(row=5, column=0, sticky="e", padx=(10, 5), pady=3)
des_d_entry = tk.Entry(klice_frame, width=40, bg=POLE, fg=TEXT, insertbackground=AKCENT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 11))
des_d_entry.grid(row=5, column=1, sticky="w", pady=3)


#Prepinac sifrovani / desifrovani a tlacitka
rezim = tk.StringVar(value="sifrovani")

ovladani_frame = tk.Frame(left_frame, bg=PANEL)
ovladani_frame.pack(fill="x", padx=15, pady=(10, 0))

sifrovat_radio = tk.Radiobutton(ovladani_frame, text="Šifrovat", variable=rezim, value="sifrovani", command=zmena_rezimu, bg=PANEL, fg=TEXT, selectcolor=POLE, activebackground=PANEL, activeforeground=AKCENT, font=(FONT, 10), highlightthickness=0, bd=0)
sifrovat_radio.pack(side="left", padx=(0, 10))

desifrovat_radio = tk.Radiobutton(ovladani_frame, text="Dešifrovat", variable=rezim, value="desifrovani", command=zmena_rezimu, bg=PANEL, fg=TEXT, selectcolor=POLE, activebackground=PANEL, activeforeground=AKCENT, font=(FONT, 10), highlightthickness=0, bd=0)
desifrovat_radio.pack(side="left", padx=(0, 20))

spustit_button = tk.Button(ovladani_frame, text="Spustit", command=spust, bg=AKCENT, fg=BG, activebackground="#BFBFBF", activeforeground=BG, relief="flat", cursor="hand2", font=(FONT, 10, "bold"), padx=14)
spustit_button.pack(side="left", padx=(0, 10))

presun_button = tk.Button(ovladani_frame, text="Výstup → vstup", command=presun_vystup_do_vstupu, bg=OKRAJ, fg=AKCENT, activebackground="#5A5A5A", activeforeground=AKCENT, relief="flat", cursor="hand2", font=(FONT, 10, "bold"))
presun_button.pack(side="left")


#Vstup
vstup_label = tk.Label(left_frame, text="Otevřený text", bg=AKCENT, fg=BG, font=(FONT, 10, "bold"), padx=6)
vstup_label.pack(anchor="w", padx=15, pady=(10, 5))

vstup_frame = tk.Frame(left_frame, bg=PANEL)
vstup_frame.pack(fill="both", expand=True, padx=15, pady=(0, 5))
vstup_text = tk.Text(vstup_frame, height=4, width=1, bg=POLE, fg=TEXT, insertbackground=AKCENT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 11), padx=10, pady=10, wrap="word")
vstup_scroll = tk.Scrollbar(vstup_frame, command=vstup_text.yview, bg=PANEL, troughcolor=POLE, relief="flat")
vstup_text.config(yscrollcommand=vstup_scroll.set)
vstup_scroll.pack(side="right", fill="y")
vstup_text.pack(side="left", fill="both", expand=True)

#Vystup
vystup_label = tk.Label(left_frame, text="Šifrový text (čísla po blocích)", bg="#BFBFBF", fg=BG, font=(FONT, 10, "bold"), padx=6)
vystup_label.pack(anchor="w", padx=15, pady=(10, 5))

vystup_frame = tk.Frame(left_frame, bg=PANEL)
vystup_frame.pack(fill="both", expand=True, padx=15, pady=(0, 5))
vystup_text = tk.Text(vystup_frame, height=4, width=1, bg=POLE, fg=TEXT, insertbackground=AKCENT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 11), padx=10, pady=10, wrap="word")
vystup_scroll = tk.Scrollbar(vystup_frame, command=vystup_text.yview, bg=PANEL, troughcolor=POLE, relief="flat")
vystup_text.config(yscrollcommand=vystup_scroll.set)
vystup_scroll.pack(side="right", fill="y")
vystup_text.pack(side="left", fill="both", expand=True)


#Mezivypocty
mezivypocty_label = tk.Label(right_frame, text="Mezivýpočty", bg=AKCENT, fg=BG, font=(FONT, 10, "bold"), padx=6)
mezivypocty_label.pack(anchor="w", padx=15, pady=(10, 5))

mezivypocty_frame = tk.Frame(right_frame, bg=PANEL)
mezivypocty_frame.pack(fill="both", expand=True, padx=15, pady=(0, 5))
mezivypocty_text = tk.Text(mezivypocty_frame, height=20, width=1, bg=POLE, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=OKRAJ, highlightcolor=AKCENT, font=(FONT, 11), padx=10, pady=10, wrap="word", state="disabled")
mezivypocty_scroll = tk.Scrollbar(mezivypocty_frame, command=mezivypocty_text.yview, bg=PANEL, troughcolor=POLE, relief="flat")
mezivypocty_text.config(yscrollcommand=mezivypocty_scroll.set)
mezivypocty_scroll.pack(side="right", fill="y")
mezivypocty_text.pack(side="left", fill="both", expand=True)


#Spusteni
root.after(100, spust_rainfall)
root.mainloop()
