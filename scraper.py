'''For scraping deckbox lists. Download the html with type, cost, power, and toughness enabled'''

import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup

def write_deck(path, deck):
    with open(path, 'w') as out:
        out.write(f'Name\tNumber\tType\tCost\tPower\tToughness\tRules\n')
        for card in deck:
            out.write('\t'.join(card) + '\n')

def scrape_deck(html, deck=True):
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.findChildren('table')
    table = tables[3]
    cards = []
    if deck:
        rows = table.findChildren('tr')[3:]
    else:
        # pulling from the inventory
        rows = table.findChildren('tr')[2:]
    for row in rows:
        try:
            card_info = scrape_card(row)
            cards.append(card_info)
        except AttributeError:
            continue
    return cards

def scrape_card(row):
    basic_info = scrape_basic_info(row)
    rules_link = basic_info[0]
    rules = scrape_rules(rules_link)
    card_info = basic_info[1:]
    card_info.append(rules)
    return card_info

def scrape_basic_info(row):
    card_link = row.a.get('href')
    name = row.a.text
    cells = row.findChildren('td')
    number = cells[1].text
    type = cells[5].text
    cost_soup = cells[6]
    cost = get_cost(cost_soup)
    power = cells[7].text
    toughness = cells[8].text
    return [card_link, name, number, type, cost, power, toughness]

def get_cost(cost_soup):
    images = cost_soup.find_all('img')
    costs = []
    for i in images:
        long_cost = i['class'][1]
        short_cost = long_cost.split('_')[-1]
        costs.append(short_cost)
    cost = ' '.join(costs)
    return cost

def scrape_rules(href):
    if href:
        with urllib.request.urlopen(href) as response:
            html = response.read()
    else:
        return
    rules = ''
    cardsoup = BeautifulSoup(html, 'html.parser')
    rows = cardsoup.findAll('tr')
    for i in rows:
        if i.td and i.td.text == 'Rules':
            rules = i.find_all('td')[1].text
    return rules

def get_html(url):
    with urllib.request.urlopen(url) as response:
        html = response.read()
    return html
