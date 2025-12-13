# 파일명: crawl_baemin.py (경로 수정 최종본)
import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

print("--- Baemin 리뷰 크롤링 시작 (최종 수정본) ---")

# 1. 경로 설정 (여기가 문제였음!)
# 현재 프로젝트 폴더 안에 있는 'chromedriver-win64' 폴더 안의 'chromedriver.exe'를 가리킵니다.
current_folder = os.getcwd()  # 현재 폴더 (CrawlingProject)
driver_path = os.path.join(current_folder, "chromedriver-win64", "chromedriver.exe")

print(f"사용할 드라이버 경로: {driver_path}")

# 2. 봇 탐지 우회 옵션
options = Options()
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")

# 3. 드라이버 실행
try:
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 5)
    print(" Chrome 브라우저 실행 성공!")
except Exception as e:
    print(f" 드라이버 실행 실패: {e}")
    print("폴더 안에 'chromedriver.exe'가 없는 것 같습니다.")
    print("'chromedriver-win64' 폴더 안에 또 다른 폴더가 있는지 확인해보세요.")
    exit()

# 4. 페이지 이동
app_id = 'com.woowahan.delivery'
url = f"https://play.google.com/store/apps/details?id={app_id}&hl=ko&gl=KR"
driver.get(url)

# 5. "리뷰 모두 보기" 버튼 클릭
try:
    # 1차 시도: 텍스트 기반 XPATH
    review_button_xpath = "//span[text()='리뷰 모두 보기']/ancestor::button[1]"

    see_all_reviews_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, review_button_xpath)
    ))
    see_all_reviews_button.click()
    print("리뷰 모두 보기 모달 진입 성공.")

except TimeoutException:
    print(" '리뷰 모두 보기' 버튼을 찾지 못했습니다.")
    print("   -> 봇 탐지는 통과했으나, 버튼 XPATH가 맞지 않습니다.")
    print("   -> 해결책: F12를 눌러 버튼의 XPATH를 복사해 코드의 review_button_xpath 변수에 붙여넣으세요.")
    driver.quit()
    exit()

# 6. 모달 창(스크롤 영역) 찾기
try:
    modal_dialog_xpath = '//*[@id="yDmH0d"]/div[4]/div[2]/div'
    modal_dialog = wait.until(EC.presence_of_element_located(
        (By.XPATH, modal_dialog_xpath)
    ))
    print("모달 창(스크롤 영역) 찾기 성공.")
except TimeoutException:
    print(" 모달 스크롤 영역을 찾지 못했습니다.")
    print("   -> F12를 눌러 모달 창의 XPATH를 복사해 코드의 modal_dialog_xpath 변수에 붙여넣으세요.")
    driver.quit()
    exit()

# 7. 스크롤링 및 데이터 수집
target_count = 10000
reviews_data = []
unique_reviews = set()
last_height = driver.execute_script("return arguments[0].scrollHeight", modal_dialog)

while len(reviews_data) < target_count:
    # 리뷰 컨테이너 찾기
    reviews_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'RHo1pe')]")

    if not reviews_elements:
        print("리뷰 요소를 찾을 수 없습니다. (클래스명 변경 가능성 있음)")
        break

    for review in reviews_elements:
        try:
            content_element = review.find_element(By.XPATH, ".//div[@class='h3YV2d']")
            content = content_element.text

            if content and len(content.strip()) >= 10:
                date_element = review.find_element(By.XPATH, ".//span[@class='bp9Aid']")
                date = date_element.text

                score_element = review.find_element(By.XPATH, ".//div[@role='img']")
                score_aria_label = score_element.get_attribute('aria-label')
                score = score_aria_label.split(' ')[2][0]

                review_id = hash(content + date)
                if review_id not in unique_reviews:
                    reviews_data.append({
                        'app': 'Baemin',
                        'date': date,
                        'score': int(score),
                        'content': content
                    })
                    unique_reviews.add(review_id)

        except NoSuchElementException:
            continue

    print(f"현재 수집된 유효 리뷰 수: {len(reviews_data)} / {target_count}")

    if len(reviews_data) >= target_count:
        print("목표치 달성. 스크롤 중단.")
        break

    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', modal_dialog)
    time.sleep(2.5)

    new_height = driver.execute_script("return arguments[0].scrollHeight", modal_dialog)
    if new_height == last_height:
        print("더 이상 스크롤할 내용이 없습니다.")
        break
    last_height = new_height

# 8. 저장
driver.quit()

if reviews_data:
    df = pd.DataFrame(reviews_data)
    if len(df) > target_count:
        df = df.head(target_count)
    df.to_csv('baemin_reviews.csv', index=False, encoding='utf-8-sig')
    print(f" 배달의 민족 리뷰 {len(df)}건 CSV 저장 완료: baemin_reviews.csv")
else:
    print("️ 수집된 리뷰가 없습니다.")