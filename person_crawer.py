import requests
from requests.adapters import HTTPAdapter
import time
import json
import random
from typing import List, Union, Dict


class PersonCrawer():
    def __init__(self, mid, cookie_string, max_retries=3):
        """
        以一个人mid为中心，爬取它的个人信息
        """
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries))
        self.s.mount('https://', HTTPAdapter(max_retries))
        self.mid = mid
        self.cookies = dict(map(lambda x:x.split('='),cookie_string.split(";")))
        self.s.cookies = requests.utils.cookiejar_from_dict(self.cookies, cookiejar=None, overwrite=True)
        self.person_info = {"mid":self.mid}

    def addFollow(self):
        try:
            page = self.s.get(f"https://api.bilibili.com/x/relation/stat?vmid={self.mid}&jsonp=jsonp", timeout=10)
        except requests.exceptions.RequestException as error:
            print(self.mid, error)
        page_info = page.json()
        if 'data' in page_info and page_info['data']:
            following = page_info['data']['following']
            follower = page_info['data']['follower']
        self.person_info.update({"nfollowing":following, "nfollower":follower})

    def addBasic(self):
        try:
            page = self.s.get(f"https://api.bilibili.com/x/space/acc/info?mid={self.mid}&jsonp=jsonp", timeout=10)
        except requests.exceptions.RequestException as error:
            print(self.mid, error)
        page_info = page.json()
        if 'data' in page_info and page_info['data']:
            self.person_info.update({"uname":page_info['data']['name']})
            self.person_info.update({"sex":page_info['data']['sex']})
            self.person_info.update({"sign":page_info['data']['sign']})
            self.person_info.update({"level":page_info['data']['level']})
            self.person_info.update({"official":page_info['data']['official']['title']})
            self.person_info.update({"birthday":page_info['data']['birthday']})
            self.person_info.update({"school":page_info['data']['school']['name']})
            self.person_info.update({"profession":page_info['data']['profession']['name']})

    def addStats(self):
        try:
            page = self.s.get(f"https://api.bilibili.com/x/space/upstat?mid={self.mid}&jsonp=jsonp", timeout=10)
        except requests.exceptions.RequestException as error:
            print(self.mid, error)
        page_info = page.json()
        if 'data' in page_info and page_info['data']:
            self.person_info.update({"video_view":page_info['data']['archive']['view']})
            self.person_info.update({"article_view":page_info['data']['article']['view']})
            self.person_info.update({"nlike":page_info['data']['likes']})

    def runPersonCrawer(self):
        self.addBasic()
        time.sleep(random.uniform(0,2))
        self.addFollow()
        time.sleep(random.uniform(0,2))
        self.addStats()
        time.sleep(random.uniform(0,2))
        return self.person_info


