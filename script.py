import json
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--headless")  

local_chromedriver = shutil.which("chromedriver")
if local_chromedriver:
    driver = webdriver.Chrome(service=Service(local_chromedriver), options=chrome_options)
else:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open the website
driver.get("https://stackoverflow.com/") 

try:
    accept_cookies = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    )
    accept_cookies.click()
    print("✅ Cookies accepted!")
except Exception as e:
    print("❌ Could not find the cookie button:", str(e))

base_url = "https://stackoverflow.com/questions/tagged/jax?page={}&tab=newest&pagesize=50"
data = []
page = 1

while True:
    print(f"Scraping Page: {page}...")
    driver.get(base_url.format(page))
    time.sleep(3)
    
    questions = driver.find_elements(By.CLASS_NAME, "s-post-summary")
    
    if not questions:
        print("No more questions found. Stopping scraper.")
        break

    for question in questions:
        try:
            has_accepted_answer = question.find_elements(By.CLASS_NAME, "has-accepted-answer")

            if has_accepted_answer:
                question_link = question.find_element(By.CSS_SELECTOR, ".s-post-summary--content-title a").get_attribute("href")
                driver.execute_script("window.open(arguments[0]);", question_link)
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(3)

                title = driver.find_element(By.CSS_SELECTOR, "h1.fs-headline1").text
                question_body = driver.find_element(By.CSS_SELECTOR, ".s-prose.js-post-body").text
                answers = []
                answer_elements = driver.find_elements(By.CSS_SELECTOR, ".answer .s-prose.js-post-body")

                for ans in answer_elements:
                    answers.append(ans.text)

                data.append({
                    "title": title,
                    "question": question_body,
                    "answers": answers,
                    "link": question_link
                })

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(2)

        except Exception as e:
            print(f"Error processing a question: {e}")

    page += 1

driver.quit()

with open("jax_questions.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"Scraping completed. {len(data)} questions saved to jax_questions.json.")
