from bet_category import BetCategory
from bet import Bet
from pinnacle import Pinnacle
from bet_categories.bet_category_constants import basketball_team_dict

class Basketball(BetCategory):

	def __init__(self):
		self.ou_multiplier = 16.0
		self.handicap_multiplier = 22.0

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
		team = (
			team.replace("1h ", "")
			.replace("1q ", "")
			.replace("tot pts ", "")
		)
		if team in basketball_team_dict:
			team = basketball_team_dict[team]
		elif '2q' in team or '3q' in team or '4q'in team:
			team = None

		return team
