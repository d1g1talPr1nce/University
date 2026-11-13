import secrets
import math


# ---------------------------------------------------------------------------
# Generovani prvocisel: FIPS 186-5, priloha B.3.1 (Miller-Rabin) a A.1.3
# ---------------------------------------------------------------------------

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
    a, m = rozklad(w)                    # kroky 1-2 (jednou pro vsechna kola)
    wlen = w.bit_length()                # krok 3: delka w v bitech
    for _ in range(iterace):             # krok 4
        # kroky 4.1-4.2: nahodna baze z wlen bitu (B.2.1), zamitaci vyber 1 < b < w - 1
        while True:
            b = secrets.randbits(wlen)
            if 1 < b < w - 1:
                break
        z = pow(b, m, w)                 # krok 4.3
        if z == 1 or z == w - 1:         # krok 4.4: kolo proslo
            continue
        for _ in range(a - 1):           # krok 4.5: postupne umocnovani na druhou
            z = pow(z, 2, w)
            if z == w - 1:               # krok 4.5.2: kolo proslo
                break
            if z == 1:                   # krok 4.5.3: netrivialni odmocnina z 1 -> slozene
                return False
        else:
            return False                 # krok 4.6: smycka dobehla bez w - 1 -> slozene
    return True                          # krok 5: vsechna kola prosla


def gcd(a: int, b: int) -> int:
    # Eukleiduv algoritmus: gcd(a, b) = gcd(b, a mod b), gcd(a, 0) = a
    while b != 0:
        a, b = b, a % b
    return a


#FIPS 186-5, B.3: limit zkuseho deleni L mezi 10^3 a 10^5
L_DELENI = 1000


def sito(L: int) -> list[int]:
    #Eratosthenovo sito: vsechna prvocisla <= L
    je_prvocislo = [True] * (L + 1)
    je_prvocislo[0] = False
    je_prvocislo[1] = False
    i = 2
    while i * i <= L:
        if je_prvocislo[i]:
            #mensi nasobky i uz byly skrtnuty mensimi prvocisly, proto az od i * i
            for nasobek in range(i * i, L + 1, i):
                je_prvocislo[nasobek] = False
        i += 1
    return [cislo for cislo in range(L + 1) if je_prvocislo[cislo]]


MALA_PRVOCISLA = sito(L_DELENI)


def projde_delenim(p: int, mala_prvocisla: list[int]) -> bool:
    #FIPS 186-5, B.3: volitelne zkuse deleni pred Miller-Rabinem
    #False = jiste slozene, True = muze byt prvocislo (pokracuje Miller-Rabin)
    #predpoklad: p > L (jinak by bylo male prvocislo p zamitnuto, protoze p % p == 0)
    for s in mala_prvocisla:
        if p % s == 0:
            return False
    return True


def kandidat(k: int) -> int:
    #FIPS 186-5, A.1.3, krok 4.2: k nahodnych bitu z kryptografickeho generatoru
    p = secrets.randbits(k)
    #krok 4.2.1: dva nejvyssi bity = 1, pak p >= 1.5 * 2^(k-1) > sqrt(2) * 2^(k-1)
    p = p | (1 << (k - 1))
    p = p | (1 << (k - 2))
    #krok 4.3: vynuceni lichosti
    p = p | 1
    return p


def splnuje_dolni_mez(p: int, k: int) -> bool:
    #FIPS 186-5, A.1.3, krok 4.4: p >= sqrt(2) * 2^(k-1)
    #sqrt(2) je iracionalni a float ma jen 53 bitu mantisy, proto obe strany na druhou:
    #p >= sqrt(2) * 2^(k-1)  <=>  p^2 >= 2^(2k-1)
    return p * p >= 2 ** (2 * k - 1)


def pocet_kol_mr(k: int) -> int:
    #FIPS 186-5, tabulka B.1 (sloupec podle bezpecnostni sily):
    #p, q 1024 bitu -> 5 kol (chyba 2^-112), 1536 -> 4 (2^-128), 2048 -> 4 (2^-144)
    #mezi radky tabulky se bere mensi velikost (vic kol = konzervativni)
    #pod 1024 bitu tabulka neplati -> odhad pro nejhorsi pripad 4^-50 = 2^-100
    if k >= 1536:
        return 4
    if k >= 1024:
        return 5
    return 50


def generuj_pq(nlen: int, e: int, prisne: bool = True) -> tuple[int, int]:
    #FIPS 186-5, A.1.3: generovani nahodnych pravdepodobnych prvocisel p, q
    #prisne=False povoli nlen < 2048 pro experimenty (pak to NENI podle standardu)
    if prisne and nlen < 2048:                          #krok 1
        raise ValueError("FIPS 186-5 vyžaduje nlen >= 2048 (A.1.3, krok 1)")
    if nlen < 128 or nlen % 2 != 0:
        raise ValueError("nlen musí být sudé a alespoň 128")
    if e <= 2**16 or e >= 2**256 or e % 2 == 0:        #krok 2
        raise ValueError("Veřejný exponent e nesplňuje podmínky FIPS 186-5 (A.1.3, krok 2)")

    k = nlen // 2
    kola = pocet_kol_mr(k)

    #Generovani p (kroky 4.1-4.7)
    i = 0                                               #krok 4.1
    while True:
        p = kandidat(k)                                 #kroky 4.2-4.3
        if not splnuje_dolni_mez(p, k):                 #krok 4.4: go to 4.2 (bez zvyseni i)
            continue
        if gcd(p - 1, e) == 1 and projde_delenim(p, MALA_PRVOCISLA) and miller_rabin(p, kola):  #krok 4.5
            break
        i += 1                                          #krok 4.6
        if i >= 5 * nlen:                               #krok 4.7
            raise RuntimeError(f"Nepodařilo se najít prvočíslo p během {5 * nlen} pokusů (A.1.3, krok 4.7)")

    #krok 5.5: hranice 2^(nlen/2 - 100); pro k <= 100 by exponent byl zaporny (float),
    #celociselne to pak znamena |p - q| <= 0, tj. p == q
    if k > 100:
        hranice = 2 ** (k - 100)
    else:
        hranice = 0

    #Generovani q (kroky 5.1-5.8)
    i = 0                                               #krok 5.1
    while True:
        q = kandidat(k)                                 #kroky 5.2-5.3
        if not splnuje_dolni_mez(q, k):                 #krok 5.4
            continue
        if abs(p - q) <= hranice:                       #krok 5.5
            continue
        if gcd(q - 1, e) == 1 and projde_delenim(q, MALA_PRVOCISLA) and miller_rabin(q, kola):  #krok 5.6
            break
        i += 1                                          #krok 5.7
        if i >= 10 * nlen:                              #krok 5.8
            raise RuntimeError(f"Nepodařilo se najít prvočíslo q během {10 * nlen} pokusů (A.1.3, krok 5.8)")

    return (p, q)


# ---------------------------------------------------------------------------
# Vypocet klicu: zadani kroky 2-5
# ---------------------------------------------------------------------------

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
    i, j = a, z                                  # krok 2
    y2, y1 = 0, 1
    while j > 0:                                 # krok 7
        quotient = i // j                        # krok 3 (celociselne deleni)
        remainder = i - j * quotient             # krok 4
        y = y2 - y1 * quotient                   # krok 5
        i, j, y2, y1 = j, remainder, y1, y       # krok 6 (soucasne prirazeni)
    if i != 1:                                   # krok 8: gcd(z, a) != 1 -> inverze neexistuje
        raise ValueError("Inverze neexistuje: gcd(z, a) != 1")
    return y2 % a                                # krok 9: prevod do intervalu (0, a)


def nsn(a: int, b: int) -> int:
    #nejmensi spolecny nasobek: lcm(a, b) = a * b / gcd(a, b), celociselne
    return a // gcd(a, b) * b


def generovani_klicu(nlen: int = 2048, e: int = 65537, prisne: bool = True) -> dict:
    #FIPS 186-5, A.1.1 a A.1.3; e se voli pred p, q (A.1.1, bod 1a)
    while True:
        p, q = generuj_pq(nlen, e, prisne)
        n = spocitej_n(p, q)
        phi = eulerova_funkce(p, q)
        #A.1.1, bod 3: d = e^(-1) mod lcm(p - 1, q - 1) (Carmichaelova funkce lambda(n))
        lam = nsn(p - 1, q - 1)
        if not over_e(e, lam):
            raise RuntimeError("e nesplňuje 1 < e < λ(n) a gcd(e, λ(n)) = 1")
        d = inverze(e, lam)
        #A.1.1, bod 3a: musi platit d > 2^(nlen/2), jinak nove p, q (extremne vzacne)
        if d > 2 ** (nlen // 2):
            break
    return {"p": p, "q": q, "n": n, "phi": phi, "lambda": lam, "e": e, "d": d, "nlen": nlen, "verejny": (n, e), "soukromy": (n, d)}


# ---------------------------------------------------------------------------
# Kontrola klicu zadanych uzivatelem (RFC 8017, 3.1 a 3.2)
# Uplnou platnost (gcd(e, phi) = 1) nelze overit bez znalosti p, q, tj. bez faktorizace n.
# Overuji se proto jen nutne podminky.
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Prevod textu na cisla a zpet
# z = 8 znaku v bloku (zadani), P = 14 bitu na znak (zvoleno):
# blok ma 8 * 14 = 112 bitu, 2^112 < 10^34 <= n, takze vzdy plati m < n.
# P = 15 by dalo 120 bitu a 2^120 > n_max, P = 14 je tedy maximum.
# ---------------------------------------------------------------------------

#Unicode ma kodove body az do U+10FFFF, to je 21 bitu (vejdou se i emoji)
P_UNICODE = 21


def parametry_bloku(n: int) -> tuple[int, int]:
    #n >= 2^(nlen-1), blok s nejvyse nlen-1 bity je tedy vzdy mensi nez n
    #vraci (z, P): pocet znaku v bloku a bitu na znak
    z = (n.bit_length() - 1) // P_UNICODE
    if z < 1:
        raise ValueError("Modul n je příliš malý pro blok alespoň jednoho znaku")
    return (z, P_UNICODE)


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


# ---------------------------------------------------------------------------
# Sifrovani a desifrovani po blocich (RFC 8017, 5.1.1 RSAEP a 5.1.2 RSADP)
# pow(x, k, n) = modularni mocneni metodou square-and-multiply
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Testy (spusti se jen pri primem spusteni souboru: python rsa.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import time

    #rozklad, Miller-Rabin, gcd, inverze
    assert rozklad(561) == (4, 35)
    for c in (15, 21, 561, 1105, 1729, 2047, 3215031751):
        assert miller_rabin(c, 50) is False
    for p in (5, 7, 13, 17, 41, 263, 271, 1_000_000_007):
        assert miller_rabin(p, 50) is True
    assert gcd(12, 18) == 6
    assert inverze(17, 3120) == 2753
    assert nsn(4, 6) == 12

    #sito a zkuse deleni
    assert sito(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert len(MALA_PRVOCISLA) == 168
    assert projde_delenim(1_000_000_007, MALA_PRVOCISLA) is True
    assert projde_delenim(1009 * 1013, MALA_PRVOCISLA) is True
    assert projde_delenim(997 * 1_000_000_007, MALA_PRVOCISLA) is False

    #kandidat a dolni mez
    for k in (64, 512, 1024):
        for _ in range(1000):
            p = kandidat(k)
            assert p.bit_length() == k
            assert p % 2 == 1
            assert p >> (k - 2) == 0b11
            assert splnuje_dolni_mez(p, k)
    assert splnuje_dolni_mez(3 * 2**62, 64)
    assert not splnuje_dolni_mez(2**63, 64)

    #prisny rezim odmitne nlen < 2048
    try:
        generuj_pq(1024, 65537)
        print("NEVYHODILO pro nlen = 1024")
    except ValueError:
        pass

    #klice ruznych velikosti + cely RSA cyklus vcetne emoji
    for nlen, prisne in ((256, False), (512, False), (1024, False), (2048, True)):
        start = time.perf_counter()
        k = generovani_klicu(nlen, 65537, prisne)
        trvani = (time.perf_counter() - start) * 1000
        n, e, d = k["n"], k["e"], k["d"]
        assert n.bit_length() == nlen
        assert (e * d) % k["lambda"] == 1
        assert d > 2 ** (nlen // 2)
        assert abs(k["p"] - k["q"]) > (2 ** (nlen // 2 - 100) if nlen // 2 > 100 else 0)
        z, P = parametry_bloku(n)
        for t in ("Ahoj svete!", "Příliš žluťoučký kůň €", "emoji 😀🔐", ""):
            c = sifruj(text_na_cisla(t, z, P), n, e)
            assert cisla_na_text(desifruj(c, n, d), P) == t
        print(f"nlen = {nlen:5}: klic za {trvani:8.1f} ms, blok = {z} znaku x {P} bitu")

    print("Všechny testy prošly.")
