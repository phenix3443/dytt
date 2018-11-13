# -*- coding: utf-8 -*-
import scrapy
import json
import re


class DyttSpider(scrapy.Spider):
    name = 'dytt'
    allowed_domains = ['www.dytt8.net', 'www.ygdy8.net']

    start_urls = ['http://www.dytt8.net/']

    def parse(self, response):
        """分析首页"""
        # 最新电影
        latest_moive_link = response.xpath(
            '//*[@id="menu"]/div/ul/li[1]/a/@href').extract_first()
        yield response.follow(
            latest_moive_link, callback=self.parse_latest_movie)

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

    def parse_moive_detail(self, response):
        """抓取电影详细信息"""
        movie = dict()
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
        m = {
            "译名": "translation",
            "片名": "title",
            "年代": "age",
            "产地": "origin_area",
            "类别": "category",
            "语言": "lang",
            "字幕": "subtitles",
            "上映日期": "premiere",
            "IMDb评分": "imdb_rate",
            "豆瓣评分": "douban_rate",
            "文件格式": "file_format",
            "视频尺寸": "chicun",
            "片长": "length",
            "导演": "director",
            "主演": "actors",
            "标签": "tags",
        }
        for (k, v) in m.items():
            for s in key_texts:
                if s.startswith(k):
                    movie[v] = s[len(k):]
                    break

        movie["translation"] = [
            s.strip() for s in movie["translation"].split("/")
        ]
        movie["title"] = [s.strip() for s in movie["title"].split("/")]
        movie["origin_area"] = [
            s.strip() for s in movie["origin_area"].split("/")
        ]
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
            for s in pure_texts if re.search(
                r"百想艺术大赏|青龙奖|电影大奖|技术奖|金狮奖|电影节|金马|金鹿奖|长春电影节|电影奖|主竞赛单元|最佳", s)
        }
        # 剩余的演员
        for s in pure_texts.difference(prize_texts):
            if len(s) < 50 and (not re.search("改编自|最佳", s)):
                movie["actors"].append(s)

        # 简介
        movie["Introduction"] = "\n".join([
            s.strip() for s in set.difference(pure_texts, prize_texts,
                                              set(movie["actors"]))
        ])
        # 获奖
        movie["prize"] = list(prize_texts)

        print(json.dumps(movie, indent=4, ensure_ascii=False))
