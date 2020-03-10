import sys
import time
from book import Book
from bet import Bet
from pinnacle import Pinnacle


class BetController:

    def __init__(self, books, place_bets):
        self.pinnacle = Pinnacle()
        self.place_bets = place_bets

        self.books = []
        for username, password in books.items():
            book = Book(
                username,
                password,
            )
            self.books.append(book)
        self.log_file = 'logs/error_logs/error_log.txt'

    def close_drivers(self):
        self.pinnacle.close()
        for book in self.books:
            book.close()

    def run(self): 
        try:
            self.run_scraper()
            self.close_drivers()
        except Exception as e:
            with open(self.log_file, 'a+') as error_log:
                error_log.write(repr(e) + '\n')
            print(f' -------- an error occured: check {self.log_file} --------')

    def run_scraper(self):
        book = self.books[0]
        bet_categories = book.get_bet_categories()

        for bet_category in bet_categories:
            book.open(bet_category)
            bets = bet_category.get_bets(self.pinnacle)
            
            if bets:
                self.log_bets(bets)

                if self.place_bets:
                    self.submit_bets(bet_category, bets)

    def submit_bets(self, bet_category, bets):
        for book in self.books:
            for bet in bets:
                if not BetController.bet_already_pending(book, bet):
                    book.make_bet(bet)
                    book.open(bet_category)

    def log_bets(self, bets):
        for bet in bets:
            if not BetController.bet_already_pending(self.books[0], bet):
                bet.log()

    def bet_already_pending(book, bet):
        bet_already_pending = False

        for pending_bet in book.pending_bets:
            for team_name in bet.team.split():
                if team_name in pending_bet:
                    bet_already_pending = True
                    break

        return bet_already_pending

if __name__ == "__main__":
    place_bets = True if sys.argv[1] == '-p' else False
    if place_bets:
        login_args = sys.argv[2:]
    else:
        login_args = sys.argv[1:]

    login_pairs = {}
    for arg in login_args:
        login = arg.split('+')

        if login[0] != 'none':
            login_pairs.update({login[0]: login[1]})

    bet_controller = BetController(login_pairs, place_bets)

    start_time = time.time()
    bet_controller.run()
    total_time = (time.time() - start_time) / 60
    print(f"total time: {total_time:.2f} minutes")