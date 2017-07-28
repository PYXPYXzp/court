from urllib.parse import urlparse

from scrapy import Spider, FormRequest, Item, Field


class TableItem(Item):
    title = Field()
    date = Field()
    name = Field()
    rows = Field()


class CourtSpider(Spider):

    name = 'court_spider'

    start_urls = [
        'https://www.courtserve.net/secure/signin.php'
    ]

    def parse(self, response):
        return [FormRequest.from_response(response,
                                          formdata={'username': 'fingers_247@hotmail.com',
                                                    'password': 'upwork12345'},
                                          callback=self.after_login)]

    def after_login(self, response):
        link_page = response.xpath('//*[@id="box1"]/ul[4]/li[3]/a/@href').extract_first()
        yield response.follow(link_page, self.general_parse)

    def general_parse(self, response):
        links = response.xpath('//*[@id="box2"]/table//tr//td//a/@href').extract()
        for link in links:
            yield response.follow(link, self.get_url_param)

    def get_url_param(self, response):
        url_param = response.xpath('//*[@id="box2"]/div/object/@data').extract_first()
        url = urlparse(response.url)
        url_no_param = url.scheme + "://" + url.netloc + url.path
        next_url = url_no_param + url_param
        yield response.follow(next_url, self.parse_table)

    def parse_table(self, response):
        table_item = TableItem()
        table_item['title'] = response.xpath('/html/body/div[1]/p[1]//span/text()').extract_first()
        table_item['name'] = response.xpath('/html/body/div[1]/p[2]//span/text()').extract_first()
        table_item['date'] = response.xpath('/html/body/div[1]/p[3]//span/text()').extract_first()
        table = response.xpath('/html/body/div/table//tr')
        items = []
        for item in table:
            time = item.xpath('./td[1]/p/span/text()').extract_first()
            case_details = item.xpath('./td[2]/p/span/text()').extract_first()
            if time and case_details:
                if time != '\xa0' and case_details != '\xa0':
                    items.append({'case_details': case_details, 'time': time})
        table_item['rows'] = items
        yield {
            'item': table_item
        }



