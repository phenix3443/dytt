# -*- coding: utf-8 -*-
import json
import re
import scrapy
import logging

from scrapy_video.items import VideoItem

logger = logging.getLogger(__name__)

class DyttSpider(scrapy.Spider):
    """电影天堂爬虫"""
    name = 'dytt'
    allowed_domains = ['www.dytt8.net', 'www.ygdy8.net']

    start_urls = ['https://www.dytt8.net/html/gndy/dyzz/20181108/57761.html']

    # def parse(self, response):
    #     """分析首页"""
    #     # 最新电影
    #     latest_moive_link = response.xpath(
    #         '//*[@id="menu"]/div/ul/li[1]/a/@href').extract_first()
    #     yield response.follow(
    #         latest_moive_link, callback=self.parse_latest_movie)

    def parse_latest_movie(self, response):
        """抓取最新电影列表"""
        # 最新电影列表
        movie_list = response.xpath('//div[@class="co_content8"]')
        detail_links = movie_list.xpath(
            './ul//a[@class="ulink"]/@href').extract()

        for dl in detail_links:
            yield response.follow(dl, callback=self.parse_moive_detail)

        # next_page = movie_list.xpath('./div//a/@href').extract_first()
        # yield response.follow(next_page, self.parse)

    # def parse_moive_detail(self, response):
    def parse(self, response):
        """抓取电影详细信息"""
        movie = VideoItem()
        info = response.xpath('//*[@id="Zoom"]')
        pictures = info.xpath('.//img/@src').extract()
        # 海报
        movie["poster"] = pictures[0]
        # 截屏
        movie["screen"] = pictures[1]

        movie["magnet_link"] = info.xpath(
            './/a[contains(@href,"magnet:")]/@href').extract_first()
        movie["ftp_link"] = info.xpath(
            './/a[contains(@href,"ftp://")]/@href').extract_first()

        texts = info.xpath(
            './/text()[normalize-space()] [contains(.,"\u3000")]').extract()
        texts = [s.replace('\u3000', '') for s in texts]
        key_texts = [s.strip().replace('◎', '') for s in texts if "◎" in s]

        for (k, v) in movie.fields.items():
            for s in key_texts:
                if s.startswith(v["cn"]):
                    movie[k] = s[len(v["cn"]):]
                    break

        movie["translation"] = [
            s.strip() for s in movie["translation"].split("/")
        ]
        movie["title"] = [s.strip() for s in movie["title"].split("/")]
        movie["origin"] = [s.strip() for s in movie["origin"].split("/")]
        movie["category"] = [s.strip() for s in movie["category"].split("/")]
        movie["lang"] = [s.strip() for s in movie["lang"].split("/")]
        movie["premiere"] = [s.strip() for s in movie["premiere"].split("/")]
        movie["tags"] = [s.strip() for s in movie["tags"].split("|")
                         ] if "tags" in movie else []
        movie["actors"] = [movie["actors"]]

        # 没有特殊标记的纯文本
        pure_texts = {s.strip() for s in texts if ("◎" not in s and s.strip())}
        # 获奖的文本
        prize_texts = {
            s
            for s in pure_texts
            if re.search("|".join(movie.fields["prize"]["names"]), s)
        }
        # 剩余的演员
        for s in pure_texts.difference(prize_texts):
            if len(s) < 50 and (not re.search("改编自|最佳", s)):
                movie["actors"].append(s)

        # 简介
        movie["introduction"] = "\n".join([
            s.strip() for s in set.difference(pure_texts, prize_texts,
                                              set(movie["actors"]))
        ])
        # 获奖
        movie["prize"] = list(prize_texts)

        print(json.dumps(dict(movie), indent=4, ensure_ascii=False))
