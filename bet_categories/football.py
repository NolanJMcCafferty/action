from bet_category import BetCategory
from bet import Bet
from pinnacle import Pinnacle
from bet_categories.bet_category_constants import football_team_dict

class Football(BetCategory):

	def __init__(self):
		self.ou_multiplier = 6.0
		self.handicap_multiplier = 8.0

	def get_period(self, title):
		if "1h" in title:
			return 1
		elif "(Qs)" in title or "1q" in title:
			return 3
		else:
			return 0

	def get_period_text(self):
		if self.period == 1:
			period_text = '1st Half'
		elif self.period == 3:
			period_text = '1st Quarter'
		else:
			period_text = 'Game'

		return period_text

	def fix_team_names(self, team):
		team_name = (
			team.replace("1h ", "")
			.replace("1q ", "")
			.replace(".", "")
		)

		if team_name in football_team_dict:
			team_name = football_team_dict[team_name]

		return team_name
