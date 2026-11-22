import hashlib
import os
import numpy as np
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button

# krypto
SALT_LEN = 16   # Bytes (128 b) - sul pro scrypt
KEY_LEN = 32    # Bytes (256 b) - AES-256 a ChaCha20
NONCE_LEN = 12  # Bytes (96 b)  - doporucena delka pro GCM

# kanal
ALPHA = 1.0     # amplituda signalu
SIGMA = 10.0    # smerodatna odchylka sumu kanalu
L = 2500        # pocet vzorku na jeden bit
PAD = 100000    # vzorku sumu pred vysilanim a po nem

# verejna posloupnost pro prenos soli
P0_KEY = hashlib.sha256(b"kanal-public-p0").digest()
CHACHA_NONCE = bytes(16)

# animace
WINDOW = 20000  # vzorku v okne
STEP = 5000     # posun okna za snimek
DEC = 10        # kresli se kazdy 10. vzorek
HEX_ROWS = 10   # radku bajtu ve frontach


def derive_keys(password: str, salt: bytes) -> tuple[bytes, bytes]:
    """Z hesla a soli odvodi dva nezavisle klice (k_enc, k_pn)."""
    # scrypt zdrazuje kazdy pokus o uhodnuti hesla (cas + 32 MiB pameti)
    kdf = Scrypt(salt=salt, length=KEY_LEN, n=2**15, r=8, p=1)
    master = kdf.derive(password.encode("utf-8"))
    # ze stejneho master dva klice bez vzajemneho vztahu (info = ucel)
    k_enc = HKDF(algorithm=hashes.SHA256(), length=KEY_LEN, salt=None, info=b"kanal-enc").derive(master)
    k_pn = HKDF(algorithm=hashes.SHA256(), length=KEY_LEN, salt=None, info=b"kanal-pn").derive(master)
    return k_enc, k_pn


def encrypt(k_enc: bytes, message: bytes) -> tuple[bytes, bytes]:
    """Zasifruje zpravu. Vraci (nonce, ciphertext || tag)."""
    nonce = os.urandom(NONCE_LEN)
    ct = AESGCM(k_enc).encrypt(nonce, message, None)
    return nonce, ct


def decrypt(k_enc: bytes, nonce: bytes, ct: bytes) -> bytes:
    """Overi tag a desifruje. Pri spatnem klici nebo zmene dat vyhodi InvalidTag."""
    return AESGCM(k_enc).decrypt(nonce, ct, None)


def bytes_to_symbols(data: bytes) -> np.ndarray:
    """Bajty -> bity (MSB prvni) -> symboly d = 2b - 1 v {-1, +1}."""
    bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
    # +-1 misto 0/1: prah rozhodnuti je 0 a symboly jsou co nejdal od sebe
    # int8, jinak by 0 - 1 v uint8 preteklo na 255
    return 2 * bits.astype(np.int8) - 1


def symbols_to_bytes(d: np.ndarray) -> bytes:
    """Symboly nebo korelace r_j -> bit podle znamenka -> bajty."""
    d = np.asarray(d)
    if d.size % 8 != 0:
        raise ValueError(f"pocet symbolu ({d.size}) musi byt nasobek 8")
    bits = (d > 0).astype(np.uint8)
    return np.packbits(bits).tobytes()


def pn_sequence(key: bytes, length: int) -> np.ndarray:
    """Z 32B klice vyrobi `length` cipu p[n] v {-1, +1}: ChaCha20 sifruje nuly = keystream."""
    n_bytes = (length + 7) // 8
    encryptor = Cipher(algorithms.ChaCha20(key, CHACHA_NONCE), mode=None).encryptor()
    stream = encryptor.update(bytes(n_bytes))
    return bytes_to_symbols(stream)[:length]


def spread(d: np.ndarray, p: np.ndarray, alpha: float) -> np.ndarray:
    """Symboly d_j -> signal s[n] = alpha * d_{n//L} * p[n]."""
    n = d.size * L
    if p.size < n:
        raise ValueError(f"posloupnost p je kratka: {p.size} < {n}")
    return alpha * np.repeat(d.astype(float), L) * p[:n]


def despread(y: np.ndarray, p: np.ndarray, n_symbols: int) -> np.ndarray:
    """Korelace r_j = suma y[n] * p[n] pres blok j."""
    n = n_symbols * L
    if y.size < n or p.size < n:
        raise ValueError(f"signal nebo p je kratky pro {n_symbols} symbolu")
    return (y[:n] * p[:n]).reshape(n_symbols, L).sum(axis=1)


def vysilac(heslo: str, zprava: str, alpha: float = ALPHA) -> tuple[bytes, np.ndarray]:
    """Zasifruje zpravu a vyrobi signal. Vraci (sul || nonce || ct, s[n])."""
    salt = os.urandom(SALT_LEN)
    k_enc, k_pn = derive_keys(heslo, salt)
    nonce, ct = encrypt(k_enc, zprava.encode("utf-8"))
    body = nonce + ct

    n_salt = SALT_LEN * 8 * L
    n_body = len(body) * 8 * L
    # sul pres verejnou p0, prijemce ji potrebuje driv nez ma klice
    s_salt = spread(bytes_to_symbols(salt), pn_sequence(P0_KEY, n_salt), alpha)
    s_body = spread(bytes_to_symbols(body), pn_sequence(k_pn, n_body), alpha)
    return salt + body, np.concatenate([s_salt, s_body])


def kanal(s: np.ndarray, sigma: float = SIGMA) -> tuple[np.ndarray, np.ndarray, int]:
    """Fyzika kanalu: ticho | vysilani | ticho, vsude sum N(0, sigma^2).
    Vraci (y, s_full, start)."""
    ticho = np.zeros(PAD)
    s_full = np.concatenate([ticho, s, ticho])
    y = s_full + np.random.default_rng().normal(0, sigma, s_full.size)
    return y, s_full, PAD


def prijimac(heslo: str, y: np.ndarray, start: int, n: int) -> dict:
    """Z kanalu vytahne paket a zkusi ho desifrovat. zprava = None, kdyz tag nesedi."""
    y = y[start:start + n]
    n_salt = SALT_LEN * 8 * L
    n_body = n - n_salt

    p0 = pn_sequence(P0_KEY, n_salt)
    r_salt = despread(y[:n_salt], p0, SALT_LEN * 8)
    salt = symbols_to_bytes(r_salt)

    k_enc, k_pn = derive_keys(heslo, salt)

    p_body = pn_sequence(k_pn, n_body)
    r_body = despread(y[n_salt:], p_body, n_body // L)
    body = symbols_to_bytes(r_body)

    nonce, ct = body[:NONCE_LEN], body[NONCE_LEN:]
    try:
        zprava = decrypt(k_enc, nonce, ct).decode("utf-8")
    except InvalidTag:
        zprava = None

    return {
        "paket": salt + body,
        "p": np.concatenate([p0, p_body]),
        "r": np.concatenate([r_salt, r_body]),
        "zprava": zprava,
    }


def bezici_korelace(y: np.ndarray, p: np.ndarray, start: int) -> np.ndarray:
    """Integrator s vybitim: prubezny soucet y*p, v kazdem bloku od nuly. Mimo vysilani NaN."""
    n = p.size
    R = np.full(y.size, np.nan)
    bloky = (y[start:start + n] * p).reshape(-1, L)
    R[start:start + n] = bloky.cumsum(axis=1).ravel()
    return R


def hex_radky(data: bytes) -> list[str]:
    """Bajty -> radky po 8 bajtech v hex."""
    return [" ".join(f"{b:02x}" for b in data[i:i + 8]) for i in range(0, len(data), 8)]


def animace(y, s_full, start, paket, rx_ok, rx_bad):
    """Ctyri panely + fronty bajtu. N = sum ZAP/VYP v panelu 2, mezernik = pauza."""
    n = rx_ok["p"].size
    ref = np.random.default_rng().normal(0, SIGMA, y.size)  # kanal, kde nikdo nevysila
    R_ok = bezici_korelace(y, rx_ok["p"], start)
    R_bad = bezici_korelace(y, rx_bad["p"], start)
    vzorku_na_bajt = 8 * L
    lim_sum = 4 * SIGMA
    lim_sig = 2 * ALPHA
    lim_R = ALPHA * L + 4 * SIGMA * np.sqrt(L)
    stav = {"sum": True, "pauza": False, "k": WINDOW}

    fig = plt.figure(figsize=(15, 9))
    gs = fig.add_gridspec(4, 3, width_ratios=[1, 5, 1.3])
    ax_tx = fig.add_subplot(gs[2:, 0])
    ax_ok = fig.add_subplot(gs[2, 2])
    ax_bad = fig.add_subplot(gs[3, 2])
    axs = [fig.add_subplot(gs[0, 1])]
    axs += [fig.add_subplot(gs[i, 1], sharex=axs[0]) for i in range(1, 4)]
    fig.subplots_adjust(hspace=0.35, left=0.03, right=0.98, top=0.94, bottom=0.08)

    nazvy = ["1  ČISTÝ ŠUM  (nikdo nevysílá)",
             "",  # panel 2 nastavi nadpis_2()
             "3  PŘÍJEMCE  (správné heslo)  běžící korelace",
             "4  ÚTOČNÍK  (špatné heslo)  běžící korelace"]
    meze = [lim_sum, lim_sum, lim_R, lim_R]
    barvy = ["#555555", "#555555", "#1e8449", "#c0392b"]
    cary = []
    for ax, nazev, m, c in zip(axs, nazvy, meze, barvy):
        (cara,) = ax.plot([], [], lw=0.7, color=c)
        cary.append(cara)
        ax.set_title(nazev, loc="left", fontsize=10)
        ax.set_ylim(-m, m)
        ax.axhline(0, color="#bbbbbb", lw=0.5)
        ax.tick_params(labelsize=8)
        if ax is not axs[-1]:
            ax.tick_params(labelbottom=False)
    for ax in axs[2:]:
        ax.axhline(+ALPHA * L, color="#bbbbbb", lw=0.5, ls="--")
        ax.axhline(-ALPHA * L, color="#bbbbbb", lw=0.5, ls="--")
    axs[-1].set_xlabel("vzorek n")

    for ax in (ax_tx, ax_ok, ax_bad):
        ax.axis("off")
    ax_tx.text(0.02, 0.5, "ODCHÁZÍ", va="bottom", fontsize=11, fontweight="bold")
    ax_ok.set_title("PŘICHÁZÍ: příjemce", fontsize=10, fontweight="bold", color="#1e8449")
    ax_bad.set_title("PŘICHÁZÍ: útočník", fontsize=10, fontweight="bold", color="#c0392b")
    txt_tx = ax_tx.text(0.02, 0.48, "", va="top", family="monospace", fontsize=9)
    txt_ok = ax_ok.text(0.02, 0.95, "", va="top", family="monospace", fontsize=9, color="#1e8449")
    txt_bad = ax_bad.text(0.02, 0.95, "", va="top", family="monospace", fontsize=9, color="#c0392b")
    txt_msg = fig.text(0.5, 0.01, "", ha="center", fontsize=12)

    def nadpis_2():
        if stav["sum"]:
            axs[1].set_title("2  KANÁL SE ZPRÁVOU  y[n] = s[n] + šum   [šum ZAP]",
                             loc="left", fontsize=10, color="black")
            axs[1].set_ylim(-lim_sum, lim_sum)
            cary[1].set_color("#555555")
        else:
            axs[1].set_title(f"2  KANÁL SE ZPRÁVOU  s[n]   [šum VYP, měřítko ×{lim_sum / lim_sig:.0f}]",
                             loc="left", fontsize=10, color="#2a6fb0")
            axs[1].set_ylim(-lim_sig, lim_sig)
            cary[1].set_color("#2a6fb0")

    def snimek(k):
        k = min(k, y.size)
        stav["k"] = k
        x = np.arange(k - WINDOW, k, DEC)
        panel_2 = y if stav["sum"] else s_full
        for cara, d in zip(cary, [ref, panel_2, R_ok, R_bad]):
            cara.set_data(x, d[x])
        axs[0].set_xlim(k - WINDOW, k)

        odeslano = int(np.clip(np.ceil((k - start) / vzorku_na_bajt), 0, len(paket)))
        prijato = int(np.clip((k - start) // vzorku_na_bajt, 0, len(paket)))
        txt_tx.set_text("\n".join(hex_radky(paket[odeslano:])[:HEX_ROWS]))
        txt_ok.set_text("\n".join(hex_radky(rx_ok["paket"][:prijato])[-HEX_ROWS // 2:]))
        txt_bad.set_text("\n".join(hex_radky(rx_bad["paket"][:prijato])[-HEX_ROWS // 2:]))

        if k >= start + n:
            bad = rx_bad["zprava"]
            txt_msg.set_text(f"příjemce: ✓ tag ověřen → \"{rx_ok['zprava']}\"      "
                             f"útočník: {'✗ InvalidTag' if bad is None else bad}")
        return cary

    def prepni_sum(event=None):
        stav["sum"] = not stav["sum"]
        tlacitko.label.set_text("Šum: ZAP" if stav["sum"] else "Šum: VYP")
        nadpis_2()
        snimek(stav["k"])  # prekresli i pri pauze
        fig.canvas.draw_idle()

    def klavesa(event):
        if event.key == "n":
            prepni_sum()
        elif event.key == " ":
            stav["pauza"] = not stav["pauza"]
            anim.pause() if stav["pauza"] else anim.resume()

    ax_btn = fig.add_axes([0.03, 0.85, 0.12, 0.05])
    tlacitko = Button(ax_btn, "Šum: ZAP")
    tlacitko.on_clicked(prepni_sum)
    fig.canvas.mpl_connect("key_press_event", klavesa)
    fig.text(0.03, 0.82, "N = šum ZAP/VYP   mezerník = pauza", fontsize=8, color="#777777")

    nadpis_2()
    anim = FuncAnimation(fig, snimek, frames=range(WINDOW, y.size + STEP, STEP),
                         interval=30, repeat=False)
    # anim a tlacitko se musi drzet, jinak je smaze garbage collector
    return fig, anim, tlacitko


def main():
    heslo = input("Heslo: ") or "tajne heslo"
    zprava = input("Zpráva: ") or "Ahoj Bobe, sejdeme se v 18:00."

    paket, s = vysilac(heslo, zprava)
    y, s_full, start = kanal(s)
    rx_ok = prijimac(heslo, y, start, s.size)
    rx_bad = prijimac(heslo + "x", y, start, s.size)  # utocnik: jine heslo

    chyby = int(np.sum(np.sign(rx_ok["r"]) != bytes_to_symbols(paket)))
    print("\nSKRYTÝ KANÁL")
    print(f"α = {ALPHA}   σ = {SIGMA}   L = {L}")
    print(f"SNR na vzorek:    {10 * np.log10(ALPHA**2 / SIGMA**2):+.1f} dB")
    print(f"SNR po korelaci:  {10 * np.log10(L * ALPHA**2 / SIGMA**2):+.1f} dB")
    print(f"zpráva: {len(zprava.encode('utf-8'))} B    paket: {len(paket)} B    vzorků: {s.size}")
    print(f"std kanálu: {y[start:start + s.size].std():.3f}"
          f"   (čistý šum: {SIGMA:.3f}, teorie se signálem: {np.hypot(SIGMA, ALPHA):.3f})")
    print(f"chybných bitů u příjemce: {chyby} / {8 * len(paket)}")
    print(f"příjemce: {rx_ok['zprava']!r}")
    print(f"útočník:  {'✗ InvalidTag' if rx_bad['zprava'] is None else rx_bad['zprava']}")

    fig, anim, tlacitko = animace(y, s_full, start, paket, rx_ok, rx_bad)
    plt.show()


if __name__ == "__main__":
    main()
