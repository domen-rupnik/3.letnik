import requests
from bs4 import BeautifulSoup
import sys


def scraper(URL):
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }

    page = requests.get(URL, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    rezultat = {"Ime": None, "Trgovina": None, "Trenutna cena": None, "Prejsnja cena": None, "Popust": None,
                "Slika": None, "URL": None, }

    if URL.split('.')[1] == 'mimovrste':

        rezultat["Ime"] = soup.find_all('h1', class_='lay-overflow-hidden word-break--word mt-5')[0].text.strip()

        rezultat["Trenutna cena"] = float(
            soup.find_all('b', class_='pro-price variant-BC con-emphasize font-primary--bold mr-5')[
                0].text.strip().replace('.', '').replace(',', '.').split(' ')[0])

        prejsna_cena = soup.find_all('del', class_='rrp-price')

        if len(prejsna_cena) != 0:
            rezultat["Prejsnja cena"] = float(
                prejsna_cena[0].text.strip().replace('.', '').replace(',', '.').split(' ')[0])

        popust = soup.find_all('div', class_='label--round-sale round-label-alignment')

        if len(popust) != 0:
            rezultat["Popust"] = popust[0].text.strip().replace('-', '').replace('%', '')
        else:
            rezultat["Popust"] = 100 - rezultat["Trenutna cena"] * 100 / rezultat["Prejsnja cena"] if rezultat[
                                                                                                          "Prejsnja cena"] is not None else None

        rezultat["Slika"] = soup.find_all('img', class_='gallery-magnifier__normal')[0].get('src')
        rezultat["URL"] = URL
        rezultat["Trgovina"] = "Mimovrste"

    elif URL.split('.')[1] == 'bigbang':

        rezultat["Ime"] = soup.find_all('h1', class_='cd-title')[0].text.strip()

        # trenutna_cena = soup.find_all('div', class_='cd-current-price red')[0].text.strip().replace(',', '.').split(' ')[0]
        rezultat["Trenutna cena"] = float(
            soup.find_all('div', class_='cd-current-price')[0].text.strip().replace('.', '').replace(',', '.').split(
                ' ')[0])

        prejsna_cena = soup.find_all('div', class_='cd-old-price')
        if len(prejsna_cena) != 0:
            rezultat["Prejsnja cena"] = float(
                prejsna_cena[0].text.strip().replace('.', '').replace(',', '.').split(' ')[0])
        else:
            rezultat["Prejsnja cena"] = None

        popust = soup.find_all('div', class_='label--round-sale round-label-alignment')

        if len(popust) != 0:
            rezultat["Popust"] = popust[0].text.strip().replace('-', '').replace('%', '')
        else:
            rezultat["Popust"] = 100 - rezultat["Trenutna cena"] * 100 / rezultat["Prejsnja cena"] if rezultat[
                                                                                                          "Prejsnja cena"] is not None else None

        rezultat["Slika"] = soup.find_all('div', class_='cd-hero-image')[0].img.get('src')

        rezultat["URL"] = URL

        rezultat["Trgovina"] = "Big Bang"

    elif URL.split('.')[0].split('/')[-1] == 'edigital':
        rezultat["Ime"] = soup.find_all('h1', class_='main-title')[0].text.strip()

        rezultat["Trenutna cena"] = float(str(soup.find(itemprop='price')).split('"')[1])

        rezultat["Prejsnja cena"] = float(
            str(soup.find_all('strong', class_='price--old')[0]).split('content')[1].split('"')[1]) if len(
            soup.find_all('strong', class_='price--old')) != 0 else None

        rezultat["Popust"] = float(str(soup.find('span', class_='discount--old')).split('content')[1].split('"')[1]) if \
        rezultat["Prejsnja cena"] is not None else None

        rezultat["Slika"] = soup.find_all('a', class_='main-image-link')[0].img.get('src')

        rezultat["URL"] = URL

        rezultat["Trgovina"] = "Extreme Digital"

    else:
        rezultat = "Spletna stran ni podprta!"

    return rezultat


def primerjajIzdelka(prvi, drugi):
    prvi = prvi.upper().replace(',', '').split(" ")
    drugi = drugi.upper().replace(',', '').split(" ")

    ujemanje = list(set(prvi) - (set(prvi) - set(drugi)))
    neujemanje = list(set(prvi) ^ set(drugi))

    if len(ujemanje) >= min(len(prvi), len(drugi)) * 0.5:
        return True
    else:
        return False
