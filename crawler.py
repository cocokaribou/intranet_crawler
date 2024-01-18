from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import *
from selenium.webdriver.chrome.service import Service
from model.Employee import Employee

BASE_DOMAIN = "http://world.pionnet.co.kr:8096"


def scrap_employee_list(id, pwd):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Login
    try:
        driver.get(BASE_DOMAIN)
        input_id = driver.find_element(By.ID, 'login_id')
        input_id.send_keys(id)
        input_pw = driver.find_element(By.ID, 'password')
        input_pw.send_keys(pwd)
        input_pw.send_keys(Keys.ENTER)

        # 직원조회
        driver.execute_script(f"window.location.href='{BASE_DOMAIN}/employee/employeeMgmt.do?method"
                              "=selectEmployeeList&rowsPerPage=300&job_code=&param_team_name=&param_team_id=&enter_yn=Y"
                              "&param_emp_name=&'")

        employee_list = list(map(lambda x: Employee.from_string(x.text),
                                 driver.find_elements(By.TAG_NAME, 'table')[5].find_elements(By.TAG_NAME, 'tr')[1:]))

        return employee_list

    # Login Fail
    except UnexpectedAlertPresentException:
        return []

    finally:
        driver.quit()
