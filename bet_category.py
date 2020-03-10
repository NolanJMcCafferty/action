from abc import ABC, abstractmethod
import time
from bet import Bet
from bet_categories.bet_category_constants import league_dict

class BetCategory(ABC):

	switch_home_and_away = [
		'usa - american hockey league', 
		'rugby league - matchups',
		'rugby union - matchups',
	]

	last_name_sports = [
		'golf',
		'tennis', 
		'mixed-martial-arts', 
		'boxing'
	]

	url = 'https://engine.action247.ag/wager/Sports.aspx?WT=0&lid='

	def __init__(self):
		pass

	def add_attributes(self, driver, id, title, sport):
		self.driver = driver
		self.id = id
		self.league = BetCategory.get_league(title.lower())
		self.title = title
		self.sport = BetCategory.get_sport_name(sport, title)

	def get_league(title):
		league = (
			title.replace(" odds to win", "")
			.replace(" (1h)", "")
			.replace(" 2019/20 -", "")
			.replace(" 2019-2020 -", "")
			.replace(" -2019/20 -", "")
			.replace(" 2020 -", "")
			.replace("wta -", "wta")
			.replace("soccer - ", "") # for uefa odds to win
		)
		if league in league_dict:
			league = league_dict[league]
		elif "nba" in title:
			league = "nba"
		elif "wncaa" in title:
			league = "wncaa"
		elif "ncaa" in title:
			league = "ncaa"
		elif "nhl" in title:
			league = "nhl ot included"
		elif "nfl" in title:
			league = "nfl"
		elif 'mlb' in title:
			league = 'mlb'
		elif 'xfl' in title:
			league = 'xfl-football'

		return league

	def get_sport_name(sport, title):
		if 'football' in sport:
			sport = 'football'
		elif 'basketball' in sport:
			sport = 'basketball'
		elif sport == 'mma fighting':
			sport = 'mixed-martial-arts'
		elif sport == 'other sports':
			if 'futsal'in title:
				sport = 'futsal'
			elif 'rugby union' in title:
				sport = 'rugby-union'
			elif 'rugby league' in title:
				sport = 'rugby-league'
			elif 'volleyball' in title:
				sport = 'volleyball'
			else:
				sport = title

		return sport

	def get_period(self, title):
		pass

	def get_period_text(self):
		pass

	def get_total_type(self):
		return 'team_total' if 'team' in self.title else 'total'

	@abstractmethod
	def get_bets(self, pinnacle):
		pass

	def get_home_or_away(self, side):
		is_home = side == 1

		if self.league in BetCategory.switch_home_and_away:
			is_home = not is_home

		return 'home' if is_home else 'away'

	def is_last_name(self):
		return self.sport in BetCategory.last_name_sports

	def get_game_url(self, current_url, game_urls, away_team, home_team):
		away_team = (
			away_team.replace(" ", "-")
			.replace("/", "")
			.replace("(", "")
			.replace(")", "")
			.replace("'", "")
			.replace(".", "")
		)
		home_team = (
			home_team.replace(" ", "-")
			.replace("/", "")
			.replace("(", "")
			.replace(")", "")
			.replace("'", "")
			.replace(".", "")
		) 
		if self.sport == 'esports':
			away_team = away_team  + '-match'
			home_team = home_team  + '-match'

		if self.is_last_name():
			away_url_start, away_url_end = f'{away_team}-vs', f'{away_team}/'
			home_url_start, home_url_end = f'{home_team}-vs', f'{home_team}/'
		else:
			away_url_start, away_url_end = f'/{away_team}-vs', f'vs-{away_team}/'
			home_url_start, home_url_end = f'/{home_team}-vs', f'vs-{home_team}/'

		if (away_url_start in current_url and home_url_end in current_url) or (home_url_start in current_url and away_url_end in current_url):
			return current_url
		else:
			for game_url in game_urls:
				if (away_url_start in game_url and home_url_end in game_url) or (home_url_start in game_url and away_url_end in game_url):
					return game_url
		
		return None

	def get_bets(self, pinnacle):
		bets = []

		pinnacle.go_to_league(self.sport, self.league)
		game_urls = pinnacle.get_league_urls()

		if len(self.driver.find_elements_by_class_name('betting-lines-container')) > 0:
			for game in self.driver.find_elements_by_class_name('betting-lines-container'):
				rows = game.find_elements_by_xpath(".//*[@class='row even' or @class='row odd']")
				game_bets = self.get_game_bets(pinnacle, game_urls, rows, True)
				bets = bets + game_bets
		else:
			rows = self.driver.find_elements_by_xpath("//*[@class='row even' or @class='row odd']")
			for game in zip(rows[::2], rows[1::2]):
				game_bets = self.get_game_bets(pinnacle, game_urls, game, False)
				bets = bets + game_bets
				
		return bets

	def get_game_bets(self, pinnacle, game_urls, rows, draws):
		current_url = ''
		bets = []
		away, home = rows[0], rows[1]
		away_team = away.find_element_by_class_name('linesTeam').text.lower()
		home_team = home.find_element_by_class_name('linesTeam').text.lower()

		self.period = self.get_period(away_team)
		self.period_text = self.get_period_text()

		away_team = self.fix_team_names(away_team)
		home_team = self.fix_team_names(home_team)

		for side, row in enumerate([away, home]):
			home_or_away = self.get_home_or_away(side)

			if away_team and home_team:
				new_game_url = self.get_game_url(current_url, game_urls, away_team, home_team)
				game_match = True if new_game_url else False
				if new_game_url and new_game_url != current_url:
					current_url = new_game_url
					game_match = pinnacle.go_to_game(current_url)

				if game_match:
					team = away_team if side == 0 else home_team
					handicap_bet = self.get_handicap_bet(row, team, pinnacle, home_or_away)
					ou_bet = self.get_ou_bet(row, team, pinnacle, home_or_away)
					ml_bet = self.get_ml_bet(row, team, pinnacle)
					bets = BetCategory.add_valid_bets(bets, [handicap_bet, ou_bet, ml_bet])
		
		if draws and len(rows) > 2 and pinnacle.check_matchup():
				ml_bet = self.get_ml_bet(rows[2], 'draw', pinnacle)
				bets = BetCategory.add_valid_bets(bets, [ml_bet])

		return bets

	def add_valid_bets(bet_list, new_bets):
		for new_bet in new_bets:
			if new_bet and new_bet.size > 0:
				print(new_bet)
				bet_list.append(new_bet)

		return bet_list

	def get_handicap_bet(self, row, team, pinnacle, home_or_away):
		line = row.find_element_by_class_name('linesSpread')
		
		add_bet_line = line.get_attribute('onclick')
		if add_bet_line:
			bet_line = add_bet_line.split(',')
			line = float(bet_line[4].replace("'", "").replace("PK", "0"))
			odds = int(bet_line[5].replace("'", ""))
			pinnacle_odds = pinnacle.get_handicap_odds(
				self.period, 
				self.period_text, 
				home_or_away, 
				line,
				self.handicap_multiplier,
			)
			if pinnacle_odds:
				bet = Bet(
					sport = self.sport,
					title = self.title,
					team = team,
					action_line = line,
					action_odds = odds,
					pinnacle_odds = pinnacle_odds,
					bet_type = 'handicap',
					add_bet_line = add_bet_line,
				)
				return bet

	def get_ou_bet(self, row, team, pinnacle, home_or_away):
		line = row.find_element_by_class_name('linesMl')

		add_bet_line = line.get_attribute('onclick')
		if add_bet_line:
			bet_line = add_bet_line.split(',')
			bet_type = 'over' if bet_line[2].lower() == "'ov'" else 'under'
			line = float(bet_line[4].replace("'", ""))
			odds = int(bet_line[5].replace("'", ""))

			pinnacle_odds = pinnacle.get_ou_odds(
				self.period, 
				self.period_text, 
				self.get_total_type(), 
				bet_type, 
				line,
				home_or_away,
				self.ou_multiplier,
			)

			if pinnacle_odds:
				bet = Bet(
					sport = self.sport,
					title = self.title,
					team = team,
					action_line = line,
					action_odds = odds,
					pinnacle_odds = pinnacle_odds,
					bet_type = bet_type,
					add_bet_line = add_bet_line,
				)
				return bet

	def get_ml_bet(self, row, team, pinnacle):
		line_class = 'linesMl' if team == 'draw' else 'linesTotal'
		line = row.find_element_by_class_name(line_class)
		
		add_bet_line = line.get_attribute('onclick')
		if add_bet_line:
			bet_line = add_bet_line.split(',')
			odds = int(bet_line[5].replace("'", ""))

			pinnacle_odds = pinnacle.get_ml_odds(
				self.period, 
				self.period_text, 
				team, 
				self.is_last_name(),
		)
			if pinnacle_odds:
				bet = Bet(
					sport = self.sport,
					title = self.title,
					team = team,
					action_odds = odds,
					pinnacle_odds = pinnacle_odds,
					bet_type = 'ml',
					add_bet_line = add_bet_line,
				)
				return bet
