# coding: utf8

import os
import re
import scrapy

from viescrapper.items import VieItem


class CiviwebSpider(scrapy.Spider):
    name = "Civiweb"
    allowed_domains = ["www.civiweb.com"]
    start_urls = ["https://www.civiweb.com/FR/offre-liste.aspx"]

    def parse(self, response):
        for post in response.xpath('//*[@id="content2"]/div[1]/section/section/article') :
            print response.urljoin(post.xpath('h1/a/@href').extract()[0])
            yield scrapy.Request(response.urljoin(post.xpath('h1/a/@href').extract()[0]), self.parse_post)

        # Got to the next page once the current page has been scrapped
        current_page = int(response.xpath('//*[@id="content2"]/div[1]/section/section/div/span[@class="actif"]/text()').extract()[0])
        all_page_url = response.xpath('//*[@id="content2"]/div[1]/section/section/div/span')  # Get all pages url
        for sel in all_page_url :
            page_number = sel.xpath('a/text()').extract()
            if page_number:  # Avoid empty selectors (<span> for civiweb next_page could be empty)
                if int(page_number[0]) == current_page+1:  # Find next page from current one
                    next_page = sel.xpath('a/@href').extract()[0]  # Get the url next page
                    if next_page is not None :
                        print "Go to next page : " + next_page
                        next_page = response.urljoin(next_page)
                        yield scrapy.Request(next_page, callback=self.parse)
                    break

    def parse_post(self, response):
        vie_item = VieItem()

        vie_item['id_civiweb'] = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oVIM"]/text()').extract()[0]
        vie_item['name'] = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oTitle"]/text()').extract()[0]
        vie_item['country'] = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oContry"]/text()').extract()[0]
        vie_item['city'] = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oCity"]/text()').extract()[0]
        vie_item['company'] = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oOrganization"]/text()').extract()[0]

        # //*[@id="ContenuPrincipal_BlocA1_m_oIndemnite"]
        salary_block = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oIndemnite"]/text()').extract()[0]
        vie_item['salary'] = int(re.match('^(\d+).*$', salary_block, re.M | re.I).group(1))

        vie_item['description'] = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oDescription"]/text()').extract()[0]
        vie_item['duration'] = int(response.xpath('//*[@id="ContenuPrincipal_BlocB1_m_oDesiredExperience"]/text()').extract()[0])
        vie_item['url'] = response.url
        vie_item['start_time'] = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oStartDate"]/text()').extract()[0]
        vie_item['published_time'] = response.xpath('//*[@id="ContenuPrincipal_BlocB1_m_oPublicationDate"]/text()').extract()[0]
        yield vie_item


'''
def parse(self, response):
    """Here is an other way to scrap data from civiweb. This method is faster, because you do less web calls,
    but you scrap less data.
    The method involves to parse each VIE offer overview in the list page. Once you we all data from the current page,
    we move to the next page and repeat the method, and again until to reach the last page.

     Here is list of data scrapped by this method :
     - Job title
     - Job country
     - Duration
     - Company
     - Offer published date
     - Description overview
     - Job offer URL

     This method is called on each VIE offer list page.
    """
    for sel in response.xpath('//*[@id="content2"]/div[1]/section/section/article'):
        vie_item = VieItem()
        # Extract data from vie title
        # We get something like "DIRECTEUR / DIRECTRICE D'ALLIANCE FRANCAISE (MADAGASCAR12MOIS)"
        # that we need to parse into : "%s(%s%smois)" % (name, location, duration)
        vie_title = sel.xpath('h1/a/text()').extract()[0]
        vie_match_groups = re.match('^(.*)\(([^\d]*)(\d+)[^\d]*\)$', vie_title, re.M | re.I)
        vie_item['name'] = vie_match_groups.group(1).strip()
        vie_item['location'] = vie_match_groups.group(2).strip()
        vie_item['duration'] = int(vie_match_groups.group(3).strip())

        # Link url extracted only contains path and does not contain host
        path_civiweb = sel.xpath('h1/a/@href').extract()[0]
        vie_item['link'] = HOST_CIVIWEB + path_civiweb

        # Extract compagny : 'ETABLISSEMENT : RCI BANQUE' => 'ETABLISSEMENT : %s' % company
        vie_item['company'] = sel.xpath('(p[@class="location"])/text()').extract()[0][16:]

        # Extract published date : 'Publi\xe9 le 23/09/2016'
        vie_item['published_time'] = sel.xpath('time/text()').extract()[0][-10:]
        yield vie_item

    # Got to the next page once the current page has been scrapped
    current_page = int(response.xpath('//*[@id="content2"]/div[1]/section/section/div/span[@class="actif"]/text()').extract()[0])
    all_page_url = response.xpath('//*[@id="content2"]/div[1]/section/section/div/span')  # Get all pages url
    for sel in all_page_url :
        page_number = sel.xpath('a/text()').extract()
        if page_number:  # Avoid empty selectors (<span> for civiweb next_page could be empty)
            if int(page_number[0]) == current_page+1:  # Find next page from current one
                next_page = sel.xpath('a/@href').extract()[0]  # Get the url next page
                if next_page is not None :
                    #next_page = HOST_CIVIWEB + next_page
                    print "go to next page : " + next_page
                    next_page = response.urljoin(next_page)
                    yield scrapy.Request(next_page, callback=self.parse)
                break
'''