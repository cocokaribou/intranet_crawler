from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from browser import Browser
from models import Employee, Input, LoginResult

BASE_DOMAIN = "http://world.pionnet.co.kr:8096"


class Crawler:
    browser = Browser(BASE_DOMAIN)

    # 로그인
    def login(self, usr_input: Input) -> LoginResult:
        # 로그아웃부터 시켜준다
        self.browser.logout()
        try:
            input_id = self.browser.find_single(value='login_id')
            input_id.send_keys(usr_input.id)

            input_pw = self.browser.find_single(value='password')
            input_pw.send_keys(usr_input.password)
            input_pw.send_keys(Keys.ENTER)

            if self.browser.is_at_main():
                return LoginResult(code=1000)
            else:
                return LoginResult(code=9999, msg="로그인 실패!")

        except UnexpectedAlertPresentException as e:
            return LoginResult(code=9999, msg=e.alert_text)

    # 직원조회
    def scrap_employee_list(self) -> list[Employee]:
        try:
            self.browser.execute_script(
                f"window.location.href='{BASE_DOMAIN}"
                + "/employee/employeeMgmt.do?method=selectEmployeeList&rowsPerPage=300&enter_yn=Y'")

            return list(map(lambda x: Employee.from_string(x.text),
                            self.browser.find_multiple(By.TAG_NAME, 'table')[5].find_elements(By.TAG_NAME, 'tr')[1:]))

        except Exception:
            return list()

    # 로그아웃 후 백그라운드 브라우저 종료
    def logout(self) -> LoginResult:
        try:
            self.browser.logout()

            input_id = self.browser.find_single(value='login_id')

            if input_id:
                return LoginResult(code=1000)
            else:
                return LoginResult(code=9999, msg="로그아웃 실패!")

        except Exception as e:
            return LoginResult(code=9999, msg=e)
