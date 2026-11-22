import base64
import binascii
import os
from datetime import datetime
import zipfile
from podpis import hashProudu, overeniHashe
from rsa import over_verejny_klic, over_soukromy_klic

PREFIX_KLICE = "RSA "


def ulozKlic(cesta: str, a: int, b: int) -> None:
    """Ulozi dvojici cisel (n,e) nebo (n,d)  ve tvaru 'RSA base64' """
    data = f"{a},{b}".encode("ascii")  # cisla ->text -> bajty
    obsah = PREFIX_KLICE + base64.b64encode(data).decode("ascii")
    with open(cesta, "w", encoding="ascii") as f:
        f.write(obsah)


def nactiKlic(cesta: str) -> tuple[int, int]:
    """Nacte dvojici cisel ze souboru 'RSA base64'
    jakykoliv jiny format je error"""
    try:
        with open(cesta, "r", encoding="ascii") as f:
            obsah = f.read().strip()
    except UnicodeDecodeError:
        raise ValueError("Soubor není textový - nejde o klíč.")

    if not obsah.startswith(PREFIX_KLICE):
        raise ValueError("Soubor nezačíná 'RSA' - nejde o klíč.")

    try:
        data = base64.b64decode(obsah[len(PREFIX_KLICE):], validate = True)
        a_text, b_text = data.decode("ascii").split(",")
        return int(a_text), int(b_text)
    except (binascii.Error, UnicodeDecodeError, ValueError):
        raise ValueError("Obsah klíče je poškozený.") 


def exportKlicu(klice: dict, cestaBezPripony: str) -> None:
    """Ulozi klicovy par: cesta.priv = (n,d) cesta.pub = (n,e) """
    ulozKlic(cestaBezPripony + ".priv", klice["n"], klice["d"])
    ulozKlic(cestaBezPripony + ".pub", klice["n"], klice["e"])


def nactiVerejnyKlic(cesta: str) -> tuple[int, int]:
    n, e = nactiKlic(cesta)
    over_verejny_klic(n, e)
    return n, e


def nactiSoukromyKlic(cesta: str) -> tuple[int, int]:
    n, d = nactiKlic(cesta)
    over_soukromy_klic(n, d)
    return n, d


PREFIX_PODPISU = "RSA_SHA3-512 "


def podpisNaText(podpis: list[int]) -> str:
    """[s0, ..., s4] -> 'RSA_SHA3-512 <base64>' (obsah souboru .sign)."""
    data = ",".join(str(s) for s in podpis).encode("ascii")   # cisla -> "s0,s1,..." -> bajty
    return PREFIX_PODPISU + base64.b64encode(data).decode("ascii")


def textNaPodpis(text: str) -> list[int]:
    """'RSA_SHA3-512 <base64>' -> [s0, ..., s4]. Spatny format -> ValueError."""
    text = text.strip()
    if not text.startswith(PREFIX_PODPISU):
        raise ValueError("Soubor nezačíná 'RSA_SHA3-512 ' – nejde o podpis.")
    try:
        data = base64.b64decode(text[len(PREFIX_PODPISU):], validate=True)
        return [int(cast) for cast in data.decode("ascii").split(",")]
    except (binascii.Error, UnicodeDecodeError, ValueError):
        raise ValueError("Obsah podpisu je poškozený.")


PRIPONA_PODPISU = ".sign"


def vytvorZip(cestaDokumentu: str, podpisText: str, cestaZipu: str) -> None:
    """Zabali dokument a jeho podpis do zipu: <nazev> + <nazev>.sign."""
    nazev = os.path.basename(cestaDokumentu)              # jen jmeno, bez slozek
    with zipfile.ZipFile(cestaZipu, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(cestaDokumentu, arcname=nazev)            # dokument z disku
        zf.writestr(nazev + PRIPONA_PODPISU, podpisText)   # podpis primo z textu


def overZip(cestaZipu: str, n: int, e: int) -> bool:
    """Overi podpis primo ze zipu, bez rozbalovani na disk.
    True/False = vysledek overeni; ValueError = zip nema ocekavanou strukturu."""
    try:
        with zipfile.ZipFile(cestaZipu, "r") as zf:
            jmena = zf.namelist()

            # podpis = .sign, ke kteremu v zipu existuje dokument se stejnym jmenem bez .sign
            podpisy = [j for j in jmena
                       if j.endswith(PRIPONA_PODPISU) and j[:-len(PRIPONA_PODPISU)] in jmena]
            if len(podpisy) != 1:
                raise ValueError("Zip musí obsahovat právě jeden dokument a jeho podpis .sign.")
            jmenoPodpisu = podpisy[0]
            jmenoDokumentu = jmenoPodpisu[:-len(PRIPONA_PODPISU)]

            try:
                podpisText = zf.read(jmenoPodpisu).decode("ascii")
            except UnicodeDecodeError:
                raise ValueError("Soubor .sign není textový.")
            podpis = textNaPodpis(podpisText)

            with zf.open(jmenoDokumentu) as f:
                h = hashProudu(f)  # hash rovnou z archivu

    except zipfile.BadZipFile:
        raise ValueError("Vybraný soubor není platný zip.")

    return overeniHashe(h, podpis, n, e)


def citelnaVelikost(bajty: int) -> str:
    """ 1785 -> '1.70 KiB (1785 B)' """
    jednotky = ["B", "KiB", "MiB", "GiB", "TiB"]
    hodnota = float(bajty)
    i = 0
    while hodnota >= 1024 and i < len(jednotky) - 1:
        hodnota /= 1024 
        i += 1
    presne = f"{bajty:,} B".replace(",", " ")
    return presne if i == 0 else f"{hodnota:.2f} {jednotky[i]} ({presne})"


def informaceOSouboru(cesta: str) -> dict:
    """Zakladni udaje o souboru pro zobrazeni v GUI."""
    stat = os.stat(cesta)   # jedno volani systemu pro vsechny udaje
    nazev = os.path.basename(cesta)
    pripona = os.path.splitext(nazev)[1].lower()  # ".pdf", nebo "" bez pripony
    formatData = "%d. %m. %Y %H:%M:%S"
    return {
        "Název": nazev,
        "Cesta": os.path.abspath(cesta),
        "Typ": pripona if pripona else "(bez přípony)",
        "Velikost": citelnaVelikost(stat.st_size),
        "Upraveno": datetime.fromtimestamp(stat.st_mtime).strftime(formatData),
        "Naposledy otevřeno": datetime.fromtimestamp(stat.st_atime).strftime(formatData),
        "Vytvořeno / změna metadat": datetime.fromtimestamp(stat.st_ctime).strftime(formatData),
    }





print(citelnaVelikost(500))          # 500 B
print(citelnaVelikost(1536))         # 1.50 KiB (1 536 B)
print(citelnaVelikost(5 * 1024**2))  # 5.00 MiB (5 242 880 B)
