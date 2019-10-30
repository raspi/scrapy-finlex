# -*- coding: utf-8 -*-
import scrapy
import os
import sys
import pathlib
from lxml import etree, html
from urllib.parse import urlsplit, urlencode, urljoin
from urllib.parse import parse_qsl as queryparse
from xml.dom import minidom


# Spider for downloading all current laws
class AjantasaSpider(scrapy.Spider):
    name = 'ajantasa'
    allowed_domains = ['finlex.fi', 'www.finlex.fi']
    start_urls = ['https://www.finlex.fi/fi/laki/ajantasa/']

    def parse(self, response):
        for yearlink in response.xpath("//div[@class='year-toc-container']//ul//li/a/@href"):
            yield scrapy.Request(response.urljoin(yearlink.extract()), callback=self.get_year)

    def get_year(self, response):
        for link in response.xpath("//dl[@class='docList']/dt[@class='doc']/a/@href").extract():
            yield scrapy.Request(response.urljoin(link), callback=self.getlaw)

    def getlaw(self, response):
        upath = urlsplit(response.url).path.lstrip("/").split("/")
        number = upath[-1]
        year = upath[-2]
        ltype = upath[-3]

        dirname = os.path.join("_law", ltype, year)

        pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)

        rawhtml = response.css("div#main-content").extract_first()
        # phtml = minidom.parseString(rawhtml).toprettyxml()

        phtml = etree.tostring(html.fromstring(rawhtml), encoding='unicode', pretty_print=True)

        # Save
        with open(os.path.join(dirname, number + ".html"), "w", encoding="utf8") as f:
            f.write(phtml)
