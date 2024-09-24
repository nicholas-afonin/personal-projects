import time

"""
GOAL
Make a program that can predict which platform a GO-train will arrive at.

Available platforms: 3-13, 20-21
Pairs: (3-4), (5-6), (7-8), (9-10), (11-12), (13)  , (20-21)

Basic algorithm:
Show you which platforms are not currently occupied

Advanced algorithm: 
- consider history and likelihood of train arriving at a certain platform
- consider which platforms were recently used
"""


def get_current_info():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By

    # initialize the driver to use chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # open departures information
    driver.get('https://www.gotransit.com/en/find-a-station-or-stop/un/routes-departures?q=departures')

    departures_table = driver.find_element(By.XPATH, '//*[@id="main"]/div[1]/div[2]/div/div/section/div/div/div/div[2]/div/div[2]')
    print(departures_table)

    raw_info = []

    done = False
    count = 1
    while not done:
        string = '/html/body/div[1]/div[1]/main/div[1]/div[2]/div/div/section/div/div/div/div[2]/div/div[2]/div[' + str(count) + ']'
        try:
            raw_train_info = driver.find_element(By.XPATH, string).text.split('\n')
            [raw_train_info.pop(a) for a in [3, 4, 5, 6]]  # get rid of some useless info
            raw_info.append(raw_train_info)  # add it to big list
        except:
            done = True
        count += 1

    print(raw_info)

    formatted_info = []
    for train in raw_info:
        formatted_info.append([train[0], train[4]])

    print(formatted_info)

    time.sleep(10)





def get_platform(line: str):
    pass



if __name__ == "__main__":
    get_current_info()