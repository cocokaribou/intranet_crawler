from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from browser import Browser
from models import Employee, Input, LoginResult

BASE_DOMAIN = "http://world.pionnet.co.kr:8096"
SESSION_COOKIE_KEY = "PION_JSESSIONID"


class Crawler:
    session_cookie = ""

    # 로그인
    def login(self, usr_input: Input):
        browser = Browser(BASE_DOMAIN)

        try:
            input_id = browser.find_single(value='login_id')
            input_id.send_keys(usr_input.id)

            input_pw = browser.find_single(value='password')
            input_pw.send_keys(usr_input.password)
            input_pw.send_keys(Keys.ENTER)

            if browser.is_at_main():
                self.session_cookie = browser.get_cookie(SESSION_COOKIE_KEY)
                return LoginResult(code=1000, msg="로그인 성공!")

            else:
                self.session_cookie = ""
                return LoginResult(code=9999, msg="로그인 실패!")

        except UnexpectedAlertPresentException as e:
            self.session_cookie = ""
            return LoginResult(code=9999, msg=e.alert_text)

        finally:
            browser.quit()

    # 직원조회
    def scrap_employee_list(self) -> list[Employee]:
        browser = Browser(BASE_DOMAIN)
        browser.add_cookie(SESSION_COOKIE_KEY, self.session_cookie)

        try:
            browser.execute_script(
                f"window.location.href='{BASE_DOMAIN}"
                + "/employee/employeeMgmt.do?method=selectEmployeeList&rowsPerPage=300&enter_yn=Y'")

            return list(map(lambda x: Employee.init_from_list(image=x.find_element(By.TAG_NAME, 'img').get_attribute('src'),
                                                              input_string=x.text),
                            browser.find_multiple(By.TAG_NAME, 'table')[5].find_elements(By.TAG_NAME, 'tr')[1:]))

        except Exception:
            return list()

        finally:
            browser.quit()

    # 내 정보 조회
    def scrap_my_information(self) -> Employee:
        browser = Browser(BASE_DOMAIN)
        browser.add_cookie(SESSION_COOKIE_KEY, self.session_cookie)

        try:
            browser.execute_script(
                f"window.location.href='{BASE_DOMAIN}"
                + "/employee/employeeMgmt.do?method=modifyNewEmployee'")

            table = browser.find_multiple(By.TAG_NAME, 'table')[1]
            return Employee(
                id=(lambda x: x.get_attribute("value"))(table.find_elements(By.TAG_NAME, 'input')[0]),
                idx=(lambda x: x.get_attribute("value"))(table.find_elements(By.TAG_NAME, 'input')[3]),
                name=(lambda x: x.get_attribute("value"))(table.find_elements(By.TAG_NAME, 'input')[4]),
                department=(lambda x: x.get_attribute("value"))(table.find_elements(By.TAG_NAME, 'input')[13]),
                image=(lambda x: x.get_attribute("src"))(table.find_elements(By.TAG_NAME, 'img')[1]),
                position=(lambda x: Select(x).first_selected_option.text)(table.find_element(By.TAG_NAME, "select"))
            )

        except Exception:
            return Employee()

        finally:
            browser.quit()

    # 세션 정보 삭제
    def logout(self):
        self.session_cookie = ""
        return LoginResult(code=1000, msg="로그아웃 성공!")
