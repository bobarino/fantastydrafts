import scrapy
from collections import defaultdict
from .. import items
from .. import psql
from scrapy.conf import settings

class ESPNSpider(scrapy.Spider):
    name = "espn"

    def start_requests(self):
        allowed_domains = ['espn.go.com', 'games.espn.go.com', 'games.espn.com']
        start_urls = ["http://games.espn.com/ffl/tools/projections"]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        playerrows = response.xpath('//tr[contains(@class, "pncPlayerRow")]')
        for player in playerrows:
            item = items.FantasyDataSpiderItem()
            item['ffl_source'] = self.name

            playerText = player.xpath('./td/text()').extract()

            playerText = [el.replace('--', '0') for el in playerText]

            pn = player.xpath('./td[@class="playertablePlayerName"]')[0]

            #Get playername, if defense then take off the D/ST from the name
            if "D/ST" not in pn.xpath('./a/text()')[0].extract():
                item['playername'] = pn.xpath('./a/text()')[0].extract()
            else:
                item['playername'] = pn.xpath('./a/text()')[0].extract()[:-4]

            tp = pn.xpath('text()').extract()[0].replace(', ', '')
            tps = [el for el in tp.split(u'\xa0') if el]
            try:
                [team, pos] = tps
            except ValueError:
                team = ''
                pos = tps[0]
            item['team'] = team
            if pos == "D/ST":
                item['pos'] = "DST"
            else:
                item['pos'] = pos

            if len(playerText) == 13:
                item['status_type'] = "n"
                item['passing_c'], item['passing_a'] = [
                    float(el) for el in playerText[2].split('/')
                ]
                item['passing_yds'] = float(playerText[3])
                item['passing_td'] = float(playerText[4])
                item['passing_int'] = float(playerText[5])
                item['rushing_r'] = float(playerText[6])
                item['rushing_yds'] = float(playerText[7])
                item['rushing_td'] = float(playerText[8])
                item['receiving_rec'] = float(playerText[9])
                item['receiving_yds'] = float(playerText[10])
                item['receiving_tot'] = float(playerText[11])
                item['pts_total'] = float(playerText[12].replace('--', '0'))

            else:
                item['status_type'] = "y"
                item['passing_c'], item['passing_a'] = [
                    float(el) for el in playerText[1].split('/')
                ]
                item['passing_yds'] = float(playerText[2])
                item['passing_td'] = float(playerText[3])
                item['passing_int'] = float(playerText[4])
                item['rushing_r'] = float(playerText[5])
                item['rushing_yds'] = float(playerText[6])
                item['rushing_td'] = float(playerText[7])
                item['receiving_rec'] = float(playerText[8])
                item['receiving_yds'] = float(playerText[9])
                item['receiving_tot'] = float(playerText[10])
                item['pts_total'] = float(playerText[11].replace('--', '0'))

            yield item

        nextLinks = response.xpath('//div[@class="paginationNav"]/a[text() = "NEXT"]')
        if nextLinks:
            url = nextLinks[0].xpath('@href')[0].extract()
            url = response.urljoin(url)
            yield scrapy.Request(url, self.parse)
