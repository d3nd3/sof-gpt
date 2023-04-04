

from selenium import webdriver

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# from selenium_stealth import stealth

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

	input_field.send_keys(question)
	input_field.send_keys(Keys.RETURN)

	before = time.time()
	previous_length = 0
	while True:
		
		# timeout is set to 2 seconds if can't find element
		# element exists but is unfinished(grows)
		try:
			response = driver.find_element(By.CSS_SELECTOR,".prose")

			# wait for it to grow to full size.
			time.sleep(2)

			if not (len(response.text) > previous_length):
				# output has not grown
				print("----Think Output has ended----")
				response = response.text
				break

			previous_length = len(response.text)

			if keep_alive_func:
				keep_alive_func()

			if time.time() - before > 30:
				print("----Graceful exit, did not find element----")
				driver.quit()
				return ""
		except:
			# timeout or closed
			pass

		# when it excepts, it uses the 2 sec timeout from driver.implicitly_wait(2)
		# when it returns val, it uses the 1 sec sleep.

	print(response)

	try:
		clear = driver.find_element(By.CSS_SELECTOR,"nav>a:nth-child(3)")
		clear.click()
		# print("----clicked once----")
		time.sleep(0.25)
		try:
			clear = driver.find_element(By.CSS_SELECTOR,"nav>a:nth-child(3)")
			clear.click()
			# print("---clicked twice----")
		except:
			print("----inner cannot find that nav----")
			
	except:
		print("----canot find that nav----")
		



	# Close the webdriver instance
	driver.quit()
	return response

def runVersion(keep_alive_func):
	if len(sys.argv) <= 1:
		print("give more")
		sys.exit(1)
	question = sys.argv[1]

	question = ' '.join([x for x in sys.argv[1:]])
	print(question)
	print("------------------------------")

	question = question + ".  Finish your response with the word `BANANA`."

	contact(question,keep_alive_func)

# gpt_ask
def libVersion(question, keep_alive):
	response = contact(question,keep_alive)
	if len(response) == 0:
		return "Tears. Something went wrong."
	
	return response


if __name__ == "__main__":
	runVersion()