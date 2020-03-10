from bet_category import BetCategory
from bet import Bet
from pinnacle import Pinnacle
from bet_categories.bet_category_constants import rugby_team_dict


class Rugby(BetCategory):

	def __init__(self):
		self.handicap_multiplier = 16.0
		self.ou_multiplier = 12.0

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
		team_name = (
			team.replace("1h ", "")
			.replace("1q ", "")
			.replace("tot pts ", "")
			.replace(" fc", "")
			.replace("r.", "")
			.replace("msv ", "")
			.replace("vfl ", "")
		)

		if team_name in rugby_team_dict:
			team_name = rugby_team_dict[team_name]

		return team_name
