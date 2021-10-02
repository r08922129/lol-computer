from json import loads as json_loads
from json import dump as json_dump
from os import makedirs
from os import listdir
from os.path import join as join_path
from abc import ABC
from utils import *
from scraper import *
from requests import get
from bs4 import BeautifulSoup
from PyQt5.QtCore import QCoreApplication

class ChampionResourceScraper(ABC):
    def __init__(self, next_scraper, textBrowser):
        self.next = next_scraper
        self.textBrowser = textBrowser

    def get_champions_resources(self):
        if not self.get_champions_resources_internal():
            self.textBrowser.write("Failed to go throught the update chain.")
        elif self.next:
            self.next.get_champions_resources_internal()

class FandomScraper(ChampionResourceScraper):

    def __init__(self, next_scraper, progressBar, textBrowser, path_to_champions="champions"):
        super().__init__(next_scraper, textBrowser)
        self.root = "https://leagueoflegends.fandom.com"
        self.path_to_champions = path_to_champions
        self.progressBar = progressBar

    def get_champions_resources_internal(self):

        try:
            champion_url = self.get_champion_url()
        except:
            self.textBrowser.write("Failed to get champions in the website: {}".format(len(champion_url), self.root))
            return False

        self.textBrowser.write("There are total {} champions in the website: {}".format(len(champion_url), self.root))
        self.textBrowser.write("Crawling data for each champions...")
        for i, url in enumerate(champion_url):
            try:
                response = get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                champion_name = self.get_champion_name(soup)
                champion_skill_cd = self.get_champion_skill_cd(soup)
                self.save_resource(champion_name, champion_skill_cd)
                self.progressBar.setValue(i/len(champion_url) * 100)

            except Exception as e:
                self.textBrowser.write("Exception occurred when parsing {}.".format(url))
                self.textBrowser.write(e)
            QCoreApplication.processEvents()

            self.progressBar.setValue(i/len(champion_url) * 100)

        return True


    def save_resource(self, champion_name, champion_skill_cd):
        champion_names = listdir(self.path_to_champions)
        matched_name = match_champion_name(champion_name, champion_names)
        print(champion_name, matched_name)
        with open(join_path(self.path_to_champions, matched_name, "skill.json"), "w") as f:
            skills = {
                "Q" : champion_skill_cd[0],
                "W" : champion_skill_cd[1],
                "E" : champion_skill_cd[2],
                "R" : champion_skill_cd[3],
            }
            json_dump(skills, f)

    def get_champion_url(self):
        champions_list_url = self.root + "/wiki/List_of_champions"
        response = get(champions_list_url)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="article-table")
        rows = table.find_all("div", class_="floatleft")

        champion_url = set()
        for row in rows:
            segment = row.find("a").get("href").replace("/wiki/", "")
            url = "/".join([self.root, "wiki", segment, "LoL"])
            champion_url.add(url)
        return champion_url

    def get_champion_name(self, soup):
        name = soup.find("div", class_="league-font").find("span").text.lower()
        return name

    def get_champion_skill_cd(self, soup):
        skill_cd = []
        items = soup.find_all("h3", string="COOLDOWN:")
        class_names = ["skill skill_q", "skill skill_w", "skill skill_e", "skill skill_r"]

        for class_name in class_names:
            try:
                cooldown = soup.find("div", class_=class_name)\
                        .find("h3",string="COOLDOWN:")\
                        .find_next_sibling("div")\
                        .text.split("/")

                if len(cooldown) == 1:
                    cooldown = cooldown * 6

                skill_cd.append(cooldown)
            except:
                skill_cd.append(None)

        return skill_cd

class OPGGScraper(ChampionResourceScraper):

    def __init__(self, next_scraper, progressBar, textBrowser, path_to_champions="champions"):
        super().__init__(next_scraper, textBrowser)
        self.progressBar = progressBar
        self.root = "https://tw.op.gg"
        self.path_to_champions = path_to_champions
        self.name_zh_to_key = {}
        self.key_to_name_en = {}

    def get_champions_resources_internal(self):
        # get name-en and tag
        return True
        try:
            response = get(self.root + "/champion/statistics", headers={"Cookie":'customLocale=en-US'})
            soup = BeautifulSoup(response.text, "html.parser")
            champion_list = soup.find("div", class_="champion-index__champion-list")
            champion_items = champion_list.find_all("div", class_="champion-index__champion-item")
            for i, champion_item in enumerate(champion_items):
                champion_name_en, key = self.get_name_and_key(champion_item)
                self.key_to_name_en[key] = champion_name_en
        except:
            self.textBrowser.write("Fail to get keys of champions from {}".format(response.url))
            return False
        try:
            response = get(self.root + "/champion/statistics")
            soup = BeautifulSoup(response.text, "html.parser")
            champion_list = soup.find("div", class_="champion-index__champion-list")
            champion_items = champion_list.find_all("div", class_="champion-index__champion-item")
        except:
            self.textBrowser.write("Fail to get champion items from {}".format(response.url))
            return False

        self.textBrowser.write("Crawling images...")
        for i, champion_item in enumerate(champion_items):
            # chinese name
            try:
                champion_name_zh, key = self.get_name_and_key(champion_item)
                champion_name_en = self.key_to_name_en[key]
                # make directory
                champion_directoy = join_path(self.path_to_champions, champion_name_en.lower())
                makedirs(champion_directoy, exist_ok=True)
            
                with open(join_path(champion_directoy, f"name.json"), "w") as f:
                    properties = {
                        "en-us" : champion_name_en,
                        "zh-tw" : champion_name_zh,
                    }
                    json_dump(properties, f)
            except:
                if champion_name_en is None:
                    self.textBrowser.write("Error occurred when fetching a champion name.")
                else:
                    self.textBrowser.write("Error occurred when fetching {}'s name.".format(champion_name_en))
                continue
            # to get image
            try:
                suffix = champion_item.find("a").get("href")
                link = self.root + suffix
                response = get(link)
                soup = BeautifulSoup(response.text, "html.parser")
                img_url = soup.find("div", class_="champion-stats-header-info__image").find("img").get("src")
                response = get(f"https:{img_url}")
                img = response.content
                with open(join_path(champion_directoy, "img.png"), "wb") as f:
                    f.write(img)
            except:
                self.textBrowser.write("Error occurred when fetching the image of {}".format(champion_name_en))

            self.progressBar.setValue(i/len(champion_items) * 100)
            QCoreApplication.processEvents()

        return True

    def get_name_and_key(self, champion_item):
        champion_name = champion_item.find("div", class_="champion-index__champion-item__name").text
        key = champion_item.get("data-champion-key")
        return champion_name, key


class DataDragonScraper(ChampionResourceScraper):

    def __init__(self, next_scraper, progressBar, textBrowser, path_to_champions="champions"):
        super().__init__(next_scraper, textBrowser)
        self.urls = {
            "champions" : "http://ddragon.leagueoflegends.com/cdn/11.19.1/data/zh_TW/champion.json",
        }
        self.regions = [
            "en_US", "zh_TW"
        ]
        self.path_to_champions = path_to_champions
        self.progressBar = progressBar
    
    def get_champions_resources_internal(self):

        self.textBrowser.write("Getting the chamopions from ddragon.")
        try:
            response = get(self.urls["champions"])
            champions = json_loads(response.text)["data"]
        except Exception as e:
            self.textBrowser.write("Failed to getting champion data from ddragon.")
            return False

        for i, champion_id in enumerate(champions):

            version = champions[champion_id]["version"]
            for region in self.regions:
                champion_url = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/{region}/champion/{champion_id}.json"
                response = get(champion_url)
                champion_info = json_loads(response.text)

                champion_directoy = join_path(self.path_to_champions, champion_id)
                makedirs(champion_directoy, exist_ok=True)
                with open(join_path(champion_directoy, f"info-{region}.json"), "w") as f:
                    json_dump(champion_info, f)


            img = champions[champion_id]["image"]["full"]
            img_url = f"http://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{img}"
            response = get(img_url)
            with open(join_path(champion_directoy, "img.png"), "wb") as f:
                f.write(response.content)
            
            self.progressBar.setValue(i/len(champions) * 100)
            QCoreApplication.processEvents()
        return True
        
