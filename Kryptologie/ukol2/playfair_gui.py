
import tkinter as tk
from tkinter import messagebox
import random
from playfairmain import sifrovaci_algoritmus, formatovat_sifru, desifrovaci_algoritmus, ziskta_klic, tabulka, filtrace_textu, bigramy

root = tk.Tk()
root.title("PLAYFAIR")
root.geometry("1100x740")
root.configure(bg="#0a0f1f")


# Rainfall 

canvas = tk.Canvas(root, bg="#0a0f1f", highlightthickness=0)
canvas.place(x=0, y=0, relwidth=1, relheight=1)

znaky = "01ABCDEF789XYZλΣπ⊕"
barvy = ["#00e5ff", "#8b5cf6", "#6366f1"]
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
            symbol = canvas.create_text(x, y - j * 20, text=random.choice(znaky), fill=barva if j == 0 else "#253558", font=("DejaVu Sans Mono", 13))
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


#  Aplikacni cast 

def upozorni_na_klic():
    key = key_entry.get()
    vybrany_jazyk = jazyk.get()
    normalizovany_klic = ziskta_klic(key, vybrany_jazyk)

    if key.lower() != normalizovany_klic:
        messagebox.showwarning("ÚPRAVA KLÍČE", f"Zadaný klíč byl upraven.\n\nPůvodní: {key}\nPoužitý: {normalizovany_klic.upper()}\n\nNepovolené znaky byly odstraněny a klíč byl normalizován.")

def sifrovani_text():
    try:
        key = key_entry.get()
        vybrany_jazyk = jazyk.get()
        upozorni_na_klic()
        text = input_text.get("1.0", "end-1c")
        

        filtrovany = filtrace_textu(text, vybrany_jazyk)
        filtered_text.delete("1.0", "end")
        filtered_text.insert("1.0", filtrovany)
        dvojice, metadata = bigramy(filtrovany)
        sifra = sifrovaci_algoritmus(text, key, vybrany_jazyk)
        formatovana_sifra = formatovat_sifru(sifra)

        bigram_text.delete("1.0", "end")
        bigram_text.insert("1.0", " | ".join(dvojice))
        output_text.delete("1.0", "end")
        output_text.insert("1.0", formatovana_sifra)
    except (ValueError, TypeError) as e:
        messagebox.showerror("Chyba šifrování", str(e))


def desifrovani_text():
    try:
        key = key_entry.get()
        vybrany_jazyk = jazyk.get()
        upozorni_na_klic()
        sifrovany_text = input_text.get("1.0", "end-1c")
        otevreny_text = desifrovaci_algoritmus(sifrovany_text, key, vybrany_jazyk)
    
        filtered_text.delete("1.0", "end")
        bigram_text.delete("1.0", "end")
        output_text.delete("1.0", "end")
        output_text.insert("1.0", otevreny_text)
    except (ValueError, TypeError) as e:
        messagebox.showerror("Chyba dešifrovaní", str(e))

# dynamicka zmena matice
def aktulizuj_matici():
    key = key_entry.get()
    vybrany_jazyk = jazyk.get()
    normalizovany_klic = ziskta_klic(key, vybrany_jazyk)
    matice = tabulka(normalizovany_klic, vybrany_jazyk)
    for i in range(5):
        for j in range(5):
            matrix_labels[i][j].config(text=matice[i][j].upper())


#  Rozdeleni do hlavnich framu 

main_frame = tk.Frame(root, bg="#11182b")
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.86, relheight=0.90)

header_frame = tk.Frame(main_frame, bg="#11182b")
header_frame.pack(fill="x", padx=20, pady=10)

config_frame = tk.Frame(main_frame, bg="#11182b", height=70)
content_frame = tk.Frame(main_frame, bg="#11182b")
config_frame.pack(fill="x")
content_frame.pack(fill="both", expand=True)


#  ASCII logo XD 

logo = """██████╗ ██╗      █████╗ ██╗   ██╗███████╗ █████╗ ██╗██████╗
██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗██║██╔══██╗
██████╔╝██║     ███████║ ╚████╔╝ █████╗  ███████║██║██████╔╝
██╔═══╝ ██║     ██╔══██║  ╚██╔╝  ██╔══╝  ██╔══██║██║██╔══██╗
██║     ███████╗██║  ██║   ██║   ██║     ██║  ██║██║██║  ██║
╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝"""

logo_label = tk.Label(header_frame, text=logo, font=("DejaVu Sans Mono", 8), fg="#00ff88", bg="#11182b", justify="left")
logo_label.pack()



#Klic a jazyk

config_frame.configure(bg="#11182b")
config_inner = tk.Frame(config_frame, bg="#11182b")
config_inner.pack(anchor="w", padx=25, pady=12)

tk.Label(config_inner, text="KEY  //", bg="#11182b", fg="#00e5ff", font=("DejaVu Sans Mono", 11, "bold")).pack(side="left", padx=(0, 15))
key_entry = tk.Entry(config_inner, width=28, bg="#0a0f1f", fg="#00ff88", insertbackground="#00ff88", font=("DejaVu Sans Mono", 11), relief="flat", bd=0, highlightthickness=1, highlightbackground="#253558", highlightcolor="#00e5ff")
key_entry.pack(side="left", ipady=8, padx=(0, 25))

tk.Label(config_inner, text="LANGUAGE  //", bg="#11182b", fg="#00e5ff", font=("DejaVu Sans Mono", 10, "bold")).pack(side="left", padx=(0, 10))

jazyk = tk.IntVar(value=1)

tk.Radiobutton(config_inner, text="CZ", variable=jazyk, value=1, command=aktulizuj_matici, bg="#11182b", fg="#d8e6ff", selectcolor="#0a0f1f", activebackground="#11182b", activeforeground="#00e5ff", font=("DejaVu Sans Mono", 10), highlightthickness=0, bd=0).pack(side="left", padx=5)
tk.Radiobutton(config_inner, text="EN", variable=jazyk, value=0, command=aktulizuj_matici, bg="#11182b", fg="#d8e6ff", selectcolor="#0a0f1f", activebackground="#11182b", activeforeground="#00e5ff", font=("DejaVu Sans Mono", 10), highlightthickness=0, bd=0).pack(side="left", padx=5)



# levy frame


left_frame = tk.Frame(content_frame, bg="#11182b")
left_frame.pack(side="left", fill="both", expand=True, padx=(10, 5))

tk.Label(left_frame, text="01 // INPUT BUFFER", bg="#11182b", fg="#00e5ff", font=("DejaVu Sans Mono", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 5))

input_text = tk.Text(left_frame, height=8, bg="#0a0f1f", fg="#d8e6ff", insertbackground="#00e5ff", font=("DejaVu Sans Mono", 11), relief="flat", padx=10, pady=10)
input_text.pack(fill="x", padx=15, pady=(0, 10))


# tlacitka 

button_frame = tk.Frame(left_frame, bg="#11182b")
button_frame.pack(fill="x", padx=15, pady=8)

tlacitko_sifra = tk.Button(button_frame, text="Šifrování", command=sifrovani_text, bg="#103d30", fg="#00ff88", activebackground="#195a45", activeforeground="#00ff88", font=("DejaVu Sans Mono", 11, "bold"), relief="flat", cursor="hand2", pady=9, bd=0)
tlacitko_sifra.pack(side="left", fill="x", expand=True, padx=(0, 5))

tlacitko_desifrovat = tk.Button(button_frame, text="Dešifrování", command=desifrovani_text, bg="#302050", fg="#c4a5ff", activebackground="#48306d", activeforeground="#ffffff", font=("DejaVu Sans Mono", 11, "bold"), relief="flat", cursor="hand2", pady=9, bd=0)
tlacitko_desifrovat.pack(side="left", fill="x", expand=True, padx=(5, 0))


# Vystup

tk.Label(left_frame, text="02 // OUTPUT BUFFER", bg="#11182b", fg="#00e5ff", font=("DejaVu Sans Mono", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
output_text = tk.Text(left_frame, height=8, bg="#0a0f1f", fg="#d8e6ff", insertbackground="#00e5ff", font=("DejaVu Sans Mono", 11), relief="flat", padx=10, pady=10)
output_text.pack(fill="x", padx=15, pady=(0, 10))

# Pravy frame

right_frame = tk.Frame(content_frame, bg="#11182b")
right_frame.pack(side="right", fill="both", expand=True, padx=(5, 10))

tk.Label(right_frame, text="03 // PLAYFAIR MATRIX", bg="#11182b", fg="#00e5ff", font=("DejaVu Sans Mono", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
matrix_frame = tk.Frame(right_frame, bg="#11182b")
matrix_frame.pack(anchor="w", padx=15, pady=(5, 20))

tk.Label(right_frame, text="04 // BIGRAM ANALYSIS", bg="#11182b", fg="#00e5ff", font=("DejaVu Sans Mono", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
bigram_text = tk.Text(right_frame, height=8, bg="#0a0f1f", fg="#00e5ff", insertbackground="#00e5ff", font=("DejaVu Sans Mono", 11), wrap="word", relief="flat", padx=10, pady=10)
bigram_text.pack(fill="x", padx=15, pady=(0, 10))

# Matice

matrix_labels = []
key_entry.bind("<KeyRelease>", lambda event: aktulizuj_matici())
for i in range(5):
    radek_labels = []
    for j in range(5):
        label = tk.Label(matrix_frame, text="", width=3, bg="#0a0f1f", fg="#00e5ff", font=("DejaVu Sans Mono", 14, "bold"), padx=7, pady=7)
        label.grid(row=i, column=j, padx=3, pady=3)
        radek_labels.append(label)
        
    matrix_labels.append(radek_labels)
aktulizuj_matici()


# Filtrovany text
tk.Label(left_frame, text="05 // FILTERED TEXT", bg="#11182b", fg="#00e5ff", font=("DejaVu Sans Mono", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
filtered_text = tk.Text(left_frame, height=4, bg="#0a0f1f", fg="#00ff88", font=("DejaVu Sans Mono", 11), wrap="word", relief="flat", padx=10, pady=10)
filtered_text.pack(fill="x", padx=15, pady=(0, 10))

root.after(100, spust_rainfall)
root.mainloop()
