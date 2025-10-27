import csv
import datetime
import time

import requests
from xml.etree import ElementTree as ET


class SiteMap:
    FilesData = list()

    def __init__(self):
        pass

    def fetch_data(self, url):
        response = requests.request(
            method="GET",
            url=url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            })

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.text)

    def generate_site_map(self, url, name):  # get url of sitemap data api, and file name
        data = self.fetch_data(url)
        # check if there is pagination
        if type(data) is dict:
            data = data['results']

        root = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        last_update = None
        for item in data:
            doc = ET.SubElement(root, 'url')
            ET.SubElement(doc, 'loc').text = item['url']
            ET.SubElement(doc, 'priority').text = '0.8'
            date_object = datetime.datetime.fromisoformat(item['updated_at']).date()
            ET.SubElement(doc, 'lastmod').text = str(date_object)
            if not last_update:
                last_update = date_object
            if date_object > last_update:
                last_update = date_object

        tree = ET.ElementTree(root)
        tree.write(f'{name}.xml', encoding='UTF-8', xml_declaration=True)
        self.FilesData.append({
            'name': f'{name}.xml',
            'updated_at': str(last_update),
        })

    def generate_files_site_map(self, name, domain):
        root = ET.Element('sitemapindex', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        for filedata in self.FilesData:
            doc = ET.SubElement(root, 'sitemap')
            ET.SubElement(doc, 'loc').text = f'{domain}/{filedata['name']}'
            ET.SubElement(doc, 'lastmod').text = str(filedata['updated_at'])

        tree = ET.ElementTree(root)
        tree.write(f'{name}.xml', encoding='UTF-8', xml_declaration=True)


site_map = SiteMap()
site_map.generate_site_map('https://stageapi-teratech.vitechdev.ir/product/product/sitemap/?size=165', 'products_site_map')
site_map.generate_site_map('https://stageapi-teratech.vitechdev.ir/product/v2/category/sitemap/', 'categories_site_map')
time.sleep(1)
site_map.generate_files_site_map('site_map', 'https://teratech.shop')
