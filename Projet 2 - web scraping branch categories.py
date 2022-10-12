# Import des packages
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re

# Lien de départ : identification des liens vers les différentes catégories du site
urlStart = "http://books.toscrape.com/"
page = requests.get(urlStart)
if page.ok:
    html = BeautifulSoup(page.content, "html.parser")
    # Récupération des liens URL des catégories à parcourir
    htmlCat = html.find("div", class_="side_categories")
    catLinks = [urlStart + link.get("href") for link in htmlCat.find_all("a")][1:]

    # Itération sur chaque catégorie
    for catLink in catLinks:

        currentCat = catLink.split("/")[-2]

        # Création d'un Data Frame
        col = [
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
        DF = pd.DataFrame(columns=col)

        catPage = requests.get(catLink)

        # première page de la catégorie à explorer
        if catPage.ok:
            htmlCatPage = BeautifulSoup(catPage.content, "html.parser")
            # Checkpages : permet de contrôler s'il existe d'autres pages dans cette catégorie
            checkPages = htmlCatPage.find("li", class_="current")
            links = [catLink]
            # Si une page suivante est identifiée, on repère le nombre total de pages à incrémenter dans la variables links
            if checkPages is not None:
                nbPages = int(checkPages.string.split()[-1])
                for page in range(2, nbPages + 1):
                    links.append(
                        catLink[0 : -catLink[::-1].index("/")]
                        + "page-"
                        + str(page)
                        + ".html"
                    )

        # La variable books nous permettra de recueillir les liens vers chacun des livres de la catégorie.
        books = []
        for link in links:
            page = requests.get(link)
            html = BeautifulSoup(page.content, "html.parser")

            for book in html.find_all(
                "a"
            ):  # Loop pour chaque lien identifié : on l'enregistre dans la liste de links
                if ("thumbnail" in str(book)) and (
                    urlStart + "catalogue/" + book.get("href") not in books
                ):
                    books.append(
                        urlStart + "catalogue/" + book.get("href").replace("../", "")
                    )

        ratingStr = ["Zero", "One", "Two", "Three", "Four", "Five"]

        # Chaque page "livre" va être examinée afin d'en tirer les informations demandées.
        for bookLink in books:
            bookHtml = BeautifulSoup(requests.get(bookLink).content, "html.parser")
            bookData = [  # récupération des données du livre
                # Page URL
                bookLink,
                # UPC
                bookHtml.find("td").text,
                # Titre
                bookHtml.find("h1").text,
                # Prix TTC
                float(bookHtml.find_all("td")[2].text[1:]),
                # PRIX HT
                float(bookHtml.find_all("td")[3].text[1:]),
                # Stock (extraction des digits avec "re.findall")
                re.findall("\d+", bookHtml.find_all("td")[5].text)[0],
                # Description
                bookHtml.find_all("p")[3].text,
                # Categorie
                bookHtml.find_all("a")[3].text,
                # Score
                ratingStr.index(str(bookHtml.find_all("p")[2].attrs["class"][1])),
                # Lien de l'image
                urlStart + bookHtml.find("img").attrs["src"],
            ]

            # La ligne spécifique au livre est ajoutée au data frame
            DF.loc[len(DF)] = bookData

            # Téléchargement de l'image
            if "Images" not in os.listdir():
                os.mkdir("Images")
                cdir = os.getcwd()
            os.chdir(cdir + "\Images")
            img_data = requests.get(bookData[-1]).content
            with open(
                ("Cover page - " + bookData[7] + "." + bookData[1] + ".jpg"), "wb"
            ) as handler:
                handler.write(img_data)
            os.chdir(cdir)

        # Enregistrement des données dans le data frame

        DF.to_csv("ScrapedBooks - Category " + currentCat + ".csv", sep=";")
