# Description: Connect to an existing Chrome DevTools Protocol session using the WebDriver protocol.
# /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_dev" &
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import os

# Start Chrome with remote debugging enabled in full screen
os.system('/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_dev" --start-fullscreen &')

# Connect to the Chrome DevTools Protocol
response = requests.get('http://localhost:9222/json')
debugger_url = response.json()[0]['webSocketDebuggerUrl']

# Start a new WebDriver session
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "localhost:9222")
driver = webdriver.Chrome(options=options)

# Get the session ID
session_id = driver.session_id
print(f"Session ID: {session_id}")

# Example: Interact with the browser
# driver.get("https://www.youtube.com")
# time.sleep(10)
# for _ in range(100):
#     webdriver.ActionChains(driver).send_keys('\t').perform()
# webdriver.ActionChains(driver).send_keys('\n').perform()

# Close the driver
driver.quit()