import requests
from bs4 import BeautifulSoup

def parser_hockey():
    URL = "https://news.sportbox.ru/Vidy_sporta/Hokkej"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    post = soup.find("div", class_="_Sportbox_Spb2015_Components_TeazerBlock_TeazerBlock")
    url = post.find("a", class_="", href=True)["href"].strip()
    title = post.find("span", class_="text").text.strip()
    return f'{title}\n<a href="https://news.sportbox.ru{url}">Подробнее:</a>'


def parser_football():
    URL = "https://news.sportbox.ru/Vidy_sporta/Futbol"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    post = soup.find("div", class_="_Sportbox_Spb2015_Components_TeazerBlock_TeazerBlock")
    url = post.find("a", class_="", href=True)["href"].strip()
    title = post.find("span", class_="text").text.strip()
    return f'{title}\n<a href="https://news.sportbox.ru{url}">Подробнее:</a>'


def parser_volleyball():
    URL = "https://news.sportbox.ru/Vidy_sporta/Volejbol"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    post = soup.find("div", class_="_Sportbox_Spb2015_Components_TeazerBlock_TeazerBlock")
    url = post.find("a", class_="", href=True)["href"].strip()
    title = post.find("span", class_="text").text.strip()
    return f'{title}\n<a href="https://news.sportbox.ru{url}">Подробнее:</a>'
