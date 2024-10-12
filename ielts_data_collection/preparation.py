!pip install chromedriver-autoinstaller
import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
import time
import json
import chromedriver_autoinstaller
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Sử dụng Selenium để đăng nhập
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless') # ensure GUI is off
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("window-size=1920,1080")  # Example resolution

chromedriver_autoinstaller.install()
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://study4.com/login/")

#Đăng nhập bằng facebook account
driver.find_element(By.CLASS_NAME,"f-login-button").click()

email_input = driver.find_element(By.ID,"email")
email_input.send_keys("nmjuyh26@gmail.com")

password_input = driver.find_element(By.ID,"pass")
password_input.send_keys("tientumega")

driver.find_element(By.ID,"loginbutton").click()
time.sleep(3)

driver.find_element(By.XPATH,"//div[@role='button']").click()
time.sleep(5)

# Sử dụng WebDriverWait để chờ phần tử có thể nhấp được
wait = WebDriverWait(driver, 10)

with open('tests.json') as file:
    data = json.load(file)

for row in data:
    url = row['test_url']
    driver.get(url)
    if "speaking" in url:
        continue
    try:
        driver.find_element(By.CLASS_NAME,"test-user-results").is_displayed()
        print(f"Skips {url}")
        continue
    except NoSuchElementException:
        try:
            driver.find_element(By.XPATH,'//a[@href="#nav-taketest"]').click()
            take_test_element = wait.until(EC.element_to_be_clickable((By.ID, 'nav-taketest')))
            ActionChains(driver).move_to_element(take_test_element).perform()
            take_test_link = take_test_element.find_element(By.XPATH, '//a[@class="btn btn-primary"]')
            take_test_link.click()
            time.sleep(5)
            if "writing" in url:
                try:
                    tex_answer_input = wait.until(EC.element_to_be_clickable
                                                  ((By.XPATH,'//textarea[@class="form-control jqwordcount"')))
                    ActionChains(driver).move_to_element(tex_answer_input).perform()
                    tex_answer_input.send_keys("Fake Answers")
                    tex_submit = wait.until(EC.element_to_be_clickable((By.ID,'submit-test')))
                    ActionChains(driver).move_to_element(tex_submit).perform()
                    tex_submit.click()
                    print(f"Did Urls: {url}")
                    time.sleep(30)
                except:
                    print(f"Error:{url}")
                    continue
            else:
                try:
                    answer_input = wait.until(EC.element_to_be_clickable((By.XPATH,'//input[@class="form-control "]')))
                    ActionChains(driver).move_to_element(answer_input).perform()
                    answer_input.send_keys("Fake Answer")
                    submit = wait.until(EC.element_to_be_clickable((By.ID,'submit-test')))
                    ActionChains(driver).move_to_element(submit).perform()
                    submit.click()
                    print(f"Did Urls: {url}")
                    time.sleep(30)
                except:
                    print(f"Error:{url}")
                    continue
        except:
            print(f"Error:{url}")
            continue
driver.quit()