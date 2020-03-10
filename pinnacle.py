import time
import os
import sys
from selenium import webdriver


class Pinnacle:

	other_sports = [
	'volleyball', 
	'rugby-union', 
	'rugby-league', 
	'handball', 
	'snooker',
	'futsal',
	'darts',
	'esports',
	]
	other_leagues = ['mma']

	def __init__(self):
		options = webdriver.ChromeOptions()
		options.add_argument('--headless')
		options.add_argument('--no-sandbox')
		options.add_argument('--disable-dev-shm-usage')

		self.driver = webdriver.Chrome(
			chrome_options=options, 
			executable_path=os.getcwd() + '/chromedriver'
		)
		self.driver.get("https://www.pinnacle.com/en/")
		time.sleep(5)

		self.check_warning_message()

	def check_warning_message(self):
		warning_message = self.driver.find_elements_by_class_name('style_dismiss__3cpzC')

		if len(warning_message) > 0:
			warning_message[0].click()
			time.sleep(.5)

	def close(self):
		self.driver.close()

	def check_matchup(self):
		return 'vs' in self.driver.current_url

	def get_league_urls(self):
		games = self.driver.find_elements_by_xpath("//a[contains(@href, '-vs-')]")
		return [game.get_attribute('href') for game in games]

	def go_to_league(self, sport, league):
		league = league.replace(" ", "-")
		if sport in Pinnacle.other_sports or league in Pinnacle.other_leagues:
			league_url = f"https://www.pinnacle.com/en/{sport}/matchups"
			wait_text = 'Highlights' if sport == 'esports' else 'Matchups'
		else:
			league_url = f"https://www.pinnacle.com/en/{sport}/{league}/matchups/"
			wait_text = 'Markets'
		
		if self.driver.current_url != league_url:
			self.driver.get(league_url)
			self.wait_for_load(0, wait_text)
			time.sleep(.5)

	def go_to_game(self, game_url):
		try:
			if 'the-field' not in game_url:
				self.driver.get(game_url)
				self.wait_for_load(0, 'Markets')
				self.check_warning_message()
				return True
		except:
			pass
		
		return False

	def wait_for_load(self, iterations, text_match):
		try:
			self.driver.find_element_by_xpath(f"//*[contains(text(), '{text_match}')]")
		except:
			time.sleep(.01)
			if iterations < 800:
				self.wait_for_load(iterations+1, text_match)

	def get_handicap_odds(
		self, 
		period, 
		period_text, 
		home_or_away, 
		action_line,
		multiplier,
	):
		if period_text:
			try:
				self.driver.find_element_by_xpath(f"//*[contains(text(), 'Handicap – {period_text}')]").click()
			except:
				return None

		is_positive = False
		is_negative = False
		handicap_lines = self.driver.find_elements_by_xpath(f"//a[@data-test-type='spread' and @data-test-designation='{home_or_away}' and @data-test-period='{period}']")
		for index, handicap_line in enumerate(handicap_lines):
			if handicap_line.get_attribute('tooltip') != "Currently Offline":
				line = float(handicap_line.find_element_by_class_name('label').text)
				odds = Pinnacle.convert_odds(float(handicap_line.find_element_by_class_name('price').text))
				is_last_line = index == len(handicap_lines) - 1
				diff = Pinnacle.get_diff(line, action_line, multiplier)
				
				if line > 0:
					is_positive = True
				elif line < 0:
					is_negative = True

				if line == action_line:
					return odds
				elif (is_last_line and not (is_negative and is_positive)):
					adjusted_odds = Pinnacle.adjust_odds(odds, diff, True)
					return adjusted_odds
		return None

	def get_ou_odds(
		self, 
		period, 
		period_text, 
		total_type, 
		over_or_under, 
		action_line,
		home_or_away,
		multiplier
	):
		if period_text:
			try:
				total_type_title = total_type.replace("_", " ").title()
				self.driver.find_element_by_xpath(f"//*[contains(text(), '{total_type_title} – {period_text}')]").click()
			except:
				return None

		ou_lines = self.driver.find_elements_by_xpath(f"//a[@data-test-type='{total_type}' and @data-test-designation='{over_or_under}' and @data-test-period='{period}']")
		if total_type == 'team_total':
			ou_lines = [line for line in ou_lines if home_or_away in line.get_attribute('data-test-key')]

		for index, ou_line in enumerate(ou_lines):
			if ou_line.get_attribute('tooltip') != "Currently Offline":
				line = float(ou_line.find_element_by_class_name('label').text.split()[1])
				odds = Pinnacle.convert_odds(float(ou_line.find_element_by_class_name('price').text))
				is_last_line = index == len(ou_lines) - 1
				diff = Pinnacle.get_diff(line, action_line, multiplier)
				if line == action_line:
					return odds
				elif ((line > action_line) or (line < action_line and is_last_line)) and over_or_under == 'over':
					adjusted_odds = Pinnacle.adjust_odds(odds, diff, False)
					return adjusted_odds
				elif ((line > action_line) or (line < action_line and is_last_line)) and over_or_under == 'under':
					adjusted_odds = Pinnacle.adjust_odds(odds, diff, True)
					return adjusted_odds

		return None

	def adjust_odds(odds, diff, should_improve):
		adjusted_odds = odds + diff if should_improve else odds - diff 
		return Pinnacle.clean_odds(adjusted_odds)

	def get_diff(line, action_line, mult):
		return mult * (line - action_line)

	def clean_odds(odds):
		if -100 < odds < 0:
			return odds + 200
		elif 0 < odds < 100:
			return odds - 200
		else:
			return odds

	def get_ml_odds(
		self, 
		period, 
		period_text, 
		team, 
		is_last_name
	):
		if period_text:
			try:
				self.driver.find_element_by_xpath(f"//*[contains(text(), 'Money line – {period_text}')]").click()
			except:
				return None

		ml_lines = self.driver.find_elements_by_xpath(f"//a[@data-test-type='moneyline' and @data-test-period='{period}']")
		for ml_line in ml_lines:
			if ml_line.get_attribute('tooltip') != "Currently Offline":
				team_name = ml_line.find_element_by_class_name('label').text.lower()
				if team_name == team or (team in team_name and is_last_name):
					return Pinnacle.convert_odds(float(ml_line.find_element_by_class_name('price').text))
		return None
	
	def get_odds_to_win(self, team):
		ml_lines = self.driver.find_elements_by_xpath(f"//a[@data-test-type='moneyline']")
		for ml_line in ml_lines:
			if ml_line.get_attribute('tooltip') != "Currently Offline":
				team_name = ml_line.find_element_by_class_name('label').text.lower()
				if team_name == team:
					return Pinnacle.convert_odds(float(ml_line.find_element_by_class_name('price').text))
		return None

	def go_to_futures(self, link_text):
		if not link_text:
			return False
		else:
			self.driver.refresh()
			time.sleep(3)

			self.check_warning_message()

			try: 
				self.driver.find_element_by_xpath("//*[contains(text(), 'Outright')]").click()
				time.sleep(1)
			except:
				try:
					self.driver.find_element_by_xpath("//*[contains(text(), 'Futures')]").click()
					time.sleep(1)
				except:
					return False
			try:
				text_match = (
					f"//div[contains(text(), '?') or "
					f"contains(text(), '(All') or "
					f"contains(text(), 'Winner') or "
					f"contains(text(), 'To Win') or "
					f"contains(text(), 'Relegated')]"
				)
				tabs = self.driver.find_elements_by_xpath(text_match)
				for tab in tabs:
					tab.click()

				if link_text == 'Division':
					links = self.driver.find_elements_by_xpath(f"//*[contains(text(), '{link_text}')]")
					for link in links:
						link.click()
				else:
					self.driver.find_element_by_xpath(f"//*[contains(text(), '{link_text}')]").click()
			except:
				return False

			return True

	def convert_odds(pinnacle_odds):
		odds = ((pinnacle_odds - 2) * 100) - 5
		odds = odds - 100 if odds < 0 else odds + 100
		return int(odds)