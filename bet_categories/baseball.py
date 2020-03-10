from bet_category import BetCategory
from bet import Bet
from pinnacle import Pinnacle

class Baseball(BetCategory):

	def __init__(self):
		self.ou_multiplier = 45.0
		self.handicap_multiplier = 100.0

	def get_period(self, title):
		return 0

	def get_period_text(self):
		period_text = 'Game'

		return period_text

	def fix_team_names(self, team):
		team = (
			team.replace(" -", "")
		)

		return team
