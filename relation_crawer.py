import requests
from requests.adapters import HTTPAdapter
import time
import json
import random



class RelationCrawer():
    def __init__(cookie_string, group_mids, max_pagesize=5, max_retries=3):
        """
        只关注following关系，不关注额外的follower关系
        @params:
        group_mids: 需要限制在这一组用户里搜索关系
        """
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries=3))
        self.s.mount('https://', HTTPAdapter(max_retries=3))
        self.cookies = dict(map(lambda x:x.split('='),cookie_string.split(";")))
        self.s.cookies = requests.utils.cookiejar_from_dict(self.cookies, cookiejar=None, overwrite=True)
        self.max_pagesize = max_pagesize
        self.group_mids = group_mids  

    def getFollow(self,mid):
        """
        mid: 对属于group的一个人，爬取following关系
        """
        edges = []
        for i in range(self.max_pagesize):
            try:
                    following_info = s.get(f"https://api.bilibili.com/x/relation/followings?vmid={mid}&pn={i+1}&ps=20&order=desc",timeout=10)
                except requests.exceptions.RequestException as error:
                    print(error)
                    time.sleep(random.uniform(0,2))
                    break
                # 请求被拦截时data是None
                try:
                    if 'data' in following_info.json() and 'list' in following_info.json()['data']:
                        following = following_info.json()['data']['list']
                        for user in following:
                            if user['mid'] not in self.group_mids: continue
                            edges.append((mid, user['mid'],'following'))
                        time.sleep(random.uniform(0,2))
                except TypeError as err:
                    print(err)
                    time.sleep(random.uniform(0,2))
                    pass
        return edges


