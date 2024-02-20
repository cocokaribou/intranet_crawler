import time

from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from bs4 import BeautifulSoup
import numpy as np

from browser import Browser
from models import Employee, Resource
from intranet_config import BASE_DOMAIN, SESSION_COOKIE_KEY, ID, PWD
import fb


def login(usr_id, usr_pwd) -> str:
    with Browser(BASE_DOMAIN) as browser:
        try:
            input_id = WebDriverWait(browser, 1).until(
                EC.presence_of_element_located((By.ID, 'login_id'))
            )
            input_id.send_keys(usr_id)

            input_pw = WebDriverWait(browser, 1).until(
                EC.presence_of_element_located((By.ID, 'password'))
            )
            input_pw.send_keys(usr_pwd)
            input_pw.send_keys(Keys.ENTER)

            if browser.is_at_main():
                session_cookie = browser.get_cookie(SESSION_COOKIE_KEY)

            else:
                session_cookie = ""

        except UnexpectedAlertPresentException as e:
            session_cookie = ""

        finally:
            return session_cookie


def scrap_employee_list(token) -> list[Employee]:
    with Browser(BASE_DOMAIN) as browser:
        browser.add_cookie(SESSION_COOKIE_KEY, token)

        try:
            browser.load(
                f"{BASE_DOMAIN}/employee/employeeMgmt.do?method=selectEmployeeList&rowsPerPage=300&enter_yn=Y")

            soup = BeautifulSoup(browser.page_source(), "html.parser")
            rows = soup.find('table', attrs={'bgcolor': '#CCCCCC'}).find('tbody').find_all('tr')

            result = [
                Employee(
                    image=f"{BASE_DOMAIN}{row.find_next('img')['src']}",
                    idx=int(row.find_all('td')[1].text),
                    name=row.find_all('td')[2].text.strip(),
                    id=row.find_all('td')[4].text.strip(),
                    position=row.find_all('td')[6].text.strip(),
                    department=row.find_all('td')[12].text.strip()
                )
                for row in rows[1:-1]
            ]

            fb.save_intranet_user(result)
            return result

        except Exception as e:
            return []


def scrap_my_employee_number(token: str) -> int:
    with Browser(BASE_DOMAIN) as browser:
        browser.add_cookie(SESSION_COOKIE_KEY, token)

        try:
            browser.load(f"{BASE_DOMAIN}/employee/employeeMgmt.do?method=modifyNewEmployee")

            soup = BeautifulSoup(browser.page_source(), "html.parser")
            index = soup.find('input', attrs={'name': 'emp_no'}).get('value')
            return int(index) if index else -1

        except Exception:
            return -1


def scrap_booked_resources(token: str, type: int):
    with Browser(BASE_DOMAIN) as browser:
        browser.add_cookie(SESSION_COOKIE_KEY, token)

        today = datetime.today().strftime('%Y-%m-%d')
        try:
            # load timetable
            browser.load(
                f"{BASE_DOMAIN}/resource/viewResourceBookingList.do"
                f"?method=searchResourceBookingList&srch_base_dt={today}&resrc_code_id={type}")
            srch_button = WebDriverWait(browser, 1).until(
                EC.presence_of_element_located((By.ID, 'srch_button_01'))
            )
            srch_button.click()
            time.sleep(1)

            # parse table content
            soup = BeautifulSoup(browser.page_source(), "html.parser")
            rows = soup.find('table', attrs={'class': 'scrollTable'}).find('tbody').find_all('tr')

            result = []
            for row in rows[1:]:
                length = len(row.find_all('td'))
                index = 4 if length == 9 else (3 if length == 8 else (2 if length == 7 else None))

                block = row.find_all('td')[index].find('input', {'name': 'work_date_0_status'})
                result.append(Resource(
                    isBooked=block.get('value', ''),
                    isMine=block.get('value', '') == "Y" and block.get('onclick', '') != "return false;"
                ))

            return [x.tolist() for x in np.array_split(result, 11)]

        except Exception as e:
            print(e)
            return []


"""
    for testing out chrome browser crawling feature.
"""
if __name__ == "__main__":
    scrap_employee_list(login(ID, PWD))
    # scrap_booked_resources(token, resource_type["여자휴게실"])
