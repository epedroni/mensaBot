#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests
import json
import locale
import calendar
import datetime
import pytz
import random

DEBUG = False 
NOW = datetime.datetime.now(pytz.timezone("Europe/Zurich"))
ETH_MENSA_NOMEAL_STR = "No lunch menu today."
UZH_MENSA_NOMEAL_STR = "{}.{}.{}".format(NOW.day, NOW.strftime("%m"), NOW.year)
UA = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"

def eth_parse_table(table):
    menu = ""
    for row in table[int(not is_lunchtime())].findAll("tr", attrs={"class": None})[0:]:
        cols = row.findAll("td")
        if len(cols) > 1:
            # first comes the header
            menu += "*" + remove_line_breaks(cols[0]).text.title() + "*\n"
            # next the dish
            dish = remove_line_breaks(cols[1]).text.replace("Show details", "")
            dish = dish.replace("Details einblenden", "")

            menu += dish + "\n\n"
    return menu

def uzh_parse_table(table):
    menu = ""
    for m in table:
        heading = m.findAll("div")[0].findAll("h3")[0:-1]
        para = m.findAll("div")[0].findAll("p")
        for i, h in enumerate(heading):
            menu += "*" + h.text.split("|")[0].strip().title() + "*\n"
            menu += " ".join(para[i].text.split()).strip() + "\n\n"
    return menu

def get_eth_menu(url):
    r = requests.get(url, headers={"User-Agent": UA})

    if ETH_MENSA_NOMEAL_STR in r.text:
        return "No ETH menu available for this day!"

    table = BeautifulSoup(r.text, "html.parser").findAll("table")

    return eth_parse_table(table)

def get_uzh_menu():
    # UZH URL actually has the weekday in german
    locale.setlocale(locale.LC_ALL, "de_CH.utf-8")
    curr_day = str(calendar.day_name[(int(NOW.strftime("%w"))+6)%7]).lower()

    if is_lunchtime():
        url = "http://www.mensa.uzh.ch/de/menueplaene/zentrum-mensa/{}.html"
    else:
        url = "http://www.mensa.uzh.ch/de/menueplaene/zentrum-mercato-abend/{}.html"
    r = requests.get(url.format(curr_day))
    
    if not UZH_MENSA_NOMEAL_STR in r.text:
        return "*Cheap mensa:*\nNo UZH menu available for this day!\n\n"
    
    menu_div = BeautifulSoup(r.text, "html.parser").findAll("div", { "class" : "text-basics" })
    menu_div.pop(0)
        
    return "*Cheap mensa:*\n" + uzh_parse_table(menu_div)

def get_poly_menu():
    try:
        return "*Polymensa:*\n" + get_eth_menu("https://www.ethz.ch/en/campus/gastronomie/menueplaene/offerDay.html?language=en&id=12&date={}-{}-{}".format(NOW.year, NOW.strftime("%m"), NOW.strftime("%d")))
    except Exception as e:
        return "*Polymensa:*\nNo food =(\n\n"

def get_asian_menu():
    try:
        return "*Clausiusbar:*\n" + get_eth_menu("https://www.ethz.ch/en/campus/gastronomie/menueplaene/offerDay.html?language=en&id=4&date={}-{}-{}".format(NOW.year, NOW.strftime("%m"), NOW.strftime("%d")))
    except:
        return "*Clausiusbar:*\nNo food =(\n\n"

def is_lunchtime():
    return int(NOW.strftime("%H")) < 14

def remove_line_breaks(element):
    for b in element.findAll("br"):
        b.replaceWith(" ")
    return element

def slack_say(message):
    slack_data = {"channel":"#vippartyroom", "username": "mensamenu", "text": message}
    url = "https://hooks.slack.com/services/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"
    requests.post(url, data=json.dumps(slack_data))

def rocketchat_say(message):
    rocket_data = {"text" : message}
    url = "https://talk.serber.club/hooks/uBQr9rKLvYKKgZzRN/BccPSWFdZEqqBXmaonzP2srBo4zTR45xDrgLm3tQnferGTnJ"
    requests.post(url, data=json.dumps(rocket_data))

def get_easter_egg():
    options = ["SMARTBOT IS WATCHING",
            "BOW BEFORE SUPERBOT",
            "SUPERBOT IS LEGIT",
            "U PICKU MATERINU",
            "SUKA BOT",
            "SMARTBOT IS YOUR FRIEND",
            "TRUST SMARTBOT",
            "SMARTBOT ALWAYS DELIVERS",
            "SMARTBOT KNOWS DE WAE"]
    return options[random.randint(0, len(options) - 1)] + " :fnc-monkey:"

def main():
    menu = "\n" + get_uzh_menu() + get_asian_menu() + "\n\n" + get_easter_egg()
    
    if DEBUG:
        print(menu)
        return

    #slack_say(menu)
    rocketchat_say(menu)

if __name__ == "__main__":
    main()

