from bet_category import BetCategory
from bet import Bet
from pinnacle import Pinnacle
from bet_categories.bet_category_constants import hockey_team_dict

class Hockey(BetCategory):

	def __init__(self):
		self.ou_multiplier = 42.0
		self.handicap_multiplier = 105.0

	def get_period(self, title):
		if "1p" in title:
			return 1
		else:
			return 0

	def get_period_text(self):
		return '1st Period' if self.period == 1 else None
			
	def fix_team_names(self, team):
		team = team.replace("1p ", "").replace("tot pts ", "")
		if team in hockey_team_dict:
			team = hockey_team_dict[team]

		return team
