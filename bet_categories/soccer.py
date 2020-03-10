from bet_category import BetCategory
from bet import Bet
from pinnacle import Pinnacle
from bet_categories.bet_category_constants import soccer_name_dict

class Soccer(BetCategory):

	def __init__(self):
		self.handicap_multiplier = 170.0
		self.ou_multiplier = 210.0
		
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

		to_advance = False
		if "to advance" in team_name:
			team_name = team_name.replace(" to advance", "")
			to_advance = True

		if team_name in soccer_name_dict:
			team_name = soccer_name_dict[team_name]

		if to_advance:
			team_name += " (to advance)"
		return team_name
