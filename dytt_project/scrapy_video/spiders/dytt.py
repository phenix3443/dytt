# -*- coding: utf-8 -*-
import json
import re
import scrapy
import time

from scrapy_video.items import VideoItem


class DyttSpider(scrapy.Spider):
    """电影天堂爬虫"""
    name = 'dytt'
    allowed_domains = ['www.dytt8.net', 'www.ygdy8.net']

    start_urls = ['https://www.dytt8.net/index.htm']

    def parse(self, response):
        """分析首页"""
        # # 最新电影
        # latest_moive_link = response.xpath(
        #     '//*[@id="menu"]/div/ul/li[1]/a/@href').extract_first()
        # yield response.follow(
        #     latest_moive_link, callback=self.parse_latest_movie)

        # yield response.follow(
        #     "http://www.ygdy8.net/html/gndy/dyzz/list_23_182.html",
        #     callback=self.parse_latest_movie)

        yield response.follow(
            # "http://www.ygdy8.net/html/gndy/dyzz/20091004/22009.html",
            "http://www.ygdy8.net/html/gndy/dyzz/20091028/22542.html",
            callback=self.parse_moive_detail)

    def parse_latest_movie(self, response):
        """抓取最新电影列表"""
        # 最新电影列表
        movie_list = response.xpath('//div[@class="co_content8"]')
        detail_links = movie_list.xpath(
            './ul//a[@class="ulink"]/@href').extract()

        for dl in detail_links:
            yield response.follow(dl, callback=self.parse_moive_detail)

        next_page = movie_list.xpath(
            './div//a[contains(.,"下一页")]/@href').extract_first()
        if next_page:
            yield response.follow(next_page, self.parse_latest_movie)

    def parse_moive_detail(self, response):
        """抓取电影详细信息"""
        movie = VideoItem()
        info = response.xpath('//*[@id="Zoom"]')
        pictures = info.xpath('.//img/@src').extract()
        # 海报
        movie["poster"] = pictures[0]
        # 截屏
        movie["screen"] = pictures[1]
        # 磁链接，可能没有
        movie["magnet_link"] = info.xpath(
            './/a[contains(@href,"magnet:")]/@href').extract_first()
        # ftp链接
        movie["ftp_link"] = info.xpath(
            './/a[contains(@href,"ftp://")]/@href').extract_first()

        texts = info.xpath('.//text()[normalize-space()]').extract()
        self.logger.debug(texts)
        texts = [s.replace('\u3000', '') for s in texts]

        key_texts = [s.strip().replace('◎', '') for s in texts if "◎" in s]

        patterns = {
            "translation": {
                "start": "译名",
                "div": "/"
            },
            "title": {
                "start": "片名",
                "div": "/"
            },
            "age": {
                "start": "年代",
            },
            "origin": {
                "start": "产地|国家",
                "div": "/"
            },
            "category": {
                "start": "类别",
                "div": "/"
            },
            "lang": {
                "start": "语言",
                "div": "/"
            },
            "subtitles": {
                "start": "字幕",
                "div": "/"
            },
            "premiere": {
                "start": "上映日期"
            },
            "imdb_rate": {
                "start": "IMDb评分"
            },
            "douban_rate": {
                "start": "豆瓣评分"
            },
            "file_format": {
                "start": "文件格式"
            },
            "chicun": {
                "start": "视频尺寸"
            },
            "length": {
                "start": "片长"
            },
            "director": {
                "start": "导演",
                "div": "/"
            },
            "actors": {
                "start": "主演",
                "div": "/"
            },
            "tags": {
                "start": "类别",
                "div": "|"
            },
        }
        for (k, v) in patterns.items():
            for s in key_texts:
                m = re.match(r"^({})(.*)".format(v["start"]), s)
                if m:
                    movie[k] = m.groups()[1]
                    if "div" in v:
                        movie[k] = [m.strip() for m in movie[k].split("/")]
                    break

        # 没有特殊标记的纯文本
        pure_texts = {s.strip() for s in texts if ("◎" not in s and s.strip())}

        # 获奖的文本
        prize_names = [
            "百想艺术大赏",
            "青龙奖",
            "电影大奖",
            "技术奖",
            "金狮奖",
            "电影节",
            "金马",
            "金鹿奖",
            "长春电影节",
            "电影奖",
            "主竞赛单元",
            "最佳",
        ]
        # 奖项的文本作为集合
        prize_texts = {
            s
            for s in pure_texts if re.search("|".join(prize_names), s)
        }

        # 获奖
        movie["prize"] = list(prize_texts)

        # 集合差集计算剩余的演员
        for s in pure_texts.difference(prize_texts):
            if len(s) < 50 and (not re.search("改编自|最佳", s)):
                movie["actors"].append(s)

        # 集合差集计算简介
        movie["introduction"] = "\n".join([
            s.strip() for s in set.difference(pure_texts, prize_texts,
                                              set(movie["actors"]))
        ])

        print(json.dumps(dict(movie), indent=4, ensure_ascii=False))

        yield movie
