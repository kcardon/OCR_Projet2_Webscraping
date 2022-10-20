"""Projet 2 Openclassrooms : 
version bêta d'une application dédiée au web-scraping d'un site web de vente de livres en ligne, books.toscrape.com.
"""

# Import des packages
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re

# Préparation du dossier de récupération des données
os.mkdir("Data")
os.chdir(os.getcwd() + "\Data")
data_dir = os.getcwd()

### EXTRACT

# Définition d'une fonction permettant de traduire une url en contenu html.
def get_html_content(url):
    page = requests.get(url)
    if page.ok:
        return BeautifulSoup(page.content, "html.parser")


# Lien de départ : identification des liens vers les différentes catégories du site
url_start = "http://books.toscrape.com/"
html = get_html_content(url_start)

# Récupération des liens URL des catégories à parcourir
html_cat = html.find("div", class_="side_categories")
cat_links = [url_start + link.get("href") for link in html_cat.find_all("a")][1:]

# Itération sur chaque catégorie
for link in cat_links:
    current_cat = link.split("/")[-2]

    # Création du dossier spécifique à la catégorie et d'un dossier Images
    os.chdir(data_dir)
    os.mkdir(current_cat)
    os.chdir(data_dir + "\\" + current_cat)
    os.mkdir("Images")
    os.chdir(data_dir + "\\" + current_cat + "\Images")
    html_catpage = get_html_content(link)

    # check_pages : permet de contrôler s'il existe d'autres pages dans cette catégorie
    links = [link]
    check_pages = html_catpage.find("li", class_="current")

    # Si une page suivante est identifiée, on repère le nombre total de pages à incrémenter dans la variables links
    if check_pages is not None:
        nbPages = int(check_pages.string.split()[-1])
        for page in range(2, nbPages + 1):
            links.append(
                link[0 : -link[::-1].index("/")] + "page-" + str(page) + ".html"
            )

    # La variable books nous permettra de recueillir les liens vers chacun des livres de la catégorie.
    books = []
    for link in links:
        html = get_html_content(link)

        for book in html.find_all(
            "a"
        ):  # Loop pour chaque lien identifié : on l'enregistre dans la liste books content les liens individuels de chaque livre
            if ("thumbnail" in str(book)) and (
                url_start + "catalogue/" + book.get("href") not in books
            ):
                books.append(
                    url_start + "catalogue/" + book.get("href").replace("../", "")
                )

    ### TRANSFORM
    # Création d'un Data Frame
    DF = pd.DataFrame(
        columns=[
            "product_page_url",
            "universal_ product_code (upc)",
            "title",
            "price_including_tax",
            "price_excluding_tax",
            "number_available",
            "product_description",
            "category",
            "review_rating",
            "image_url",
        ]
    )

    # Chaque page "livre" va être examinée afin d'en tirer les informations demandées.
    for book_link in books:
        book_html = get_html_content(book_link)
        book_data = [  # récupération des données du livre
            # Page URL
            book_link,
            # UPC
            book_html.find("td").text,
            # Titre
            book_html.find("h1").text,
            # Prix TTC
            float(book_html.find_all("td")[2].text[1:]),
            # PRIX HT
            float(book_html.find_all("td")[3].text[1:]),
            # Stock (extraction des digits avec "re.findall")
            re.findall("\d+", book_html.find_all("td")[5].text)[0],
            # Description
            book_html.find_all("p")[3].text,
            # Categorie
            book_html.find_all("a")[3].text,
            # Score
            ["Zero", "One", "Two", "Three", "Four", "Five"].index(
                str(book_html.find_all("p")[2].attrs["class"][1])
            ),
            # Lien de l'image
            url_start + book_html.find("img").attrs["src"],
        ]

        ###LOAD
        # La ligne spécifique au livre est ajoutée au data frame
        DF.loc[len(DF)] = book_data

        # Téléchargement de l'image
        img_data = requests.get(book_data[-1]).content
        with open(
            ("Cover page - " + book_data[7] + "." + book_data[1] + ".jpg"), "wb"
        ) as handler:
            handler.write(img_data)

    # Enregistrement des données dans le data frame
    os.chdir(data_dir + "\\" + current_cat)
    DF.to_csv("ScrapedBooks - Category " + current_cat + ".csv", sep=";")
