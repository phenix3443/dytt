# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VideoItem(scrapy.Item):
    """视频条目"""
    poster = scrapy.Field()
    screen = scrapy.Field()
    magnet_link = scrapy.Field()
    ftp_link = scrapy.Field()
    translation = scrapy.Field()
    title = scrapy.Field()
    age = scrapy.Field()
    origin = scrapy.Field()
    category = scrapy.Field()
    lang = scrapy.Field()
    subtitles = scrapy.Field()
    premiere = scrapy.Field()
    imdb_rate = scrapy.Field()
    douban_rate = scrapy.Field()
    file_format = scrapy.Field()
    chicun = scrapy.Field()
    length = scrapy.Field()
    director = scrapy.Field()
    actors = scrapy.Field()
    tags = scrapy.Field()
    introduction = scrapy.Field()
    prize = scrapy.Field()
