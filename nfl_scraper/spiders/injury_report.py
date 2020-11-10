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
				'https://www.baltimoreravens.com/team/injury-report/week/REG-1',
				'https://www.bengals.com/team/injury-report/week/REG-1',
				'https://www.clevelandbrowns.com/team/injury-report/week/REG-1',
				'https://www.steelers.com/team/injury-report/week/REG-1',
				'https://www.buffalobills.com/team/injury-report/week/REG-1',
				'https://www.miamidolphins.com/team/injury-report/week/REG-1',
				'https://www.patriots.com/team/injury-report/week/REG-1',
				'https://www.newyorkjets.com/team/injury-report/week/REG-1',
				'https://www.houstontexans.com/team/injury-report/week/REG-1',
				'https://www.colts.com/team/injury-report/week/REG-1',
				'https://www.jaguars.com/team/injury-report/week/REG-1',
				'https://www.tennesseetitans.com/team/injury-report/week/REG-1',
				'https://www.denverbroncos.com/team/injury-report/week/REG-1',
				'https://www.chiefs.com/team/injury-report/week/REG-1',
				'https://www.raiders.com/team/injury-report/week/REG-1',
				'https://www.chargers.com/team/injury-report/week/REG-1',
				'https://www.chicagobears.com/team/injury-report/week/REG-1',
				'https://www.detroitlions.com/team/injury-report/week/REG-1',
				'https://www.packers.com/team/injury-report/week/REG-1',
				'https://www.vikings.com/team/injury-report/week/REG-1',
				'https://www.dallascowboys.com/team/injury-report/week/REG-1',
				'https://www.giants.com/team/injury-report/week/REG-1',
				'https://www.philadelphiaeagles.com/team/injury-report/week/REG-1',
				'https://www.washingtonfootball.com/team/injury-report/week/REG-1',
				'https://www.atlantafalcons.com/team/injury-report/week/REG-1',
				'https://www.panthers.com/team/injury-report/week/REG-1',
				'https://www.neworleanssaints.com/team/injury-report/week/REG-1',
				'https://www.buccaneers.com/team/injury-report/week/REG-1',
				'https://www.azcardinals.com/team/injury-report/week/REG-1',
				'https://www.therams.com/team/injury-report/week/REG-1',
				'https://www.49ers.com/team/injury-report/week/REG-1',
				'https://www.seahawks.com/team/injury-report/week/REG-1'
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
					val = re.sub(r'<.*>', '', match).strip()
					if val == '':
						values[current_team].append(None)
					else:
						values[current_team].append(val)

			teams = []
			players = []
			positions = []
			injury_lst = []
			game_status = []


			for key in values.keys():
				teams.extend(np.repeat(key, len(values[key][::5])))
				players.extend(values[key][::5])
				positions.extend(values[key][1::5])
				injury_lst.extend(values[key][2::5])
				game_status.extend(values[key][4::5])


			current_week = re.match('https://www.nfl.com/injuries/league/{}/(.*)'.format(self.year), response.url).groups()[0]
			current_week_num = int(re.findall(r'\d+', current_week)[0])
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
					injury.year = self.year
					injury.week = current_week_num
					injury.team_key = teams[i]
					injury.week_key = week_key
					injury.player_key = players[i]
					injury.position = positions[i]
					injury.injury_location = injury_lst[i]
					injury.game_status = game_status[i]

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
			
			current_week = re.match('https://(.*)/team/injury-report/week/(.*)', response.url).group(0).split('/')[-1].replace('-', '')
			current_week_num = int(re.findall(r'\d+', current_week)[0])

			team_name = response.css('.nfl-o-injury-report__container:nth-child(3) .nfl-o-injury-report__club-name::text').get()

			if team_name != None: ## checking for when on some team websites only other team injuries are listed
				print('Found a team name! ', team_name)
				players = []
				positions = []
				injury_lst = []
				game_status = []

				player_selector = '.nfl-o-injury-report__container:nth-child(3) .d3-o-media-object'
				for i, match in enumerate(response.css(player_selector).getall()):
					soup = BeautifulSoup(match)
					try:
						players.append(soup.span.a.text.strip())
					except AttributeError:
						players.append(soup.span.text.strip())

				position_selector = '.nfl-o-injury-report__container:nth-child(3) td:nth-child(2)'
				for i, match in enumerate(response.css(position_selector).getall()):
					soup = BeautifulSoup(match)
					positions.append(soup.text.strip())

				injury_selector = '.nfl-o-injury-report__container:nth-child(3) td:nth-child(3)'
				for i, match in enumerate(response.css(injury_selector).getall()):
					soup = BeautifulSoup(match)
					injury_lst.append(soup.text.strip())

				game_status_selector = '.nfl-o-injury-report__container:nth-child(3) td:nth-child(7)'
				for i, match in enumerate(response.css(game_status_selector).getall()):
					soup = BeautifulSoup(match)
					val = soup.text.strip().lower().capitalize()
					if val == '(-)':
						game_status.append(None)
					else:
						game_status.append(val)

				week_key = self.year + current_week 

				for i, player in enumerate(players):
					
					engine = db_connect()
					self.Session = sessionmaker(bind=engine)
					session = self.Session()
					injury = InjuryReport()

					injury_exists = session.query(InjuryReport).filter_by(team_key=team_name, week_key=week_key, player_key=players[i]).first()
					if injury_exists:
						print('Injury already exists for {0} during week {1}.'.format(players[i], week_key))
					else:
						print('Adding injury of player {0} during week {1}.'.format(players[i], week_key))
						injury_key = team_name.replace(' ', '') + week_key + players[i].replace(' ', '') + 'REP'

						injury.injury_key = injury_key.upper()
						injury.year = self.year
						injury.week = current_week_num
						injury.team_key = team_name
						injury.week_key = week_key
						injury.player_key = players[i]
						injury.position = positions[i]
						injury.injury_location = injury_lst[i]
						injury.game_status = game_status[i]

						try:
							session.add(injury)
							session.commit()
						except:
							session.rollback()
							raise
					session.close()

			

			weeks_css = response.css('.d3-o-dropdown option').getall()
			weeks = []
			for week in weeks_css:
				soup = BeautifulSoup(week)
				weeks.append(soup.option.text.strip().split(' ')[-1])

			site_url = '/'.join(response.url.split('/')[:-1]) + '/REG{week}'

			for week in weeks:
				yield scrapy.Request(site_url.format(week=week), callback=self.parse)


	




