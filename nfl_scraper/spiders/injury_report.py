import scrapy
import pandas as pd
import re
from sqlalchemy.orm import sessionmaker
from ..models import InjuryReport, db_connect
import numpy as np
from bs4 import BeautifulSoup


class InjuriesSpider(scrapy.Spider):
    name = "injury_report"

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

            teams = []
            players = []
            positions = []
            injury_lst = []
            participation = []


            for key in values.keys():
                teams.extend(np.repeat(key, len(values[key][::5])))
                players.extend(values[key][::5])
                positions.extend(values[key][1::5])
                injury_lst.extend(values[key][2::5])
                participation.extend(values[key][3::5])

            current_week = re.match('https://www.nfl.com/injuries/league/{}/(.*)'.format(self.year), response.url).groups()[0]
            week_key = self.year + current_week 

            for i, player in enumerate(players):
            	
                engine = db_connect()
                self.Session = sessionmaker(bind=engine)
                session = self.Session()
                injury = InjuryReport()

                injury_exists = session.query(InjuryReport).filter_by(team_key=teams[i], week_key=week_key, player_key=players[i]).first()
                if injury_exists:
                    print('Injury already exists for {0} during week {1}.'.format(players[i], week_key))
                else:
                    print('Adding injury of player {0} during week {1}.'.format(players[i], week_key))
                    injury_key = teams[i].replace(' ', '') + week_key + players[i].replace(' ', '') + 'REP'

                    injury.injury_key = injury_key.upper()
                    injury.team_key = teams[i]
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

            ## TO DO:
            ##   - This xpath only looks for REG season weeks - need to add in pre and post season as well?
            # get all the weeks for current year and scrape those injuries
            site_url = 'https://www.nfl.com/injuries/league/{year}/REG{week}'
            weeks = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "nfl-c-form__group", " " )) and (((count(preceding-sibling::*) + 1) = 2) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "d3-o-dropdown", " " ))]/option/@value').re(r'/'+self.year+'/REG(.*)')
            for week in weeks:
                yield scrapy.Request(site_url.format(year=self.year, week=week), callback=self.parse)
            
        else:
            print('------------ LOADING FROM TEAM WEBSITE -----------')

            # values = [[], [], [], [], [], [], []]  #[[players], [psotiions], [injury_lst], [EMPTY], [EMPTY], [EMPTY], [participation]]
            players = []
            positions = []
            injury_lst = []
            participation = []

            print()

            # print(response.css('.d3-l-grid--inner:nth-child(1) table td').getall()[0:10])

            print()
            print()

            player_selector = '.nfl-o-injury-report__container:nth-child(3) .d3-o-media-object'
            for i, match in enumerate(response.css(player_selector).getall()):
            	soup = BeautifulSoup(match)
            	players.append(soup.span.a.text.strip())



            position_selector = '.nfl-o-injury-report__container:nth-child(3) td:nth-child(2)'
            for i, match in enumerate(response.css(position_selector).getall()):
                soup = BeautifulSoup(match)
                positions.append(soup.text.strip())

            injury_selector = '.nfl-o-injury-report__container:nth-child(3) td:nth-child(3)'
            for i, match in enumerate(response.css(injury_selector).getall()):
                soup = BeautifulSoup(match)
                injury_lst.append(soup.text.strip())

            participation_selector = '.nfl-o-injury-report__container:nth-child(3) td:nth-child(7)'
            for i, match in enumerate(response.css(participation_selector).getall()):
                soup = BeautifulSoup(match)
                participation.append(soup.text.strip())


            ## TO DO: 
            # 1. Need to pull team and current week out of url
            # 2. Need to save items in injury_report DB

            # ------------ STOPPED HERE --------------------------------------------- #

            # current_week = re.match('https://www.nfl.com/injuries/league/{}/(.*)'.format(self.year), response.url).groups()[0]
            # week_key = self.year + current_week 


    




