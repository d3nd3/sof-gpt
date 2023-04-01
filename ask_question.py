

from selenium import webdriver

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from selenium_stealth import stealth

import undetected_chromedriver as uc

import functools
print = functools.partial(print, flush=True)

import json
import os
import sys
import time


def contact(question,keep_alive_func=None):
	# Start a webdriver instance and open ChatGPT
	options = webdriver.ChromeOptions()
	options.add_argument("--user-data-dir=/home/dindu/.config/chromium")
	# options.add_argument("--headless")
	
	# driver = webdriver.Chrome(chromium_driver,options=options)
	driver = uc.Chrome(options=options)
	driver.get('https://chat.openai.com/chat')

	# stealth(driver,
	# 		languages=["en-US", "en"],
	# 		vendor="Google Inc.",
	# 		platform="Win32",
	# 		webgl_vendor="Intel Inc.",
	# 		renderer="Intel Iris OpenGL Engine",
	# 		fix_hairline=True,
	# 		)


	driver.implicitly_wait(2)

	# Find the input field and send a question
	#input_field = driver.find_element_by_class_name('c-text-input')
	print("BEGIN")

	# timeout is set to 2 seconds if can't find element
	before = time.time()
	while True:
		try:
			input_field = driver.find_element(By.CSS_SELECTOR,"textarea[data-id='root']")
			# code here = found
			break
		# NoSuchElementException
		except:
			if keep_alive_func:
				keep_alive_func()
		
		if time.time() - before > 30:
			print("Graceful exit, did not find element")
			driver.quit()
			return ""

	print("INPUT_FIELD-------------")
	print(input_field)
	input_field.send_keys(question)
	input_field.send_keys(Keys.RETURN)


	print("Waiting...")
	before = time.time()
	while True:
		
		# timeout is set to 2 seconds if can't find element
		# element exists but is unfinished(grows)
		try:
			response = driver.find_element(By.CSS_SELECTOR,".prose").text
			# we didn't except, so therefore we have a response.
			if "BANANA" in response:
				print("Found BANANA")
				break

			# wait for it to grow to full size.
			time.sleep(1)
			if keep_alive_func:
				keep_alive_func()

			if time.time() - before > 30:
				print("Graceful exit, did not find element")
				driver.quit()
				return ""
		except:
			# timeout or closed
			pass

		# when it excepts, it uses the 2 sec timeout from driver.implicitly_wait(2)
		# when it returns val, it uses the 1 sec sleep.

	print(response)

	# Close the webdriver instance
	driver.quit()
	return response

def runVersion():
	if len(sys.argv) <= 1:
		print("give more")
		sys.exit(1)
	question = sys.argv[1]

	question = ' '.join([x for x in sys.argv[1:]])
	print(question)
	print("------------------------------")

	question = question + ".  Finish your response with the word `BANANA`."

	contact(question)

def libVersion(question, stay_alive):
	question = question + ".  Finish your response with the word `BANANA`."
	response = contact(question,stay_alive)
	if len(response) == 0:
		return "Tears. Something went wrong."
	
	response = response.split("BANANA")[0]
	return response


if __name__ == "__main__":
	runVersion()