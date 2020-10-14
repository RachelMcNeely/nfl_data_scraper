import scrapy
import pandas as pd
import re
from sqlalchemy.orm import sessionmaker
from ..models import Injuries, db_connect


class InjuriesSpider(scrapy.Spider):
    name = "injuries"

    def start_requests(self):
        year = getattr(self, 'year', 2020)

        urls = [
            'https://www.nfl.com/injuries/league/{}/REG1'.format(year)
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        values = []
        for i, match in enumerate(response.css('td').getall()):
            try:
                value = re.sub(r'<.*>', '', match).strip()
                values.append(value)
            except:
                continue

        players = values[::5]
        positions = values[1::5]
        injury_lst = values[2::5]
        participation = values[3::5]

        # try:
        
        
        # # prev_year_str = response.css('.d3-o-dropdown option')[1].get()
        # next_week_str = response.css('.nfl-c-form__group:nth-child(2) .d3-o-dropdown option')[1].get()
        # # print('PREVIOUS YR STR: ', prev_year_str)
        # print('NEXT WEEK STR: ', next_week_str)
        # # prev_year = re.match('<option value="(.*)">', prev_year_str).groups()[0]
        # next_week = re.match('<option value="(.*)"', next_week_str).groups()[0]
        # print('** NEXT WEEK: ', next_week)
        # # print('** PREVIOUS YEAR: ', prev_year)

        # # if prev_year is not None:
        # #     yield response.follow(prev_year, callback=self.parse)

        print()
        print('CURRENT URL: ', response.url)
        print()

        current_year = re.match('https://www.nfl.com/injuries/league/(.*)/', response.url).groups()[0]
        current_week = re.match('https://www.nfl.com/injuries/league/{}/(.*)'.format(current_year), response.url).groups()[0]
        week_key = current_year + current_week 

        weeks = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "nfl-c-form__group", " " )) and (((count(preceding-sibling::*) + 1) = 2) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "d3-o-dropdown", " " ))]/option/@value').re(r'/2020/REG(.*)')

        print(weeks)

        site_url = 'https://www.nfl.com/injuries/league/2020/REG{week}'
        for week in weeks:
            yield scrapy.Request(site_url.format(week=week), callback=self.parse)

        # except:
        #     print('Failed.')

        for i, player in enumerate(players):
            engine = db_connect()
            self.Session = sessionmaker(bind=engine)
            session = self.Session()
            injury = Injuries()

            injury_exists = session.query(Injuries).filter_by(week_key=week_key, player_key=players[i]).first()
            if injury_exists:
                print('Injury already exists for {0} during week {1}.'.format(players[i], week_key))
            else:
                print('Adding injury of player {0} during week {1}.'.format(players[i], week_key))
                injury.week_key = week_key
                injury.player_key = players[i]
                injury.position = positions[i]
                injury.injury_location = injury_lst[i]
                injury.participation = participation[i]

                try:
                    session.add(injury)
                    session.commit()
                except:
                    session.rollback()
                    raise
            session.close()


        
        # self.log('Saved file %s' % filename)