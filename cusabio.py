import requests
from bs4 import BeautifulSoup
import lxml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import re
import time
from datetime import datetime
from random import randrange
import csv

URL = "https://www.cusabio.com/"

# URL = "https://www.cusabio.com/Polyclonal-Antibody/MNDA-Antibody-11095443.html"
# URL = "https://www.cusabio.com/Polyclonal-Antibody/MEF2B-Antibody-11092097.html"
# URL = "https://www.cusabio.com/Monoclonal-Antibody/CD9-Monoclonal-Antibody-12928588.html"

#  CSB-PA010214, CSB-PA003215, CSB-PA023302HA01HU, CSB-PA022431LA01HU

# def get_data(url):
    # headers = {
    #     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    # }
    # req = requests.get(url, headers)

    # with open("data-cus\\article-mon.html", "w", encoding="utf-8") as file:
    #     file.write(req.text)
    # with open("data-cus\\article-mon.html", encoding="utf-8") as file:
    #     src = file.read()
    # return src

def get_art_page(driver, art):

    time.sleep(2)
    try:
        search_bar = driver.find_elements(By.ID, "nav_search_q")[1]
        search_bar.clear()
        time.sleep(1)
        search_bar.send_keys(art + Keys.ENTER)
        time.sleep(3)

    except:
        print('Can`t find search input')
    try:
        driver.find_element(By.CLASS_NAME, "text-middle").click()
    except:
        print('can`t find tag a for art ' + art)
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[1])
    return driver.page_source

def get_soup(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        return soup
    except:
        print('No soup!')

def get_art_structure(soup, art):

    reactivity_dict = {
        "Human": "человек",
        "Mouse": "мышь",
        "Rat": "крыса"
    }

    application_dict = {
        "WB": "вестерн-блоттинга",
        "IHC": "иммуногистохимии",
        "IHC-P": "иммуногистохимии на парафиновых срезах",
        "IF/ICC": "иммунофлуоресцентного/иммуноцитохимического анализа",
        "ICC": "иммуноцитохимического анализа",
        "IF": "иммунофлуоресцентного анализа",
        "IP": "иммунопреципитации",
        "ChIP": "иммунопреципитации хроматина",
        "ChIP-seq": "иммунопреципитации хроматина и высокоэффективного секвенирования",
        "RIP": "иммунопреципитации РНК",
        "FC": "проточной цитометрии",
        "FC(Intra)": "проточной цитометрии (Intra)",
        "ELISA": "ИФА",
        "MeDIP": "иммунопреципитации метилированной ДНК",
        "Nucleotide Array": "исследования нуклеотидных последовательностей",
        "DB": "дот-блоттинга",
        "FACS": "сортировки клеток, активируемых флуоресценцией",
        "CoIP": "коиммунопреципитации",
        "CUT&Tag": "CUT&Tag секвенирование",
        "meRIP": "иммунопреципитации метилированной РНК"
    }

    article_sib = soup.find("td", string="Code")
    if article_sib:
        article = article_sib.find_next_sibling("td").get_text().strip()
    else:
        print("Can`t find article")
        article = art

    volume_vars = soup.find("select", id="dvSpecific")
    volumes = []
    volume_units = []
    prices = []
    if volume_vars:
        volume_con = volume_vars.find_all("option")
        volumes_f = [volume.get_text().strip() for volume in volume_con]
        for volume in volumes_f:
            for i in range(0, len(volume)):
                if volume[i].isdigit():
                    continue
                else:
                    volumes.append(volume[:i])
                    volume_units.append(volume[i:].replace("μ", "u").lower())
                    break
        prices = [price["price"].strip() for price in volume_con]
    else:
        print("Can`t find volumes and prices")

    antigen_sib = soup.find("div", string="Target Names")
    if antigen_sib:
        antigen = antigen_sib.find_next_sibling("div").get_text().strip()
    else:
        print("No antigen")
        antigen = ""
# TODO переписать на функцию с поиском сиблинга

    # siblings_dict = {
    #     article: "Code",
    #     antigen: "Target Names",
    #     reactivity: "Species Reactivity",
    #     host: "Raised in",
    #     appls: "Tested Applications",
    #     clonality: "Clonality"
    # }

    # def get_next_siblig_text(soup, txt, var_name):
    #     container = soup.find("div", string=txt)

    #     if container:
    #         var_name = container.find_next_sibling("div").get_text().strip()
    #     else:
    #         print("Can`t find {var_name}")
    #         var_name = ""
    #     return var_name

    reactivity_con = soup.find("div", string="Species Reactivity")
    if reactivity_con:
        reactivity = reactivity_con.find_next_sibling("div").get_text().strip()
    else:
        print("Can`t find reactivity")
        reactivity = ""
    host_cont = soup.find("div", string="Raised in")
    if host_cont:
        host = host_cont.find_next_sibling("div").get_text().strip()
    else:
        print("No host")
        host = ""
    appls_con = soup.find("div", string="Tested Applications")
    if appls_con:
        appls = appls_con.find_next_sibling("div").get_text().strip()
    else:
        appls = ""
        print("No appls")
    clonality_con = soup.find("div", string="Clonality")
    if clonality_con:
        clonality = clonality_con.find_next_sibling("div").get_text().strip()
    else:
        clonality = "Polyclonal"
        clone = ""
        print("No clon/clonality")
        # TODO проверить логику с клонами
    if clonality.lower() == "monoclonal":
        clone = soup.find("div", string="Clone No.").find_next_sibling("div").get_text().strip()
    else:
        clone = ""

    title_con = soup.find("div", class_="product-name")
    if title_con:
        title = title_con.find("h1").get_text().strip()
    else:
        title = ""
        print("No title")
    dilutions = []
    ihc_dil = ""
    dilus_tbl = soup.find("table", class_="table table-bordered").find_all("tr")
    if dilus_tbl:
        appl_names = []
        dilus_txts = []
        for tr in dilus_tbl:
            td_list = tr.find_all("td")
            if len(td_list) > 0:
                appl_name = td_list[0].get_text().strip()
                dilus_txt = td_list[1].get_text().strip()
                appl_names.append(appl_name)
                dilus_txts.append(dilus_txt)
                dilutions.append(appl_name + " " + dilus_txt)
                if appl_name == "IHC" or appl_name == "IHC-P":
                    ihc_dil = dilus_txt
        if len(appls.split(", ")) != len(dilutions):
            for appl in appls.split(", "):
                if not appl in appl_names:
                    dilutions.append(appl)
        if len(ihc_dil) > 0:
            application_dict["IHC"] = "иммуногистохимии (рекомендуемое разведение " + ihc_dil + ")"
            application_dict["IHC-P"] = "иммуногистохимии на парафиновых срезах (рекомендуемое разведение " + ihc_dil + ")"
    else:
        print('No dilus')

    if len(appls) > 0:
        appls_ru = ", ".join([application_dict.get(w.strip(), w.strip()) for w in appls.split(",")])
    else:
        appls_ru = ""
        print("No ru appls")
    reactivity_ru = ", ".join([reactivity_dict.get(w.strip(), w.strip()) for w in reactivity.split(",")])
    text = "\n".join(dilutions) + "\n" + reactivity
    # print(text)
    conjug = soup.find("div", string="Conjugate").find_next_sibling("div").get_text().strip()
    storage = soup.find("div", string="Storage").find_next_sibling("div").get_text().strip()
    storage_buff = soup.find("div", string="Buffer").find_next_sibling("div").get_text().strip()
    conc = soup.find("div", string="Concentration").find_next_sibling("div").get_text().strip()

    dict_art_list = []
    for i in range(0, len(volumes)):
        dict_art = {
            "Article": article,
            "Volume": volumes[i],
            "Volume units": volume_units[i],
            "Antigen": antigen,
            "Host": host,
            "Clonality": clonality,
            "Clone_num": clone,
            "Text": text,
            "Applications_ru": appls_ru,
            "Reactivity_ru": reactivity_ru,
            "Title": title,
            "Applications": appls,
            "Dilutions": ", ".join(dilutions),
            "Reactivity": reactivity,
            # "Form": form,
            "Conjugation": conjug,
            "Storage instructions": storage,
            "Storage buffer": storage_buff,
            "Concentration": conc,
            "Price": prices[i],
        }
        dict_art_list.append(dict_art)
    # print(dict_art_list)
    return dict_art_list

def write_csv(result):
    date = datetime.now().strftime('%d.%m.%Y_%H.%M')
    with open("data-cus\\Cusabio_{}.csv".format(date), "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=result[0].keys())
        writer.writeheader()
        writer.writerows(result)

def get_articles_list():
    print("Введите список артикулов:")
    articles = [str(art).strip() for art in input().split(",")]
    return articles

service = Service("C:\\Users\\Public\\Parsing programs\\chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
# options.add_argument("--disable-gpu")
# options.add_argument("--headless")
options.add_argument("--ignore-certificate-errors-spki-list")
options.add_argument("--ignore-ssl-errors")
options.add_argument("--disable-infobars")
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()
driver.get(URL)
print("Main site opened")
time.sleep(3)


try:
    arts = get_articles_list()
    start_time = datetime.now()
    result = []
    counter = 0
    for art in arts:
        counter += 1
        print(counter, " art No ", art)
        src = get_art_page(driver, art)
        soup = get_soup(src)
        art_info = get_art_structure(soup, art)
        result.extend(art_info)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    # print(result)
    write_csv(result)
    finish_time = datetime.now()
    spent_time = finish_time - start_time
    print(spent_time)

except Exception as ex:
    print(ex)
finally:
    # driver.close()
    driver.quit()
    print('Driver closed')
