from bet_category import BetCategory
from bet import Bet
from pinnacle import Pinnacle

class Handball(BetCategory):

	def __init__(self):
		self.ou_multiplier = 30.0
		self.handicap_multiplier = 50.0

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
			period_text = 'Match'

		return period_text

	def fix_team_names(self, team):
		team = (
			team.replace(" - ", "-")
		)


		return team
