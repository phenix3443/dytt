# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VideoItem(scrapy.Item):
    """视频条目"""
    poster = scrapy.Field(cn="海报")
    screen = scrapy.Field(cn="截屏")
    magnet_link = scrapy.Field(cn="磁链")
    ftp_link = scrapy.Field(cn="ftp链接")
    translation = scrapy.Field(cn="译名")
    title = scrapy.Field(cn="片名")
    age = scrapy.Field(cn="年代")
    origin = scrapy.Field(cn="产地")
    category = scrapy.Field(cn="类别")
    lang = scrapy.Field(cn="语言")
    subtitles = scrapy.Field(cn="字幕")
    premiere = scrapy.Field(cn="上映日期")
    imdb_rate = scrapy.Field(cn="IMDb评分")
    douban_rate = scrapy.Field(cn="豆瓣评分")
    file_format = scrapy.Field(cn="文件格式")
    chicun = scrapy.Field(cn="视频尺寸")
    length = scrapy.Field(cn="片长")
    director = scrapy.Field(cn="导演")
    actors = scrapy.Field(cn="主演")
    tags = scrapy.Field(cn="标签")
    introduction = scrapy.Field(cn="简介")
    prize = scrapy.Field(
        cn="获奖",
        names=[
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
        ])
