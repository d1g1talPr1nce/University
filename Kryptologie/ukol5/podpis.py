from rsa import sifruj, desifruj
import hashlib


def hashProudu(f) -> bytes:
    """SHA3-512 z libovolneho otevreneho binarniho proudu (soubor na disku, soubor v zipu, ...).
    Staci, aby objekt mel metodu .read(n) vracejici bytes."""
    keccak = hashlib.sha3_512()
    blok = f.read(65536)
    while blok != b"":
        keccak.update(blok)
        blok = f.read(65536)
    return keccak.digest()


def hashSouboru(cesta: str) -> bytes:
    """SHA3-512 souboru na disku."""
    with open(cesta, "rb") as f:
        return hashProudu(f)


def rozdeleniHasheBloky(h: bytes, velikostBloku: int = 14) -> list[int]:
    """Rozdeleni hash na bloky po velikostBloku bajtech,
    kazdy blok prevede na cislo"""
    bloky: list[int] = []
    for i in range(0, len(h), velikostBloku):  # skonci sam na konci
        kus = h[i:i + velikostBloku]  # posledni kus ma 8 B
        bloky.append(int.from_bytes(kus, "big"))  # big endian
    return bloky


def blokyNaHash(bloky: list[int], velikostBloku: int = 14, delkaHashe: int = 64) -> bytes:
    """Vraceni hashe z ciselnych hodnot zpatky na bytes"""
    bytesHash: bytes = b""
    for k, blok in enumerate(bloky):
        # bloky 0 az 3 maji velikostBloku,
        # posledni má ale ( 64-4*14 = 8)
        delka = min(velikostBloku, delkaHashe - velikostBloku*k)
        bytesHash += blok.to_bytes(delka, "big")
    return bytesHash


def podepsaniHashe(h: bytes, n: int, d: int) -> list[int]:
    """Jadro podpisu: s_k = m_k^d mod n pro kazdy blok hashe (soukromy klic)."""
    return desifruj(rozdeleniHasheBloky(h), n, d)


def podepsani(cesta: str, n: int, d: int) -> list[int]:
    """Podpis souboru na disku."""
    return podepsaniHashe(hashSouboru(cesta), n, d)


def overeniHashe(h: bytes, podpis: list[int], n: int, e: int) -> bool:
    """Jadro overeni: s_k^e mod n -> slozit hash -> porovnat s h (verejny klic)
    Nezavisi na tom, odkud hash pochazi (soubor na disku, soubor v zipu)."""
    # 64 B hash po 14 B -> 5 bloku; jiny pocet = poskozeny nebo cizi podpis
    if len(podpis) != len(rozdeleniHasheBloky(bytes(64))):
        return False

    # podpis je vzdy < n; jinak nemohl vzniknout s timto klicem
    if any(not (0 <= s < n) for s in podpis):
        return False

    bloky = sifruj(podpis, n, e)   # RSAVP1: s^e mod n

    try:
        slozenyHash = blokyNaHash(bloky)
    except OverflowError:
        # obnoveny blok se nevejde do sve delky -> nevznikl z praveho hashe
        return False

    return slozenyHash == h


def overeniPodpisu(cesta: str, podpis: list[int], n: int, e: int) -> bool:
    """Overeni podpisu souboru na disku."""
    return overeniHashe(hashSouboru(cesta), podpis, n, e)
