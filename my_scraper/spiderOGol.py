import os
import json
import scrapy

class OGolSpider(scrapy.Spider):
    
    name = 'oGol'
    start_urls = ['https://www.ogol.com.br/proximos_jogos.php']

    def parse(self, response):
        
        # Get the data
        teamsHome = response.xpath('//tr//td[re:test(@class, "text home")]//div//a[re:test(@href, "equipa.php?")]/text()').getall()
        teamsAway = response.xpath('//tr//td[re:test(@class, "text away")]//div//a[re:test(@href, "equipa.php?")]/text()').getall()
        editions = response.xpath('//tr//td[re:test(@class, "edition")]//div//a[re:test(@href, "edition.php?")]/text()').getall()
        gamesUrls = response.xpath('//tr//td//a[re:test(@href, "match_live.php?")]/@href').getall() + response.xpath('//tr//td[re:test(@class, "vs")]//a[re:test(@href, "jogo.php?")]/@href').getall()
        dates = response.xpath('//tr//td[re:test(@class, "date")]/text()').getall()
        datesPhasesAndHours = response.xpath('//tr//td/text()').getall()
        hours = [datesPhasesAndHours[i] for i in range(1, len(datesPhasesAndHours), 3)]
        #hours = [response.xpath('//tr//td/text()').getall()[i] for i in range(1, len(response.xpath('//tr//td/text()').getall()), 3)]

        # Formatting data
        gamesUrls = [url.replace('/', '') for url in gamesUrls]
        hours = [hour.replace(':', 'h') for hour in hours]
        dates = [date.replace('-', '/') for date in dates]
        
        data = []
        
        for home, away, hour, date, edition, url in zip(teamsHome, teamsAway, hours, dates, editions, gamesUrls):
            
            data.append({
                "home": home,
                "away": away,
                "edition": edition,
                "date": date,
                "time": hour,
                "url": "https://www.ogol.com.br/{}".format(url)
            })
        
        # Save the data to a json file
        path = r'{}\spiderOGol.json'.format(os.getcwd())
        with open(path, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False)
        print("The json file has been saved. See him at " + path)

        pass

