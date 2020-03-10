from bet_category import BetCategory
from bet import Bet
from pinnacle import Pinnacle
from bet_categories.bet_category_constants import odds_to_win_dict, odds_to_win_links_dict

class OddsToWin(BetCategory):

	def get_bets(self, pinnacle):
		bets = []

		pinnacle.go_to_league(self.sport, self.league)
		is_futures = pinnacle.go_to_futures(self.get_link_text())

		if is_futures:
		
			rows = self.driver.find_elements_by_xpath("//*[@class='row']")[3:]

			for row in rows:
				team = row.find_element_by_class_name('linesTeam').text.lower()
				team = OddsToWin.fix_team_names(team)

				new_bet = self.get_odds_to_win(row, team, pinnacle)
				bets = BetCategory.add_valid_bets(bets, [new_bet])

		return bets

	def get_link_text(self):
		link_text = None
		if self.title in odds_to_win_links_dict:
			link_text = odds_to_win_links_dict[self.title]
		elif 'division' in self.title:
			link_text = 'Division'

		return link_text

	def fix_team_names(team_name):
		if team_name in odds_to_win_dict:
			team_name = odds_to_win_dict[team_name]

		return team_name

	def get_odds_to_win(self, row, team, pinnacle):
		line_class = 'linesSpread'
		line = row.find_element_by_class_name(line_class)
		add_bet_line = line.get_attribute('onclick')
		
		if add_bet_line:
			bet_line = add_bet_line.split(',')
			odds = int(bet_line[5].replace("'", ""))

			pinnacle_odds = pinnacle.get_odds_to_win(team)
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


