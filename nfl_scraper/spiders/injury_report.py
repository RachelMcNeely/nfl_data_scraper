import scrapy
import pandas as pd
import re
from sqlalchemy.orm import sessionmaker
from ..models import InjuryReport, db_connect
import numpy as np


class InjuriesSpider(scrapy.Spider):
    name = "injuries"

    def start_requests(self):
        year = int(getattr(self, 'year', 2020))

        if year != 2020:
            ## can pull injury report directly from nfl site 
            print('year is: ', year)
            urls = [
                'https://www.nfl.com/injuries/league/{}/REG1'.format(year)
            ]
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)
        else:
            ## need to pull injuries from team websites
            urls = [
                # 'https://www.baltimoreravens.com/team/injury-report/',
                'https://www.vikings.com/team/injury-report/'
            ]
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        print()
        print('CURRENT URL: ', response.url)
        print()

        if 'www.nfl.com/injuries/' in response.url:
            print('---------- LOADING FROM NFL SITE -----------')
            inital_team_html = response.css('td , .d3-o-section-sub-title').getall()[0]
            current_team = re.search(r'<span>(.*?)</span>', inital_team_html).group(1)

            values = {current_team: []}

            for i, match in enumerate(response.css('td , .d3-o-section-sub-title').getall()):
            # for i, match in enumerate(response.css('td').getall()):

                if re.search(r'<span>(.*?)</span>', match):
                    # found a team header - need to add new empty list of team to dictionary 
                    current_team = re.search(r'<span>(.*?)</span>', match).group(1)
                    values[current_team] = [] 
                else:
                    values[current_team].append(re.sub(r'<.*>', '', match).strip())

            combined_teams = []
            combined_players = []
            combined_injury_lst = []
            combined_participation = []


            for key in values.keys():
                combined_teams.append(np.repeat(key, len(values[key][::5])))
                combined_players.append(values[key][::5])
                combined_injury_lst.append(values[key][1::5])
                combined_participation.append(values[key][3::5])

            # players = values[::5]
            # positions = values[1::5]
            # injury_lst = values[2::5]
            # participation = values[3::5]

            print(len(combined_teams))
            print(len(combined_injury_lst))

            current_week = re.match('https://www.nfl.com/injuries/league/{}/(.*)'.format(self.year), response.url).groups()[0]
            week_key = self.year + current_week 

            ## TO DO:
            ##   - This xpath only looks for REG season weeks - need to add in pre and post season as well?

            # weeks = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "nfl-c-form__group", " " )) and (((count(preceding-sibling::*) + 1) = 2) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "d3-o-dropdown", " " ))]/option/@value').re(r'/'+self.year+'/REG(.*)')

            # site_url = 'https://www.nfl.com/injuries/league/{year}/REG{week}'

            # for week in weeks:
            #     yield scrapy.Request(site_url.format(year=self.year, week=week), callback=self.parse)

            # for i, player in enumerate(players):
            #     engine = db_connect()
            #     self.Session = sessionmaker(bind=engine)
            #     session = self.Session()
            #     injury = InjuryReport()

            #     injury_exists = session.query(InjuryReport).filter_by(week_key=week_key, player_key=players[i]).first()
            #     if injury_exists:
            #         print('Injury already exists for {0} during week {1}.'.format(players[i], week_key))
            #     else:
            #         print('Adding injury of player {0} during week {1}.'.format(players[i], week_key))
            #         # injury.team_key 
            #         injury.week_key = week_key
            #         injury.player_key = players[i]
            #         injury.position = positions[i]
            #         injury.injury_location = injury_lst[i]
            #         injury.participation = participation[i]

            #         try:
            #             session.add(injury)
            #             session.commit()
            #         except:
            #             session.rollback()
            #             raise
            #     session.close()
            
        else:
            print('------------ LOADING FROM TEAM WEBSITE -----------')
            team 

    
    # def league_injuries(self, response):
    #     print('MADE IT TO LEAGUE INJURIES!!!')
        


    

    
        # self.log('Saved file %s' % filename)