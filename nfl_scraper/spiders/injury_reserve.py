import scrapy
import pandas as pd
import re
from sqlalchemy.orm import sessionmaker
from ..models import InjuryReserve, db_connect
import datetime


class ReserveSpider(scrapy.Spider):
    name = "injury_reserve"

    def start_requests(self):
        year = getattr(self, 'year', 2020)

        urls = [
            'https://www.nfl.com/transactions/league/reserve-list/{}/9'.format(year)  # 6
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        values = []
        players = []
        for i, match in enumerate(response.css('td').getall()):
            try:
                if re.sub(r'<.*>', '', match).strip().split('\n')[0] != "":
                    value = re.sub(r'<.*>', '', match).strip().split('\n')[0]
                else:
                    # Value is a player
                    value = match.split('\n')[1].split('>')[1].split('<')[0]
                values.append(value)
            except:
                continue
        

        teams = values[0::6]
        dates = values[2::6]
        players = values[3::6]
        positions = values[4::6]
        transactions = values[5::6]

        current_month = re.match('https://www.nfl.com/transactions/league/reserve-list/{}/(.*)'.format(self.year), response.url).groups()[0]
        print('CURRENT WEEK: ', current_month )

        site_url = 'https://www.nfl.com/transactions/league/reserve-list/{year}/{month}'
        
        if response.css('div.nfl-o-table-pagination__buttons a::attr(href)').get():
            next_page_url = response.css('div.nfl-o-table-pagination__buttons a::attr(href)').get().split('/')
            print('FOUND NEXT PAGE!')

            yield scrapy.Request(site_url.format(year=self.year, month=next_page_url[5]), callback=self.parse)
        else:
            months = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "nfl-c-form__group", " " )) and (((count(preceding-sibling::*) + 1) = 2) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "d3-o-dropdown", " " ))]/option/@value').re(r'/'+self.year+'/(.*)')
            for month in months:
                yield scrapy.Request(site_url.format(year=self.year, month=month), callback=self.parse)



        for i, player in enumerate(players):
            engine = db_connect()
            self.Session = sessionmaker(bind=engine)
            session = self.Session()
            reserve = InjuryReserve()

            date_str = dates[i] + '/' + self.year

            ir_exists = session.query(InjuryReserve).filter_by(team=teams[i], year=self.year, month=current_month[0],
                player_key=players[i]).first()
            if ir_exists:
                print('Transaction on injury reserve already exists for {0} in month {1}/{2}.'.format(players[i], current_month[0], self.year))
            else:
                print('Adding injury reserve transaction of player {0} in month {1}/{2}.'.format(players[i], current_month[0], self.year))
                reserve.team = teams[i]
                reserve.year = self.year
                reserve.month = current_month[0]
                reserve.player_key = players[i]
                
                date_str = dates[i] + '/' + self.year
                reserve_date = datetime.datetime.strptime(date_str.replace('/',''), "%m%d%Y").date()

                reserve.date =  reserve_date  # datetime.datetime.strptime('24052010', "%d%m%Y").date()
                reserve.injury_key = teams[i].replace(' ', '') + str(reserve_date) + players[i].replace(' ', '') + 'RES'
                reserve.position = positions[i]
                reserve.transaction = transactions[i]

                try:
                    session.add(reserve)
                    session.commit()
                except:
                    session.rollback()
                    raise
            session.close()