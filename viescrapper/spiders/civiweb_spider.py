# coding: utf8

import re
import scrapy  # $ pip install scrapy
import locale

from datetime import datetime
from viescrapper.items import VieItem


class CiviwebSpider(scrapy.Spider):
    """
    Spider dedicated on scrapping French International Volunteers in Business (in French : VIE) offers website.

    The strategy for this scrapper is :
    - Extract each civiweb job offer URL
    - Request each URL and callback a parse function that does scrap data we need into our item
    """
    name = "Civiweb"
    allowed_domains = ["www.civiweb.com"]
    start_urls = ["https://www.civiweb.com/FR/offre-liste.aspx"]
    cpt = 0

    def __init__(self):
        locale.setlocale(locale.LC_TIME, '')

    def parse(self, response):
        """
        Go through the civiweb job offer list pages, extract and request on each job offer URL. Once all job offer
        URL have been extracted, look for the next list page
        """
        offers = response.xpath('//*[@id="content2"]/div[1]/section/section/article')

        for offer in offers:
            yield scrapy.Request(response.urljoin(offer.xpath('h1/a/@href').extract()[0]), self.parse_post)

        # Got to the next page once the current page has been scrapped
        current_page = int(response.xpath('//*[@id="content2"]/div[1]/section/section/div/span[@class="actif"]/text()').extract()[0])
        all_page_url = response.xpath('//*[@id="content2"]/div[1]/section/section/div/span')  # Get all pages url
        for sel in all_page_url :
            page_number = sel.xpath('a/text()').extract()
            # Avoid empty selectors (<span> for civiweb next_page could be empty)
            if page_number:
                # Find next page from current one
                if int(page_number[0]) == current_page+1:
                    # Get the url next page
                    next_page = sel.xpath('a/@href').extract()[0]
                    if next_page is not None :
                        scrapy.log('Request on next page {0}'.format(next_page))
                        next_page = response.urljoin(next_page)
                        yield scrapy.Request(next_page, callback=self.parse)
                    break

    def parse_post(self, response):
        """
        This method is called on each response from job offer url request. It does scrape data we need into item.
        """
        vie_item = VieItem()

        vie_item['id_civiweb'] = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oVIM"]/text()').extract()[0]
        vie_item['job_title'] = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oTitle"]/text()').extract()[0]
        vie_item['country'] = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oContry"]/text()').extract()[0]
        vie_item['city'] = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oCity"]/text()').extract()[0]
        vie_item['company'] = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oOrganization"]/text()').extract()[0]
        vie_item['degrees'] = [degree.strip() for degree in response.xpath('//*[@id="ContenuPrincipal_BlocB1_m_oEducationLevel"]/text()').extract()[0].split(',')]
        vie_item['languages'] = [language.strip() for language in response.xpath('//*[@id="ContenuPrincipal_BlocB1_m_oLanguages"]/text()').extract()[0].split(',')]
        vie_item['experience_required'] = int(response.xpath('//*[@id="ContenuPrincipal_BlocB1_m_oDesiredExperience"]/text()').extract()[0])
        vie_item['skill_fields'] = [field.strip() for field in response.xpath('//*[@id="ContenuPrincipal_BlocB1_m_oCompetence"]/text()').extract()[0].split(',')]
        vie_item['description'] = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oDescription"]/text()').extract()[0]
        vie_item['duration'] = int(response.xpath('//*[@id="ContenuPrincipal_BlocB1_m_oDesiredExperience"]/text()').extract()[0])
        vie_item['url'] = response.url
        vie_item['scrapped_time'] = datetime.now().isoformat()

        salary_block = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oIndemnite"]/text()').extract()[0]
        vie_item['salary'] = int(re.match('^(\d+).*$', salary_block, re.M | re.I).group(1))

        start_time_scrapped = response.xpath('//*[@id="ContenuPrincipal_BlocA1_m_oStartDate"]/text()').extract()[0]
        vie_item['start_date'] = self._convert_date_scrapped_to_iso_date(start_time_scrapped)

        published_time_scrapped = response.xpath('//*[@id="ContenuPrincipal_BlocB1_m_oPublicationDate"]/text()').extract()[0]
        vie_item['published_date'] = self._convert_date_scrapped_to_iso_date(published_time_scrapped)

        yield vie_item

    def _convert_date_scrapped_to_iso_date(self, u_date_in_letter):
        """
        Convert a scrapped date into an iso formatted date (u'01 d\xe9cembre 2016' -> ' 2016-12-01')
        :param u_date_in_letter: a unicode full letter date (format : day_in_decimal month_as_full_name year_in_decimal)
        :return: a iso formatted date 'YYYY-MM-DD'
        """
        # Encode the date from unicode to a iso-8859-1 (Latin-1) string
        date_in_leter = u_date_in_letter.encode("iso-8859-1" )

        # Create a datetime object from the date in letter
        datetime_object = datetime.strptime(date_in_leter, '%d %B %Y')

        # Return an iso formatted date
        return datetime_object.date().isoformat().decode('utf-8')

'''
    def parse(self, response):
        """
        Here is an other way to scrap data from civiweb. This method is faster, because you do less web calls,
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