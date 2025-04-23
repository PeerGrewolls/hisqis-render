from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import hashlib
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("HISQIS_USERNAME")
password = os.getenv("HISQIS_PASSWORD")
pushover_user_key = os.getenv("PUSHOVER_USER_KEY")
pushover_api_token = os.getenv("PUSHOVER_API_TOKEN")

def sende_push_benachrichtigung():
    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": pushover_api_token,
        "user": pushover_user_key,
        "title": "HISQIS Update",
        "message": "Es gibt eine neue Note auf HISQIS!",
        "priority": 1
    })

def get_noten_hash(html):
    soup = BeautifulSoup(html, 'html.parser')
    inhalt = soup.get_text()
    return hashlib.md5(inhalt.encode('utf-8')).hexdigest()

def main():
    options = Options()
    options.add_argument("--headless")  # für Tests sichtbar lassen
    options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    # Startseite mit Session
    driver.get("https://qis.dez.tu-dresden.de/qisserver/servlet/de.his.servlet.RequestDispatcherServlet?state=user&type=1&category=auth.login&startpage=portal.vm")

    # Login
    wait.until(EC.presence_of_element_located((By.NAME, "asdf")))
    driver.find_element(By.NAME, "asdf").send_keys(username)
    driver.find_element(By.NAME, "fdsa").send_keys(password)
    driver.find_element(By.NAME, "submit").click()

    # Klick: Prüfungsbescheinigungen
    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Prüfungsbescheinigungen (HTML, PDF)")))
    driver.find_element(By.LINK_TEXT, "Prüfungsbescheinigungen (HTML, PDF)").click()

    # Klick: Leistungen für Abschluss 11 Diplom anzeigen
    wait.until(EC.presence_of_element_located((By.XPATH, "//a[@title='Leistungen für Abschluss 11 Diplom anzeigen']")))
    driver.find_element(By.XPATH, "//a[@title='Leistungen für Abschluss 11 Diplom anzeigen']").click()



    # Seite ist geladen, HTML holen
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    html = driver.page_source
    driver.quit()

    # Hash berechnen und vergleichen
    new_hash = get_noten_hash(html)

    try:
        with open('last_hash.txt', 'r') as f:
            old_hash = f.read()
    except FileNotFoundError:
        old_hash = ''

    if new_hash != old_hash:
        print("Änderung entdeckt!")
        sende_push_benachrichtigung()
        with open('last_hash.txt', 'w') as f:
            f.write(new_hash)
    else:
        print("Keine Änderung.")
        
if __name__ == "__main__":
    main()
