import secrets

def rozklad(w : int) -> tuple[int, int]:
    #predpocitani parametru a, m pro miller-rabina (FIPS 186-5 B.3.1 kroky 1-2)
    if(w % 2 == 0 or  w < 5):
        raise ValueError("Kandidát (w) není lichý nebo neplatí relace w >= 5 ")

    m = w-1
    #delim m dvema, dokud neni liche; a pocita, kolikrat jsem delil
    a : int = 0
    while(m % 2 == 0):
        a +=1
        m  = m // 2

    return (a,m)

#otestovani toho, zda cislo je slozene nebo prvocislo, pomoc miller rabina... (podle standardu B.3.1)
def miller_rabin(w : int, iterace : int)-> bool:
    #najiti koeficientu a, m  (hlavne a)
    (a,m) = rozklad(w)
    #velikost w v bitech,
    wlen = w.bit_length()
    for _ in range(1, iterace+1):
        # dostaneme retezec b o wlen bitech z nahodneho z DRBG, nasledne prevedeny na integere podle B.2.1
        while(True):
            b = secrets.randbits(wlen)
            #zamitaci vyber, pokud podminka neni splena, vytvarim b znovu
            if((b<=1) or (b>=w-1)):
                continue
            else:
                #nasli jsme spravne b
                break

        z = pow(b,m,w)
        if((z == 1) or (z == w -1)):
            continue
        for _ in range(a-1):
            z = pow(z,2,w)
            if(z == w-1):
                break
            elif(z == 1):
                return False
        else:
            return False

    return True

def gcd(a: int, b: int) -> int:
    # plati veta gcd(a, b) = gcd(b, a mod b), pro vsechna a gcd(a, 0) = a
    while b != 0:
        a, b = b, a % b
    return a

def generuj_pq(e: int) -> tuple[int, int]:
    # FIPS 186-5, A.1.3 (rozsah 18 cifer dle zadani; kroky 1 a 4.4/5.4 vynechany)
    if e <= 2**16 or e >= 2**256 or e % 2 == 0:        # krok 2
        raise ValueError("Veřejný exponent e nesplňuje podmínky FIPS 186-5 (A.1.3, krok 2)")
    rng = secrets.SystemRandom()

    # Generovani p (kroky 4.1-4.7)
    i = 0
    while True:
        p = rng.randrange(10**17, 10**18)
        if p % 2 == 0:
            p += 1
        if gcd(p - 1, e) == 1 and miller_rabin(p, 50):
            break
        i += 1
        if i >= 600:
            raise RuntimeError("Nepodařilo se najít prvočíslo p během 600 pokusů (A.1.3, krok 4.7)")

    # Generovani q (kroky 5.1-5.8)
    i = 0
    while True:
        q = rng.randrange(10**17, 10**18)
        if q % 2 == 0:
            q += 1
        # Krok 5.5: |p - q| <= 2^(nlen/2 - 100). Pro nlen ~ 120 je prava strana
        # 2^-40 < 1; pro cela cisla to plati prave kdyz p == q.
        if p == q:
            continue
        if gcd(q - 1, e) == 1 and miller_rabin(q, 50):
            break
        i += 1
        if i >= 1200:
            raise RuntimeError("Nepodařilo se najít prvočíslo q během 1200 pokusů (A.1.3, krok 5.8)")

    return (p, q)

def spocitej_n(p: int, q: int) -> int:
    return p * q

def eulerova_funkce(p: int, q: int) -> int:
    # phi(n) = (p - 1)(q - 1) pro n = p*q, p != q prvocisla
    return (p - 1) * (q - 1)

def over_e(e: int, phi: int) -> bool:
    # Zadani, krok 4: 1 < e < phi a gcd(e, phi) = 1.
    # Zaruceno konstrukci: gcd(p-1, e) = gcd(q-1, e) = 1  =>  gcd(e, (p-1)(q-1)) = 1.
    # Kontrola hlida, ze tento predpoklad plati.
    return 1 < e < phi and gcd(e, phi) == 1


def inverze(z: int, a: int) -> int:
    # FIPS 186-5, B.1: z^-1 mod a
    # EGCD
    if not(0<z<a):
        raise ValueError("Musí platit 0 < z < a")
    i, j = a, z
    y2, y1 = 0,1
    while j > 0:
        quotient = i // j
        remainder = i -j * quotient
        y = y2 - y1  * quotient
        i, j, y2, y1 = j, remainder, y1, y
    if i != 1:
        raise ValueError("Inverzne neexisutje: gcd(z, a) != 1")
    return y2 % a

def generovani_klicu(e : int = 65537) ->dict:
    p,q = generuj_pq(e)
    n = spocitej_n(p,q)
    phi = eulerova_funkce(p,q)
    if not over_e(e, phi):
        raise RuntimeError("e nesplňuje 1 < e < φ(n) a gcd(e, φ(n)) = 1")
    d = inverze(e, phi)
    return {"p" : p, "q" : q, "n" : n, "phi" : phi, "e" : e, "d" : d, "verejny" : (n,e), "soukromy" : (n,d)}



