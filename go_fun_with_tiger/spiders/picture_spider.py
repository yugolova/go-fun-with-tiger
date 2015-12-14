import scrapy
import logging

from calendar import monthrange
from go_fun_with_tiger.items import OneDayPictureItem

log = logging.getLogger(__name__)

EARLIEST_YEAR = 1985
OUT_OF_RANGE_ERROR = "requested date is out of range"

#adding super mega awesome comment
#and this!!!!



#and this!!

class DayByDayPictureSpider(scrapy.Spider):
    name = "calvin_and_hobbes_pics"

    def __init__(self, year=None, month=None, _all=None):
        super(DayByDayPictureSpider, self).__init__()

        self.allowed_domains = ["gocomics.com"]
        self.start_urls = ["http://www.gocomics.com/calvinandhobbes"]
        self.base_url = self.start_urls[0].split('/')

        self.asked_year = int(year) if year else False
        self.asked_month = int(month) if month else False
        self._all = _all


    def parse(self, response):
        url_for_current_date = (response.xpath("""//meta[@property='og:url']
                                                        /@content""").extract()[0])

        year, month, day = [int(x) for x in url_for_current_date.split('/')[4:]]

        if self.asked_year:
            if ((self.asked_year > year or self.asked_year < EARLIEST_YEAR)
                or (self.asked_month not in range(1,13) and self.asked_month)):
                log.error(OUT_OF_RANGE_ERROR)
                return
            elif self.asked_year == EARLIEST_YEAR and self.asked_month in range(1,11):
                log.error(OUT_OF_RANGE_ERROR)
                return
            elif year == self.asked_year and self.asked_month:
                if self.asked_month > month:
                    log.error(OUT_OF_RANGE_ERROR)
                    return


        if self._all:
            urls = self.urls_for_whole_time(year, month, day)
        elif self.asked_year and not self.asked_month:
            urls = self.urls_for_whole_year(year, month, day)
        elif self.asked_year and self.asked_month:
            urls = self.urls_for_whole_month(year, month, day)

        for url in urls:
            request = scrapy.Request(url, callback=self.parse_calendar_page)

            yield request


    def parse_calendar_page(self, response):
        item = OneDayPictureItem()
        image_info_str = response.xpath("""//a/img[contains(
                                            @alt,"Calvin and Hobbes") and
                                            contains(@class, "strip")]""")

        item['image_urls'] = image_info_str.xpath('@src').extract()

        yield item



    def get_month_list(self, year, month, day_range):
        urls = []
        for _day in day_range:
            url = self.base_url[:]
            url.extend([year, month, str(_day)])
            urls.append("/".join(url))

        return urls


    def get_urls_for_earliest_year(self):
        urls = []

        #last november days till 1985 12
        day_range = range(18, monthrange(EARLIEST_YEAR, 11)[1] + 1)
        month_list = self.get_month_list(str(1985), str(11), day_range)
        urls.extend(month_list)

        #last month till 1986
        day_range = range(1, monthrange(EARLIEST_YEAR, 12)[1] + 1)
        month_list = self.get_month_list(str(1985), str(12), day_range)

        urls.extend(month_list)

        return urls


    def urls_for_whole_year(self, year, month, day):
        if self.asked_year == EARLIEST_YEAR:
            urls = self.get_urls_for_earliest_year()

            return urls

        urls = []
        last_month = month if self.asked_year == year else 12

        for _month in range(1, last_month + 1):
            if self.asked_year == year and self.asked_month ==_month:
                last_day = day
            else:
                last_day = monthrange(self.asked_year, _month)[1]

            month_list = self.get_month_list(str(self.asked_year), str(_month),
                                                range(1, last_day + 1))
            urls.extend(month_list)

        return urls


    def urls_for_whole_month(self, year, month, day):
        urls = []
        first_day = 1

        if self.asked_year == year and self.asked_month == month:
            last_day = day
        elif self.asked_year == EARLIEST_YEAR and self.asked_month == 11:
            last_day = monthrange(EARLIEST_YEAR, 11)[1]
            first_day = 18
        else:
            last_day = monthrange(self.asked_year, self.asked_month)[1]

        month_list = self.get_month_list(str(self.asked_year), str(self.asked_month),
                                            range(first_day, last_day + 1))
        urls.extend(month_list)

        return urls


    def urls_for_whole_time(self, year, month, day):
        urls = []
        urls.extend(self.get_urls_for_earliest_year())

        #1986 till current year-1
        for _year in range(1986, year):
            for _month in range(1, 13):
                day_range = range(1, monthrange(_year, _month)[1] +1)
                month_list = self.get_month_list(str(_year), str(_month),
                                                    day_range)
                urls.extend(month_list)

        #current year,  jan till current month
        for _month in range(1, month):
            day_range = range(1, monthrange(year, _month)[1] +1)
            month_list = self.get_month_list(str(year), str(_month), day_range)
            urls.extend(month_list)

        #days of current month
        day_range = range(1, day + 1)
        month_list = self.get_month_list(str(year), str(month), day_range)
        urls.extend(month_list)

        return urls

