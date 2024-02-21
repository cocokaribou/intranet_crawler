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
from models import Employee, Resource, ResourceResultCode
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


"""
    :param str token: session cookie value as a token
    :param int type: Men `10` / Women `20`
"""
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
            rows = soup.find_all('input', attrs={'name': 'work_date_0_status'})

            result = [
                Resource(
                    isBooked=row.get('value', ''),
                    isMine=row.get('value', '') == "Y" and row.get('onclick', '') != "return false;"
                )
                for row in rows[1:]
            ]

            # split result list into 11 chunks (8,9,10...17,18)
            return [x.tolist() for x in np.array_split(result, 11)]

        except Exception as e:
            print(e)
            return []


"""
    :param str token: session cookie value as a token
    :param int type: Men `10` / Women `20`
    :param list[int] selected_blocks: list of index of selected blocks. up to 3
    :return: [ResourceBookResult] code
"""
def book_resources(token: str, type: int, selected_blocks: list[int]) -> ResourceResultCode:
    if len(selected_blocks) == 0:
        return ResourceResultCode.EMPTY_LIST

    if len(selected_blocks) > 3:
        return ResourceResultCode.OVER_THREE

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

            rows = browser.find_multiple(By.NAME, 'work_date_0_status')

            # prevent overbooking (6 blocks per day)
            my_booked_list = [row for row in rows if row.get_attribute('value') == 'Y' and row.get_attribute('onclick') != 'return false;']
            if len(my_booked_list) > 6:
                return ResourceResultCode.OVER_SIX

            # click available time blocks
            for i in selected_blocks:
                if rows[i].get_attribute('onclick') != 'return false;':
                    rows[i].click()

            # save changes
            save_button = WebDriverWait(browser, 1).until(
                EC.presence_of_element_located((By.ID, 'SaveBtn'))
            )
            save_button.click()
            time.sleep(0.5)
            if browser.alert_text() == "저장하시겠습니까?":
                browser.confirm_alert()

            time.sleep(0.5)
            if browser.alert_text() == "처리되었습니다.":
                browser.confirm_alert()

            return ResourceResultCode.SUCCESS

        except UnexpectedAlertPresentException as e:
            print(e)
            return ResourceResultCode.ERROR


"""
    for testing out chrome browser crawling feature.
"""
if __name__ == "__main__":
    # scrap_employee_list(login(ID, PWD))
    book_resources(login(ID, PWD), 20, [7, 8, 9])
