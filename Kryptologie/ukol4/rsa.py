import secrets
import math


# Generovani prvocisel: FIPS 186-5, priloha B.3.1 (Miller-Rabin) a A.1.3
def rozklad(w: int) -> tuple[int, int]:
    # FIPS 186-5, B.3.1, kroky 1-2: najde a, m takova, ze w - 1 = 2^a * m, m liche
    # w musi byt liche a w >= 5 (pro w = 3 je interval bazi 1 < b < w - 1 prazdny)
    if w % 2 == 0 or w < 5:
        raise ValueError("Kandidát (w) musí být lichý a w >= 5")
    m = w - 1
    a = 0
    # delim m dvema, dokud neni liche; a pocita pocet deleni
    while m % 2 == 0:
        a += 1
        m = m // 2
    return (a, m)


def miller_rabin(w: int, iterace: int) -> bool:
    # FIPS 186-5, B.3.1: True = pravdepodobne prvocislo, False = slozene
    # pravdepodobnost chyby je nejvyse 4^(-iterace)
    a, m = rozklad(w)     # kroky 1-2 (jednou pro vsechna kola)
    wlen = w.bit_length()    # krok 3: delka w v bitech
    for _ in range(iterace): # krok 4
        # kroky 4.1-4.2: nahodna baze z wlen bitu (B.2.1), zamitaci vyber 1 < b < w - 1
        while True:
            b = secrets.randbits(wlen)
            if 1 < b < w - 1:
                break
        z = pow(b, m, w)     # krok 4.3
        if z == 1 or z == w - 1: # krok 4.4: kolo proslo
            continue
        for _ in range(a - 1):   # krok 4.5: postupne umocnovani na druhou
            z = pow(z, 2, w)
            if z == w - 1:   # krok 4.5.2: kolo proslo
                break
            if z == 1:    # krok 4.5.3: netrivialni odmocnina z 1 -> slozene
                return False
        else:
            return False      # krok 4.6: smycka dobehla bez w - 1 -> slozene
    return True       # krok 5: vsechna kola prosla


def gcd(a: int, b: int) -> int:
    # Eukleiduv algoritmus: gcd(a, b) = gcd(b, a mod b), gcd(a, 0) = a
    while b != 0:
        a, b = b, a % b
    return a


def generuj_pq(e: int) -> tuple[int, int]:
    # FIPS 186-5, A.1.3: generovani nahodnych pravdepodobnych prvocisel p, q
    # Odchylky od standardu: rozsah 18 cifer dle zadani (misto nlen >= 2048),
    # krok 1 (nlen >= 2048) a kroky 4.4 / 5.4 (dolni mez) vynechany.
    # Analog nlen: n ma priblizne 120 bitu -> limity 5 * 120 = 600 a 10 * 120 = 1200.
    if e <= 2**16 or e >= 2**256 or e % 2 == 0:        # krok 2
        raise ValueError("Veřejný exponent e nesplňuje podmínky FIPS 186-5 (A.1.3, krok 2)")
    rng = secrets.SystemRandom()

    # Generovani p (kroky 4.1-4.7)
    i = 0    # krok 4.1
    while True:
        p = rng.randrange(10**17, 10**18)  # krok 4.2: 18 cifer
        if p % 2 == 0:   # krok 4.3: vynuceni lichosti
            p += 1
        if gcd(p - 1, e) == 1 and miller_rabin(p, 50):  # krok 4.5
            break
        i += 1        # krok 4.6
        if i >= 600:  # krok 4.7
            raise RuntimeError("Nepodařilo se najít prvočíslo p během 600 pokusů (A.1.3, krok 4.7)")

    # Generovani q (kroky 5.1-5.8)
    i = 0  # krok 5.1
    while True:
        q = rng.randrange(10**17, 10**18) # krok 5.2
        if q % 2 == 0:   # krok 5.3
            q += 1
        # krok 5.5: |p - q| <= 2^(nlen/2 - 100); pro nlen ~ 120 je prava strana 2^-40 < 1,
        # pro cela cisla to tedy plati prave kdyz p == q (zaroven pozadavek zadani na ruzna p, q)
        if p == q:
            continue
        if gcd(q - 1, e) == 1 and miller_rabin(q, 50):  # krok 5.6
            break
        i += 1               # krok 5.7
        if i >= 1200:    # krok 5.8
            raise RuntimeError("Nepodařilo se najít prvočíslo q během 1200 pokusů (A.1.3, krok 5.8)")

    return (p, q)


# Vypocet klicu: zadani kroky 2-5

def spocitej_n(p: int, q: int) -> int:
    # zadani, krok 2: modul n = p * q
    return p * q


def eulerova_funkce(p: int, q: int) -> int:
    # zadani, krok 3: phi(n) = (p - 1)(q - 1) pro n = p * q, p != q prvocisla
    return (p - 1) * (q - 1)


def over_e(e: int, phi: int) -> bool:
    # zadani, krok 4: 1 < e < phi a gcd(e, phi) = 1
    # Zaruceno konstrukci: gcd(p - 1, e) = gcd(q - 1, e) = 1 => gcd(e, (p - 1)(q - 1)) = 1.
    # Kontrola hlida, ze tento predpoklad skutecne plati.
    return 1 < e < phi and gcd(e, phi) == 1


def inverze(z: int, a: int) -> int:
    # FIPS 186-5, B.1: z^(-1) mod a pomoci rozsireneho Eukleidova algoritmu
    # i, j = posledni dva zbytky; y2, y1 = jejich koeficienty u z (invariant: i = z * y2 mod a)
    if not (0 < z < a):                          # krok 1
        raise ValueError("Musí platit 0 < z < a")
    i, j = a, z       # krok 2
    y2, y1 = 0, 1
    while j > 0:   # krok 7
        quotient = i // j  # krok 3 (celociselne deleni)
        remainder = i - j * quotient  # krok 4
        y = y2 - y1 * quotient    # krok 5
        i, j, y2, y1 = j, remainder, y1, y       # krok 6 (soucasne prirazeni)
    if i != 1:               # krok 8: gcd(z, a) != 1 -> inverze neexistuje
        raise ValueError("Inverze neexistuje: gcd(z, a) != 1")
    return y2 % a    # krok 9: prevod do intervalu (0, a)


def generovani_klicu(e: int = 65537) -> dict:
    # Zadani, kroky 1-5. e se voli pred p, q (FIPS 186-5, A.1.1, bod 1a).
    p, q = generuj_pq(e)     # krok 1 (jedine misto s nahodou)
    n = spocitej_n(p, q)  # krok 2
    phi = eulerova_funkce(p, q)  # krok 3
    if not over_e(e, phi):   # krok 4
        raise RuntimeError("e nesplňuje 1 < e < phi(n) a gcd(e, phi(n)) = 1")
    d = inverze(e, phi)  # krok 5

    return {"p": p, "q": q, "n": n, "phi": phi, "e": e, "d": d, "verejny": (n, e), "soukromy": (n, d)}

# Kontrola klicu zadanych uzivatelem (RFC 8017, 3.1 a 3.2)
# Uplnou platnost (gcd(e, phi) = 1) nelze overit bez znalosti p, q, tj. bez faktorizace n.
# Overuji se proto jen nutne podminky
def over_verejny_klic(n: int, e: int) -> None:
    if n <= 1:
        raise ValueError("Modul n musí být větší než 1")
    if not (3 <= e <= n - 1):
        raise ValueError("Exponent e musí splňovat 3 <= e <= n - 1")
    # phi(n) je pro n = p * q s lichymi p, q sude, sude e tedy nemuze byt nesoudelne
    if e % 2 == 0:
        raise ValueError("Exponent e musí být lichý")


def over_soukromy_klic(n: int, d: int) -> None:
    if n <= 1:
        raise ValueError("Modul n musí být větší než 1")
    if not (1 <= d <= n - 1):
        raise ValueError("Exponent d musí splňovat 1 <= d <= n - 1")

# Prevod textu na cisla a zpet
# z = 8 znaku v bloku (zadani), P = 14 bitu na znak (zvoleno):
# blok ma 8 * 14 = 112 bitu, 2^112 < 10^34 <= n, takze vzdy plati m < n
def text_na_cisla(text: str, z: int = 8, P: int = 14) -> list[int]:
    # kontrola: kod kazdeho znaku se musi vejit do P bitu (emoji apod. ne)
    for znak in text:
        if ord(znak) >= 2**P:
            raise ValueError(f"Znak {znak!r} nelze zakódovat pomocí {P} bitů.")

    # rozdeleni textu na bloky po z znacich (posledni blok muze byt kratsi)
    bloky = []
    for i in range(0, len(text), z):
        bloky.append(text[i:i + z])

    # kazdy znak -> P bitu (doplneni nul smerem k MSB), bity bloku spojit -> jedno cislo (B.2.1)
    cisla = []
    for blok in bloky:
        bity = ""
        for znak in blok:
            bity += format(ord(znak), f"0{P}b")
        cisla.append(int(bity, 2))
    return cisla

def cisla_na_text(cisla: list[int], P: int = 14) -> str:
    text = ""
    for m in cisla:
        # cislo bloku -> binarni retezec (pocatecni nuly se ztratily)
        bity = format(m, "b")
        # doplneni nul zleva na nejblizsi nasobek P; ztrati se nejvyse P - 1 bitu,
        # protoze prvni znak bloku ma kod >= 1 (vyjimka: znak NUL)
        delka = math.ceil(len(bity) / P) * P
        bity = bity.zfill(delka)
        # rozdeleni po P bitech -> kod znaku -> znak
        for i in range(0, len(bity), P):
            kus = bity[i:i + P]
            text += chr(int(kus, 2))
    return text

# Sifrovani a desifrovani po blocich (RFC 8017, 5.1.1 RSAEP a 5.1.2 RSADP)
# pow(x, k, n) = modularni mocneni metodou square-and-multiply
def sifruj(cisla: list[int], n: int, e: int) -> list[int]:
    # c = m^e mod n pro kazdy blok
    sifra = []
    for m in cisla:
        if not (0 <= m < n):
            raise ValueError("Zpráva je mimo rozsah, musí platit 0 <= m < n")
        sifra.append(pow(m, e, n))
    return sifra

def desifruj(cisla: list[int], n: int, d: int) -> list[int]:
    # m = c^d mod n pro kazdy blok
    zprava = []
    for c in cisla:
        if not (0 <= c < n):
            raise ValueError("Zašifrovaný text je mimo rozsah, musí platit 0 <= c < n")
        zprava.append(pow(c, d, n))
    return zprava

