from _ast import Yield

import scrapy
import csv
from selenium import webdriver
import time
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.exceptions import CloseSpider
import re




class Home_page(scrapy.Spider):
    name = 'Round1'

    def start_requests(self):
        path = "chromedriver.exe"
        self.driver = webdriver.Chrome(path)
        self.driver.get("https://www.bukalapak.com/")
        time.sleep(2)
        sel = Selector(text=self.driver.page_source)
        all_cat = sel.xpath('//ul[@class = "bl-list"]/li//@href').extract()
        Main_category = 'handphone'
        for cat in all_cat:
            url = 'https://www.bukalapak.com' + cat
            if re.search(Main_category, url):
                yield Request(url, callback=self.parse_book)
        else:
            yield {
                        'Message': 'This category not Present'
                    }

    def parse_book(self, response):
        if response.status != 200:
            raise CloseSpider('Error: Status Code Wrong!')
        else:
            sub_cats = response.xpath('//ul[@class = "bl-list"]/li//@href').extract()
            #print(sub_cats)
            Sub_category = 'hp-smartphone'
            for sub_cat in sub_cats:
                if re.search(Sub_category, sub_cat):
                    yield response.follow(sub_cat, callback=self.parsesubcat)
            else:
                yield response.follow(sub_cat, callback=self.parsesubcat)

    def parsesubcat(self, response):
        if response.status != 200:
            raise CloseSpider('Error: Status Code Wrong!')
        else:
            Keyword = 'samsung'
            key_word = 'https://www.bukalapak.com/products?search%5Bkeywords%5D=' + Keyword
            yield response.follow(key_word,callback=self.parse_data)
            #print(response.url)

    def parse_data(self,response):
        if response.status != 200:
            raise CloseSpider('Error: Status Code Wrong!')
        else:
            #writer = csv.writer(open('product_details.csv','w'))

            #writer1 = csv.writer(open('product.csv', 'w'))
            #writer.writerow(['Product_name', 'Product_Price','Product_URL', 'Brand', 'Location','Product_Rating'])

            data_array = response.xpath('//div[@class = "bl-flex-item mb-8"]')

            for data in data_array:
                Product_url = data.css('div[class*="thumbnail"] a::attr(href)').get()
                Product_name = data.css('div[class*="description-name"] a::text').get()
                Product_price = data.css('div[class*="description-price"] p::text').get()
                Product_location = data.css('div[class*="description-store"] span::text').get()
                Product_Rating = data.css('div[class*="description-rating"] a::text').get()

                #writer.writerow([Product_url]) # To create Input file for round 2
                #writer.writerow([Product_name, Product_price, Product_url, 'Samsung', Product_location, Product_Rating])

                #Currently using Yield function to out the data, file wiriting part is commented
                yield{
                    'Product_name': str(Product_name).strip(),
                    'Product_price': str(Product_price).strip(),
                    'Product_URL':Product_url,
                    'Brand':'Samsung',
                    'Location':str(Product_location).strip(),
                    'Product_Rating':str(Product_Rating).strip()
            }

            Next_pages = response.css('ul[class="bl-pagination__list"] a::attr(href)').getall()
            for Next_page in Next_pages:
                if Next_page:
                    yield response.follow(Next_page,callback=self.parse_data)
                else:
                      pass

