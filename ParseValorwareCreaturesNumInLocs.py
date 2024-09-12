url_enemies = "https://www.valorware.com/9d3guide_/subPages/_enemyList.html"
url_locations = "https://www.valorware.com/9d3guide_/subPages/_locationList.html"

headers = {  # For preventing ban DDOS
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36"
}

import requests
import os
from bs4 import BeautifulSoup

# скачиваем сайт с врагами _____________________________________________________________________________________________
# req = requests.get(url_enemies, headers=headers)
# enemy_src = req.text[3:]
# os.makedirs(os.path.dirname("roots/enemy_index.html"), exist_ok=True)
# with open("roots/enemy_index.html", "w") as f:
#     f.write(enemy_src)

# скачиваем сайт с локациями ___________________________________________________________________________________________
# req = requests.get(url_locations, headers=headers)
# loc_init_src = req.text[3:]
# os.makedirs(os.path.dirname("roots/location_index.html"), exist_ok=True)
# os.makedirs(os.path.dirname("roots/locations/"), exist_ok=True)
# with open("roots/location_index.html", "w") as f:
#     f.write(loc_init_src)
#     dwnld_soup = BeautifulSoup(loc_init_src, features="html.parser")
#     dwnld_soup.find('center').decompose()
#     for item in dwnld_soup.findAll(href=True):
#         loc_url = 'https://www.valorware.com/9d3guide_' + item["href"][2:].replace('\\', '/')
#         req = requests.get(loc_url, headers=headers)
#         loc_src = req.text[3:]
#         with open("roots/locations/" + item.text + ".html", "w") as loc_f:
#             loc_f.write(loc_src)

# обрабатываем врагов __________________________________________________________________________________________________
import re
enemy_dict = {}
with open("roots/enemy_index.html", encoding="utf-8") as f:
    src = f.read()

enemy_soup = BeautifulSoup(src, features="html.parser")
def tr_has_td_child(tag):  # Ввели функцию по которой проверяем, что у тега tr есть чайлд-тэг td
    return tag.name == 'tr' and tag.find('td') is not None

for item in enemy_soup.findAll(tr_has_td_child):
    # Достаем катинку
    img_url = 'https://www.valorware.com/9d3guide_' + \
              item.select("td:nth-child(" + str(2) + ")")[0].findAll(src=re.compile(r'^(?!.*transparent).*'))[0]['src'][2:].replace('\\', '/')
    level = item.select("td:nth-child(" + str(3) + ")")[0].text.replace(',', "")
    health = item.select("td:nth-child(" + str(4) + ")")[0].text.replace(',', "")
    total_in_game = item.select("td:nth-child(" + str(5) + ")")[0].text.replace(',', "")
    enemy_dict[item.find_next().text + ' lvl_' + level] = {'img': img_url, 'lvl': int(level), 'hp': int(health), 'cnt': int(total_in_game), 'locs': {}}

# обрабатываем локации _________________________________________________________________________________________________
locations_dict = {}
with open("roots/location_index.html", encoding="utf-8") as f:
    loc_init_src = f.read()
loc_init_soup = BeautifulSoup(loc_init_src, features="html.parser")
loc_init_soup.find('center').decompose()

for item in loc_init_soup.findAll(href=True):
    loc_url = 'https://www.valorware.com/9d3guide_' + item["href"][2:].replace('\\', '/')
    locations_dict[item.text] = {"loc_url": loc_url, "loc_enemies": {}}

    with open("roots/locations/" + item.text + ".html", encoding="utf-8") as f:
        loc_src = f.read()
    loc_soup = BeautifulSoup(loc_src, features="html.parser")

    loc_soup_table = loc_soup.find("table", style="width:700px")
    for t_row in loc_soup_table.findAll(tr_has_td_child):
        enemy_level = t_row.select("td:nth-child(" + str(3) + ")")[0].text
        enemy_name = t_row.find_next().text
        total_in_loc = int(t_row.select("td:nth-child(" + str(4) + ")")[0].text.replace(',', ""))
        locations_dict[item.text]['loc_enemies'][enemy_name + ' lvl_' + enemy_level] = locations_dict[item.text]['loc_enemies'].get(enemy_name + ' lvl_' + enemy_level, 0) + total_in_loc

# собираем все в словарь врагов ________________________________________________________________________________________
for en in enemy_dict:
    for loc in locations_dict:
        if en in locations_dict[loc]['loc_enemies'].keys():
            enemy_dict[en]['locs'][loc] = locations_dict[loc]['loc_enemies'][en]

# собираем таблицу врагов как на сайте _________________________________________________________________________________
enemy_soup.find('center').decompose()
enemy_soup.find('br').decompose()
enemy_soup.find('br').decompose()
enemy_soup.find('br').decompose()
enemy_soup.find('br').decompose()

# new header
new_tag = enemy_soup.new_tag('th')
new_tag.string = 'Locations:'
enemy_soup.findAll('th')[-1].insert_after(new_tag)
gener_of_widths = (x for x in [27, 10, 10, 10, 12]) # forming generator
for th in enemy_soup.findAll('th')[:-1]:
    th['width'] = '"' + str(next(gener_of_widths)) + '"'
# new column
for tr in enemy_soup.findAll('tr')[1:]:
    new_tag = enemy_soup.new_tag('td', align="right", valign="middle")
    enemy_name = tr.find_next().text
    enemy_level = tr.select("td:nth-child(" + str(3) + ")")[0].text
    tr.find(src=re.compile(r'^(?!.*transparent).*'))['src'] = enemy_dict[enemy_name + ' lvl_' + enemy_level]['img']
    sorted_list = sorted(enemy_dict[enemy_name + ' lvl_' + enemy_level]['locs'].items(), key=lambda x: x[1], reverse=True)
    for loc_tuple in sorted_list:
        new_tag.insert(len(new_tag.contents), loc_tuple[0] + ": " + str(loc_tuple[1]))
        new_tag.insert(len(new_tag.contents), enemy_soup.new_tag('br'))
    cnt_difference = enemy_dict[enemy_name + ' lvl_' + enemy_level]['cnt'] - sum(enemy_dict[enemy_name + ' lvl_' + enemy_level]['locs'].values())
    if cnt_difference > 0:
        new_tag.insert(len(new_tag.contents), 'World map: ' + str(cnt_difference))
    tr.findAll('td')[-1].insert_after(new_tag)

from PIL import Image
# from io import BytesIO
# response = requests.get(enemy_dict["Rat"]["img"])
# im = Image.open(BytesIO(response.content))
# im.show()

with open("roots/final.html", "w") as f:
    f.write(str(enemy_soup.prettify()))

