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
from intranet_config import BASE_DOMAIN, SESSION_COOKIE_KEY, ID, PWD, PION_WORLD, TAB_LIST
import fb
import re


def login(usr_id, usr_pwd) -> str:
    with Browser() as browser:
        browser.load(BASE_DOMAIN)
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
    with Browser() as browser:
        browser.load(BASE_DOMAIN)
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
    with Browser() as browser:
        browser.load(BASE_DOMAIN)
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
    with Browser() as browser:
        browser.load(BASE_DOMAIN)
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
                for row in rows
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
    # prevent index out of range exception
    selected_blocks = [index for index in selected_blocks if 66 > index >= 0]

    if len(selected_blocks) == 0:
        return ResourceResultCode.EMPTY_LIST

    if len(selected_blocks) > 3:
        return ResourceResultCode.OVER_THREE

    with Browser() as browser:
        browser.load(BASE_DOMAIN)
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

            # click available time blocks
            for i in selected_blocks:
                if rows[i].get_attribute('onclick') != 'return false;':
                    rows[i].click()

            # prevent overbooking (6 blocks per day)
            my_booked_list = [row for row in rows if
                              row.get_attribute('value') == 'Y' and row.get_attribute('onclick') != 'return false;']
            print(len(my_booked_list))
            if len(my_booked_list) > 6:
                return ResourceResultCode.OVER_SIX

            # save changes
            save_button = WebDriverWait(browser, 1).until(
                EC.presence_of_element_located((By.ID, 'SaveBtn'))
            )
            save_button.click()
            time.sleep(0.5)
            if browser.alert_text() == "저장하시겠습니까?":
                browser.confirm_alert()

            # check result alert
            time.sleep(0.5)
            if browser.alert_text() == "Wrong Gender !! ":
                browser.confirm_alert()
                return ResourceResultCode.WRONG_GENDER

            if browser.alert_text() == "처리되었습니다.":
                browser.confirm_alert()

            return ResourceResultCode.SUCCESS

        except Exception as e:
            print(e)
            return ResourceResultCode.ERROR


def format_text(element):
    text_content = element.text.strip()

    if element.name in ["h1", "h2", "h3", "h4"]:
        return f"<{text_content}>\n"
    elif element.name == "li":
        list_content = text_content or "•".join(element.find('span').text if element.find('span') else "")
        return f"• {list_content}\n"
    elif element.name == "table":
        return format_table(element)
    else:
        return re.sub(r'\s+', ' ', text_content) if element.name not in ["table", "li"] else text_content


def format_table(table_element):
    markdown_table = "\n(table)\n"
    headers = [th.text.strip() for th in table_element.find_all('th')]
    markdown_table += "| " + " | ".join(headers) + " |\n"
    markdown_table += "| " + " | ".join(['---'] * len(headers)) + " |\n"

    for tr in table_element.find('tbody').find_all('tr'):
        row = [td.text.strip() for td in tr.find_all('td')]
        markdown_table += "| " + " | ".join(row) + " |\n"

    return markdown_table


def scrap_pion_world():
    result_strings = []

    with Browser() as browser:
        for i, tab in enumerate(TAB_LIST):
            browser.load(PION_WORLD + tab)
            time.sleep(1)  # Wait for any dynamic content to load

            is_work_tab = i in [20, 21, 22]

            soup = BeautifulSoup(browser.page_source(), "html.parser")
            div = soup.find_all("div", attrs={'class': 'container'})[2]
            tag_list = ["h1", "h2", "h3", "h4", "h5", "p", "span"] + (
                ["li", "dt", "dd", "a", "table"] if not is_work_tab else [])

            matching_tags = div.find_all(tag_list)
            matching_tags += div.find_all("div", class_="about-author2")

            formatted_text = [format_text(x) for x in matching_tags]
            result_strings.append(" ".join(formatted_text) + "\n" + "-" * 60 + "\n\n")

    return "".join(result_strings)


"""
    for testing out chrome browser crawling feature.
"""
if __name__ == "__main__":
    scrap_pion_world()
