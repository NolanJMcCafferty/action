import os
import time
from selenium import webdriver
from bet_category import BetCategory
from bet_categories.baseball import Baseball
from bet_categories.soccer import Soccer
from bet_categories.basketball import Basketball
from bet_categories.hockey import Hockey
from bet_categories.odds_to_win import OddsToWin
from bet_categories.fighting import Fighting
from bet_categories.volleyball import Volleyball
from bet_categories.cricket import Cricket
from bet_categories.rugby import Rugby
from bet_categories.tennis import Tennis
from bet_categories.golf import Golf
from bet_categories.football import Football
from bet_categories.handball import Handball
from bet_categories.snooker import Snooker
from bet_categories.futsal import Futsal
from bet_categories.darts import Darts
from bet_categories.esports import Esports
from bet_categories.table_tennis import TableTennis


class Book:

	def __init__(self, username, password):
		self.username = username
		self.password = password

		options = webdriver.ChromeOptions()
		options.add_argument('--headless')
		options.add_argument('--no-sandbox')
		options.add_argument('--disable-dev-shm-usage')

		self.driver = webdriver.Chrome(
			chrome_options=options, 
			executable_path=os.getcwd() + '/chromedriver'
		)

		self.login()
		self.pending_bets = self.get_pending_bets()

	def login(self):
		self.driver.get("http://action247.ag/")

		self.driver.find_element_by_id('account').send_keys(self.username)
		self.driver.find_element_by_id('password').send_keys(self.password)
		self.driver.find_element_by_css_selector("input[type='submit']").click()
		time.sleep(1)

	def close(self):
		self.driver.close()

	def get_pending_bets(self):
		pending_bets = []

		try:
			self.driver.get('https://engine.action247.ag/Wager/OpenBets.aspx')
			time.sleep(1)

			rows = self.driver.find_elements_by_xpath("//*[@class='TrGameOdd' or @class='TrGameEven']")

			for row in rows:
				if row.find_element_by_tag_name('th').text == 'Description':
					description = row.find_element_by_tag_name('td').text.lower()
					pending_bets.append(description)
		except:
			pass

		self.driver.get('https://engine.action247.ag/wager/Sports.aspx')
		time.sleep(1)

		return pending_bets

	def get_bet_categories(self):
		leagues = self.driver.find_elements_by_class_name('sportLeague')
		bet_categories = []
		for league in leagues:
			bet_category = None

			title = league.get_attribute('text').lower()
			sport = Book.get_sport(league, title)
			if 'odds to win' in title or 'winner' in title:
				bet_category = OddsToWin()
			elif sport == 'baseball':
				bet_category = Baseball()
			elif sport == 'football':
				bet_category = Football()
			elif sport == 'basketball':
				bet_category = Basketball()
			elif sport == 'hockey':
				bet_category = Hockey()
			elif sport == 'soccer':
				bet_category = Soccer()
			elif sport == 'tennis':
				bet_category = Tennis()
			elif sport == 'mixed-martial-arts' or sport == 'boxing':
				bet_category = Fighting()
			elif sport == 'cricket':
				bet_category = Cricket()
			elif sport == 'volleyball':
				bet_category = Volleyball()
			elif 'rugby' in sport:
				bet_category = Rugby()
			elif sport == 'golf':
				bet_category = Golf()
			elif sport == 'handball':
				bet_category = Handball()
			elif sport == 'snooker':
				bet_category = Snooker()
			elif sport == 'futsal':
				bet_category = Futsal()
			elif sport == 'darts':
				bet_category = Darts()
			elif sport == 'esports':
				bet_category = Esports()
			elif sport == 'table tennis':
				bet_category = TableTennis()

			if bet_category:
				bet_category.add_attributes(
					driver=self.driver,
					id=league.get_attribute('data-lg'),
					title=title,
					sport=sport,
				)
				bet_categories.append(bet_category)
		return bet_categories

	def open(self, bet_category):
		self.driver.get(BetCategory.url + bet_category.id)
		time.sleep(1)

	@staticmethod
	def get_sport(league, title):
		sport = league.find_element_by_xpath('./../../../..').get_attribute('id')
		sport = sport.replace("_", " ").split()
		sport = " ".join(sport[1:]).lower()
		return BetCategory.get_sport_name(sport, title)

	def make_bet(self, bet):
		self.driver.execute_script(bet.add_bet_line)
		self.driver.execute_script("checkBet()")
		time.sleep(2)
		self.driver.find_element_by_class_name('risk').send_keys(bet.get_risk())
		time.sleep(1)
		self.driver.execute_script("place_straight()")
		time.sleep(2)
		self.driver.execute_script("dobet()")
		time.sleep(5)
