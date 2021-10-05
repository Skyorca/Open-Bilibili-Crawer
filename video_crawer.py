import requests
from requests.adapters import HTTPAdapter
import time
import json
import random
from typing import List, Union, Dict


class VideoCrawer():
    def __init__(self, mid, cookie_string, max_retries=3, max_videopage=4, max_keep_tags = 50):
        """
        以一个人为中心，爬取它的视频信息。最多爬取100个视频，并计算视频类型统计、视频标签统计，以及各视频统计情况
        """
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries))
        self.s.mount('https://', HTTPAdapter(max_retries))
        self.mid = mid
        self.max_videopage = max_videopage
        self.max_keep_tags = max_keep_tags
        self.cookies = dict(map(lambda x:x.split('='),cookie_string.split(";")))
        self.s.cookies = requests.utils.cookiejar_from_dict(self.cookies, cookiejar=None, overwrite=True)

    def getVideos(self)->Union[List,Dict]:
        aids = []
        typeid_counts = {}  #视频的type的统计信息，以typeid为标识
        for i in range(self.max_videopage):  # 爬最近100个视频 4*25
            videos = self.s.get(f"https://api.bilibili.com/x/space/arc/search?mid={self.mid}&pn={i+1}&ps=25&index=1&jsonp=jsonp", timeout=10)
            videos_info = videos.json()
            if 'data' in videos_info:
                for v in videos_info['data']['list']['vlist']:
                    aids.append(v['aid'])
                    if str(v['typeid']) in typeid_counts: typeid_counts[str(v['typeid'])]+=1
                    else: typeid_counts[str(v['typeid'])] = 1
            time.sleep(random.uniform(0,2))
        return aids, typeid_counts

    def getVideoTags(self, aid) -> Union[Dict, List]:
        try:
            page = self.s.get(f"https://api.bilibili.com/x/web-interface/view/detail/tag?aid={aid}", timeout=10)
        except requests.exceptions.RequestException as error:
            print(error)
            return {},[]
        page_info = page.json()
        if 'data' in page_info and page_info['data']:
            tags = {}  # tag详细信息 {tagid:{xx,xx,xx,xx},...}
            tids = []  # tagid 一个视频的tag应该没有重复的
            for tag in page_info['data']:
                tags.update({str(tag['tag_id']):{"tid":tag['tag_id'],"tag_name":tag['tag_name'], 'subscribe':tag['subscribed_count'],'use':tag['count']['use'],'feature':tag['featured_count']}})
                tids.append(str(tag['tag_id']))
            return tags, tids
        else:
            return {}, []
    
    def getVideoStat(self,aid)->dict:
        self.s.headers.update({'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"})
        try:
            stat = self.s.get(f"https://api.bilibili.com/x/web-interface/archive/stat?aid={aid}", timeout=10)
        except requests.exceptions.RequestException as error:
            print(error)
            return {}
        time.sleep(random.uniform(0,2))
        stat_info = stat.json()
        if 'data' in stat_info and stat_info['data']:
            # need: aid bvid view danmaku reply favorite coin share like his_rank
            stat_need = stat_info['data']
            stat_need.pop("no_reprint")
            stat_need.pop("copyright")
            stat_need.pop("argue_msg")
            stat_need.pop("evaluation")
            stat_need.pop("now_rank")
            return stat_need
        else:
            return {}

    def runVideoCraw(self):
        # all_typeids 每个人视频类型id的统计信息
        all_aids, all_typeids = self.getVideos()
        print(f"{self.mid}: {len(all_aids)} videos found!!!")
        all_tagids = {}  # 每个人标签id的统计信息
        all_taginfo = {}  # 对每个人，去重后的所有标签id及其基本信息,这个需要去全局再统一去重一次
        all_stat = []  # 每个人，其所有视频统计数据的列表
        cnt = 0
        for aid in all_aids:
            tags_info, tids = self.getVideoTags(aid)
            time.sleep(random.uniform(2,4))
            stat = self.getVideoStat(aid)
            time.sleep(random.uniform(2,4))
            for tagid, tag_info in tags_info.items():
                if tagid not in all_taginfo: all_taginfo.update({tagid:tag_info})
            for tid in tids:
                if tid not in all_tagids: all_tagids[tid] = 1
                else: all_tagids[tid] += 1
            all_tagids = list(sorted(all_tagids.items(), key=lambda x:x[1], reverse=True))[:self.max_keep_tags]
            all_tagids = {x[0]:x[1] for x in all_tagids}
            all_stat.append(stat)
            cnt += 1
            if cnt%25==0: print(f"{self.mid}: {cnt} videos analyzed!!!")
        return all_typeids, all_tagids, all_stat, all_taginfo

