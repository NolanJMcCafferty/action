# -------- input book logins here --------
USERNAME1=rcoles900
PASSWORD1=colesr1000

USERNAME2=sample_username2
PASSWORD2=sample_password2

log_bets:
	python3 bet_controller.py $(USERNAME1)+$(PASSWORD1) $(USERNAME2)+$(PASSWORD2)

place_bets:
	python3 bet_controller.py -p $(USERNAME1)+$(PASSWORD1) $(USERNAME2)+$(PASSWORD2)
