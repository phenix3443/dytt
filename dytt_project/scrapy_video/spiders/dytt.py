# -*- coding: utf-8 -*-
import json
import re
import scrapy

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
            "http://www.ygdy8.net/html/gndy/dyzz/20091004/22009.html",
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

        texts = info.xpath('.//text()[normalize-space(.)]').extract()

        # 去掉特殊符号
        token = ["\xa0", "\u3000"]
        for t in token:
            texts = [s.replace(t, '') for s in texts]

        texts = [s.strip() for s in texts]  # 去掉首尾空格
        texts = [s for s in texts if s]  # 去掉空字符串

        # 去掉特殊行
        texts = [s for s in texts if not re.match(".*(ftp://|下载地址|磁力链).*", s)]
        self.logger.debug(texts)

        patterns = {
            "translation": {
                "start": "◎译名",
                "div": "/"
            },
            "title": {
                "start": "◎片名",
                "div": "/"
            },
            "age": {
                "start": "◎年代",
            },
            "origin": {
                "start": "◎产地|◎国家",
                "div": "/"
            },
            "category": {
                "start": "◎类别",
                "div": "/"
            },
            "lang": {
                "start": "◎语言",
                "div": "/"
            },
            "subtitles": {
                "start": "◎字幕",
                "div": "/"
            },
            "premiere": {
                "start": "◎上映日期"
            },
            "imdb_rate": {
                "start": "◎IMDb评分"
            },
            "douban_rate": {
                "start": "◎豆瓣评分"
            },
            "file_format": {
                "start": "◎文件格式"
            },
            "chicun": {
                "start": "◎视频尺寸"
            },
            "length": {
                "start": "◎片长"
            },
            "director": {
                "start": "◎导演",
                "div": "/"
            },
            "actors": {
                "start": "◎主演",
                "div": "/",
            },
            "tags": {
                "start": "◎标签",
                "div": "|"
            },
            "introduction": {
                "start": "◎简介",
                "div": "/",
            },
            "prize": {
                "start": "◎获奖情况",
                "div": "/",
            }
        }
        # 标记各个字段的位置
        for (idx, s) in enumerate(texts):
            for (k, v) in patterns.items():
                m = re.match(r"^({})(.*)".format(v["start"]), s)
                if m:
                    v["idx"] = idx
                    break

        for (k, v) in patterns.items():
            if "idx" in v:
                m = re.match(r"^({})(.*)".format(v["start"]), texts[v["idx"]])
                movie[k] = m.groups()[1]
                if "div" in v:
                    movie[k] = [m.strip() for m in movie[k].split(v["div"])]

        # 演员字段
        start = patterns["actors"]["idx"] + 1
        for s in texts[start:]:
            if "◎" in s:
                break
            else:
                movie["actors"].append(s)

        # 简介字段
        start = patterns["introduction"]["idx"] + 1
        for s in texts[start:]:
            if "◎" in s:
                break
            else:
                movie["introduction"].append(s)

        ads = info.xpath('.//a/span/text()').extract()
        movie["introduction"] = list(
            set(movie["introduction"]).difference(ads))

        # 获奖情况
        if "idx" in patterns["prize"]:
            start = patterns["prize"]["idx"] + 1
            for s in texts[start:]:
                if "◎" in s:
                    break
                else:
                    movie["prize"].append(s)

        # 去掉特殊符号
        for k in ["introduction", "prize"]:
            if k in movie:
                movie[k] = [s for s in movie[k] if s]  # 去掉空字符串

        yield movie
