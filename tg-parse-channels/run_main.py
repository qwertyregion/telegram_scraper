
import schedule
from main_pars import start_script


def run_main_pars():
    schedule.every().day.at('16:36').do(start_script)  #start_script()
    while True:
        schedule.run_pending()


if __name__ == '__main__':
    run_main_pars()

