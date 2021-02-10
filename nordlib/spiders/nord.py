import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from nordlib.items import Article


class NordSpider(scrapy.Spider):
    name = 'nord'
    start_urls = ['https://www.nordlb.com/nordlb/press/archive/']

    def parse(self, response):
        links = response.xpath('//a[@class="toggle-next clickafterload"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="box-body-content news"]//h2/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="box-body-content news"]//text()').getall()
        content = [text for text in content if text.strip()]
        date = content.pop(0)
        if date:
            date = datetime.strptime(date.strip(), '%d.%m.%Y')
            date = date.strftime('%Y/%m/%d')
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
