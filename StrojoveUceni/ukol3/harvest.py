import requests
import time
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# naharvestovani textu 
def harvester(jazyk: str, n: int):
    #vybrane jazyky
    jazyky = {
        "cs": "Čeština",
        "sk": "Slovenština",
        "en": "Angličtina",
        "uk": "Ukrajinština",
        "ru": "Ruština"
    }

    # Kontrola vstupu
    if jazyk not in jazyky.values():
        raise ValueError("Neplatný jazyk!")

    if type(n) is not int or n <= 0:
        raise ValueError("Počet článků musí být kladné celé číslo!")

    # Sestaveni url pro WIKIAPI
    url = None
    zkratka = None
    #nastaveni spravne URL
    for kod, nazev in jazyky.items():
        if nazev == jazyk:
            zkratka = kod
            url = f"https://{kod}.wikipedia.org/w/api.php"
            break
    #pokud URL neni, vyhlasit chybu
    if url is None:
        raise ValueError("Nebyla zadána platná URL!")

    # parametry pro harvest
    batch_size = 10
    min_length = 300
    max_requests = max(20, n)

    pocet = 0
    pocet_znaku = 0
    pocet_ziskanych = 0

    seen = set()
    #nastvaeni request
    params = {
        "action": "query",
        "format": "json",
        "generator": "random",
        "prop": "extracts",
        "grnnamespace": 0,
        "grnlimit": batch_size,
        "explaintext": 1,
        "exintro": 1,
        "exlimit": batch_size,
        "maxlag": 5
    }

    headers = {
        "User-Agent": "yujky1@seznam.cz"
    }

    cesta = Path(f"corpus/{zkratka}.txt")

    #HTTP session s automatickym opakovanim
    retry = Retry(total=3,backoff_factor=2,status_forcelist=[429, 500, 502, 503, 504],allowed_methods=["GET"],respect_retry_after_header=True)
    with requests.Session() as session:
        session.headers.update(headers)
        session.mount("https://",HTTPAdapter(max_retries=retry))

        # otevereni souboru 
        with open(cesta, mode="w", encoding="utf-8") as soubor:

            # Zacet harvestovani
            for pokus in range(max_requests):

                if pocet >= n:
                    break

                params["grnlimit"] = min(batch_size, n - pocet)

                try:
                    response = session.get(url=url,params=params,timeout=20)
                    response.raise_for_status()
                    data = response.json()
                except requests.RequestException as error:
                    print(f"HTTP chyba: {error}")
                    break

                # Ocekavani chyb
                if "error" in data:
                    chyba = data["error"]

                    if chyba.get("code") == "maxlag":
                        time.sleep(5)
                        continue
                    raise RuntimeError(f"Chyba Wikipedia API: {chyba}")

                pages = data.get("query", {}).get("pages", {})

                # Zpracovani clanku
                for page_id, page in pages.items():
                    pocet_ziskanych += 1

                    # Kontrola duplicity
                    if page_id in seen:
                        continue

                    seen.add(page_id)
                    nazev = page.get("title", "")
                    text = page.get("extract", "").strip()

                    # Kontrola minimalni delky
                    if len(text) < min_length:
                        continue

                    # Ulozeni textu
                    soubor.write(text)
                    soubor.write("\n\n")

                    pocet += 1
                    pocet_znaku += len(text)

                    if pocet >= n:
                        break

                print(f"[{jazyk}] "f"Uloženo: {pocet}/{n} | "f"Znaků: {pocet_znaku}")

                # Prodleva mezi pozadvky
                if pocet < n:
                    time.sleep(1)
                    
    print(f"Požadováno článků: {n}")
    print(f"Zpracováno článků: {pocet_ziskanych}")
    print(f"Úspěšně uloženo: {pocet}")
    print(f"Celkový počet znaků: {pocet_znaku}")
    print(f"Soubor: {cesta}")
    if pocet < n:
        print("Upozornění: Nepodařilo se dosáhnout požadovaného počtu článků.")
    return pocet


if __name__ == "__main__":

    for jazyk in [
        "Čeština",
        "Slovenština",
        "Angličtina",
        "Ruština",
        "Ukrajinština"
    ]:
        harvester(jazyk, 300)