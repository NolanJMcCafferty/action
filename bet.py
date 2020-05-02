import datetime


class Bet:
    
    # ---------- These are example bet constants --------------
    threshold = .25
    MIN_BET = 10.0
    MAX_RISK = 20.0
    MAX_WIN = 500.0
    MULT = 1.0  # should be increased when max risk is increased

    log_file = datetime.datetime.today().strftime('logs/bet_logs/%Y_%m_%d.txt')

    def __init__(
        self,
        sport, 
        title,
        team,
        action_odds, 
        pinnacle_odds,
        bet_type,
        add_bet_line,
        action_line=None,
    ):  
        self.sport = sport
        self.title = title
        self.team = team
        self.action_line = action_line
        self.action_odds = action_odds
        self.pinnacle_odds = pinnacle_odds
        self.type = bet_type
        self.add_bet_line = add_bet_line
        self.perc_off = self.get_percent_off()
        self.size = self.get_size()

    def get_percent_off(self):
        abs_action_odds = abs(self.action_odds)
        abs_pinnacle_odds = abs(self.pinnacle_odds)

        if self.odds_cross_over():
            percent_off = (abs_pinnacle_odds + abs_action_odds - 200) / min(abs_pinnacle_odds, abs_action_odds)
        elif self.action_odds >= 0:
            percent_off = (self.action_odds - self.pinnacle_odds) / self.pinnacle_odds
        else:
            percent_off = (self.action_odds - self.pinnacle_odds) / abs_action_odds

        percent_off = round(percent_off, 2) if self.action_odds > self.pinnacle_odds else 0.0
        return percent_off

    def odds_cross_over(self):
        return (self.action_odds < 0 < self.pinnacle_odds) or (self.pinnacle_odds < 0 < self.action_odds)

    def get_size(self):
        perc_above_threshold = self.perc_off - Bet.threshold

        if perc_above_threshold > 0:
            bet_size = min(Bet.MIN_BET + Bet.MULT * perc_above_threshold, self.get_largest_bet(Bet.MAX_RISK))
            bet_size = int(5 * round(bet_size / 5))  # round to nearest multiple of 5

            return bet_size
        else:
            return 0

    def get_largest_bet(self, max_risk):
        if self.action_odds > 0:
            size = Bet.MAX_WIN / (self.action_odds / 100.0)
        else:
            size = max_risk / (self.action_odds / -100.0)
        
        return max(1, size)

    def get_to_win(self):
        if self.action_odds <= 0:
            return self.size
        else:
            return int(self.size * (self.action_odds / 100))

    def get_risk(self):
        if self.action_odds >= 0:
            return self.size
        else:
            return int(self.size * (self.action_odds / -100))

    def log(self):
        with open(Bet.log_file, 'a+') as file:
            file.writelines(str(self))

    def __eq__(self, other):
        return self.team == other.team

    def __str__(self):
        return (
            f"Sport: {self.sport}, Title: {self.title}, Team: {self.team}\n"
            f"\tType: {self.type}, Line: {self.action_line}, Odds: {self.action_odds}\n"
            f"\tRisk: {self.get_risk()}, To Win: {self.get_to_win()}\n"
            f"\tPercent Off: {self.perc_off}\n\n"
        )
