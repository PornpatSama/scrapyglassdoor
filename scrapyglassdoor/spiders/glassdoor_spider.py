import scrapy
from urllib.parse import urljoin
from scrapy.http import Request,FormRequest
import json
import re
import pandas as pd
import math
from scrapy.exceptions import CloseSpider
import csv

class MoorSpider(scrapy.Spider):
    name = 'Moor'
    allowed_domains = ['glassdoor.com']
    start_urls = ['https://www.glassdoor.com/profile/login_input.htm']
    page_number = 3
    items = []


    def parse(self,response):
        #### (1)
        token = response.css('body').re(r"gdToken\":\"(.*?)\",")[0]
        #### (2)
        yield FormRequest('https://www.glassdoor.com/profile/ajax/loginSecureAjax.htm', formdata={'username':'likej41679@94jo.com','password':'1a2b3c4d','gdToken':token}, callback=self.startscraper)
    
    #industry 200001 - 200048
    #sgoc(job function: art/design, consulting)1001-1023
    
    def startscraper(self,response):
        sgoc_start_id = 1001
        sgoc_end_id = 1023
        industry_start_id = 200001
        industry_end_id = 200048

        for sgoc in range(sgoc_start_id,1003):
            for industry in range(industry_start_id,200003):
                yield Request("https://www.glassdoor.com/Explore/browse-companies.htm?overall_rating_low=0&page=1&sgoc={sgoc}&industry={industry}".format(sgoc = sgoc, industry = industry), callback=self.startscraper2)
    
# LIMIT 999 Pages
# = partitioning -> start with a
# https://stackoverflow.com/questions/65383046/crawled-403-error-while-login-to-glassdoor-com-using-scrapy-in-python-need-so: 
# How come? -> '&isHiringSurge=0&locId=1282&locType=S&locName=North%20Carolina,%20US,%20US', https://www.glassdoor.com/Explore/browse-companies.htm
    

    def startscraper2(self,response):
        # same as previous function, not good. How to dot it?
        sgoc_start_id = 1001
        sgoc_end_id = 1023
        industry_start_id = 200001
        industry_end_id = 200048
        # if strong text > 10000, return that it won't work
        
        total_comp = response.xpath("//div[@class='d-none d-md-block py-xxl px-std']/span[@class='resultCount css-56kyx5']/span/strong[3]/text()").get()
        total_page = math.ceil(int(total_comp)/10)
        
        # Check module first
        if int(total_page > 999):
            raise CloseSpider('Process is terminated. Page limit for scraping is 999 pages')
        # range(1, total page + 1)
        for sgoc in range(1001,1002):
                for industry in range(200001,200002):
                    for page in range(1, 3):
                        yield Request("https://www.glassdoor.com/Explore/browse-companies.htm?overall_rating_low=0&page={page}&sgoc={sgoc}&industry={industry}".format(page = page, sgoc = sgoc, industry = industry), callback=self.startscraper3)

    def startscraper3(self,response):
        for comp_review_link in response.xpath("//div[@class='col-12 col-lg-4 mt-lg-0 mt-std d-flex justify-content-between justify-content-lg-end order-6 order-lg-1']/a[@data-test='cell-Salaries-url']/@href"):
            yield response.follow(comp_review_link.get(), callback=self.parse_comp_metric)
    

    def parse_comp_metric(self, response):

        # items is in wrong place tho, but for testing
        
        for metric in ['reviews', 'jobs', 'salaries', 'interviews', 'benefits', 'photos']:
            #HTML script is either one of these versions
            company_metric_v1 = response.xpath("//a[@class='eiCell cell {metric} ']/span[@class='num eiHeaderLink']/text()".format(metric = metric)).get()
            company_metric_v2 = response.xpath("//a[@class='eiCell cell {metric} active']/span[@class='num eiHeaderLink']/text()".format(metric = metric)).get()
            company_metric_v3 = response.xpath("//a[@datatest='ei-nav-{metric}-link']/div[@data-test='ei-nav-{metric}-count']/text()".format(metric = metric)).get()
            

            if(company_metric_v1) is not None:
                company_metric = company_metric_v1
            elif(company_metric_v2) is not None:
                company_metric = company_metric_v2
            else:
                company_metric = company_metric_v3
            
            # Variable with string format?? 
            # if(metric=='{metric'.format(metric=metric):
            #   company_{metric}.format(metric=metric) = company metric
            if(metric=='reviews'):
                company_reviews = company_metric
            if(metric=='jobs'):
                company_jobs = company_metric
            if(metric=='salaries'):
                company_salaries = company_metric
            if(metric=='interviews'):
                company_interviews = company_metric
            if(metric=='benefits'):
                company_benefits = company_metric
            if(metric=='photos'):
                company_photos = company_metric

        company_name = response.xpath("//div[@class='header cell info']/p[@class='h1 strong tightAll']/span[@class='d-inline-flex align-items-center']/text()").get()

        yield{
            'comp_url': response.url,
            'comp_name': company_name,
            'reviews': company_reviews, 
            'jobs': company_jobs, 
            'salaries': company_salaries, 
            'interviews': company_interviews,
            'benefits': company_benefits, 
            'photos': company_photos
        }
    
        
        
        

        # print(next_page)
        #for url in urls:
           # url1 = urljoin('https://www.glassdoor.com/', url)
           # yield url1
            #Request(url1, callback=self.DetailPage)
    
