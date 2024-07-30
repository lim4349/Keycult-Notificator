from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import requests
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import threading
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# 슬랙 API 토큰 및 채널 설정
slack_token = "<토큰>"
slack_channel = "<채널이름>"
client = WebClient(token=slack_token)

# 슬랙 메시지 보내기
def send_slack_message(pretext, title, title_link):
    try:
        response = client.chat_postMessage(
            channel=slack_channel,
            text=pretext,
            attachments=[
                {
                    "pretext": pretext,
                    "title": title,
                    "title_link": title_link,
                    "fallback": title,
                    "color": "#36a64f",
                    "icon_emoji": ":exclamation:",
                    "username": "BOT"
                }
            ]
        )
        print("Slack message sent:", response)
        return response
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# 키컬트 페이지 모니터링
def monitor_keycult():
    purchase_page_url = 'https://keycult.com/products/no-2-65-raw-1' #'https://keycult.com/products/no-2-tkl-raw-edition'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    add_to_cart_visible = False

    while True:
        try:
            print("Checking the page for 'Add to cart' button...")
            driver.get(purchase_page_url)
            add_to_cart_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Add to cart')]"))
            )
            print("Found 'Add to cart' button.")
            if not add_to_cart_visible:
                add_to_cart_visible = True
                for i in range(20):
                    send_slack_message("키컬트 재고 알림", "키컬트 제품 재고가 있습니다!", purchase_page_url)
                    time.sleep(1)

        except Exception as e:
            print(f"Error: {e}")
            add_to_cart_visible = False

        time.sleep(random.randrange(30, 60))

if __name__ == '__main__':
    # 키컬트 모니터링 시작
    keycult_thread = threading.Thread(target=monitor_keycult)
    keycult_thread.daemon = True
    keycult_thread.start()

    while True:
        time.sleep(10)
