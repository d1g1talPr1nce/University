import requests
import csv
import time
import unicodedata
import csv
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

#nastaveni jazyku
JAZYKY = {
    "cs": "Čeština",
    "sk": "Slovenština",
    "en": "Angličtina",
    "ru": "Ruština",
    "uk": "Ukrajinština"
}
#nastaveni parametru pro request
POCET_NA_JAZYK = 20
MIN_ZNAKU = 120
MAX_ZNAKU = 300
BATCH_SIZE = 10
MAX_POKUSU = 100
USER_AGENT = "yujky1@seznam.cz"
BASE = Path(__file__).resolve().parent
CORPUS_DIR = BASE / "corpus"
TEST_DIR = BASE / "test_data"

#normalizace textu
def normalizuj(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.casefold()

    znaky = [znak if znak.isalpha() else " "for znak in text]

    return " ".join("".join(znaky).split())


def priprav_text(text: str) -> str:

    # Odstranenich prebytecnych bilych znaku
    text = " ".join(text.split())

    # Omezeni velikosti slov a neodtrani poslednih oznaku
    if len(text) > MAX_ZNAKU:
        text = text[:MAX_ZNAKU].rsplit(" ", 1)[0]

    return text


def vytvor_session() -> requests.Session:
    session = requests.Session()

    session.headers.update({"User-Agent": USER_AGENT})

    retry = Retry(total=3,backoff_factor=2,status_forcelist=[429, 500, 502, 503, 504],allowed_methods=["GET"],respect_retry_after_header=True)

    session.mount("https://",HTTPAdapter(max_retries=retry))

    return session


def harvest_test(jazyk: str, session: requests.Session) -> list:

    if jazyk not in JAZYKY:
        raise ValueError("Nepodporovaný jazyk!")

    nazev = JAZYKY[jazyk]
    url = f"https://{jazyk}.wikipedia.org/w/api.php"

    # Načtení trénovacího korpusu kvůli kontrole překryvu
    with open(CORPUS_DIR / f"{jazyk}.txt",encoding="utf-8") as soubor:
        trenovaci_text = normalizuj(soubor.read())

    vysledky = []
    pouzita_id = set()
    pouzite_texty = set()
    params = {
        "action": "query",
        "format": "json",
        "generator": "random",
        "grnnamespace": 0,
        "grnlimit": BATCH_SIZE,
        "prop": "extracts",
        "explaintext": 1,
        "exintro": 1,
        "exchars": 550,
        "exlimit": BATCH_SIZE,
        "maxlag": 5
    }

    for pokus in range(MAX_POKUSU):
        if len(vysledky) >= POCET_NA_JAZYK:
            break
        try:
            response = session.get(url,params=params,timeout=(5, 20))

            response.raise_for_status()
            data = response.json()

        except (requests.RequestException, ValueError) as error:
            print(f"Chyba požadavku: {error}")
            time.sleep(3)
            continue

        if "error" in data:
            kod_chyby = data["error"].get("code")

            if kod_chyby in ("maxlag", "ratelimited"):
                time.sleep(5)
                continue

            raise RuntimeError(data["error"])

        pages = data.get("query", {}).get("pages", {})

        for page in pages.values():

            page_id = page.get("pageid")

            if page_id is None or page_id in pouzita_id:
                continue

            pouzita_id.add(page_id)

            text = priprav_text(page.get("extract", ""))
            normalizovany = normalizuj(text)

            # Kontrola minimální délky
            if len(normalizovany) < MIN_ZNAKU:
                continue

            # Kontrola doslovného překryvu s trénovacím korpusem
            if normalizovany in trenovaci_text:
                continue

            # Kontrola duplicit v testovací sadě
            if normalizovany in pouzite_texty:
                continue

            pouzite_texty.add(normalizovany)

            vysledky.append({"jazyk": nazev,"text": text,"page_id": page_id,"nazev_clanku": page.get("title", ""),"zdroj": f"https://{jazyk}.wikipedia.org/?curid={page_id}"})

            if len(vysledky) >= POCET_NA_JAZYK:
                break

        print(f"{nazev}: "f"{len(vysledky)}/{POCET_NA_JAZYK} textů")

        if len(vysledky) < POCET_NA_JAZYK:
            time.sleep(1)

    if len(vysledky) != POCET_NA_JAZYK:
        raise RuntimeError(f"{nazev}: podařilo se získat pouze "f"{len(vysledky)} testovacích textů.")

    return vysledky


def main():

    TEST_DIR.mkdir(parents=True, exist_ok=True)

    vsechny_texty = []

    with vytvor_session() as session:

        for jazyk in JAZYKY:
            vysledky = harvest_test(jazyk, session)
            vsechny_texty.extend(vysledky)

    cesta = TEST_DIR / "testy.tsv"

    with open(cesta,mode="w",encoding="utf-8",newline="") as soubor:

        writer = csv.DictWriter(soubor,fieldnames=[
                "jazyk",
                "text",
                "page_id",
                "nazev_clanku",
                "zdroj"
            ],
            delimiter="\t"
        )

        writer.writeheader()
        writer.writerows(vsechny_texty)

    print(f"Celkový počet textů: {len(vsechny_texty)}")
    print(f"Soubor: {cesta}")


if __name__ == "__main__":
    main()