import configparser
config_parser = configparser.ConfigParser()
config_parser.read("config.ini")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

import time
import os

wait_time = 30

def init_chrome(download_dir=''):

	opts = webdriver.ChromeOptions()
	opts.add_argument('--no-sandbox') 
	opts.add_argument("--headless") 
	opts.add_argument("--disable-gpu") 
	opts.add_argument("--window-size=600,400") 
	opts.add_argument("--ignore-certificate-errors") 
	opts.add_argument("--log-level=3")
	if (download_dir != ''):
		print('Download Directory: {0}'.format(download_dir))
		prefs = {'download.default_directory' : download_dir}
		opts.add_experimental_option('prefs', prefs)	
	print('Opening Chrome')
	driver = webdriver.Chrome(chrome_options=opts)
	return driver

def switch_to_frame(driver, id):
	print('Switching to {0} iFrame'.format(id))
	#wait_for_iframe(driver, '//iframe[id="ngtModule"]')
	#driver.switch_to_frame(id)
	driver.switch_to.frame(id)
	# TODO: Ensure the iframe is loaded 
	#verify_iframe(driver, 'iframe[id="ngtModule"]')
	#driver.frame_to_be_available_and_switch_to_it('ngtModule')

def switch_to_window(driver):
	print('Switching to new window')
	for handle in driver.window_handles:
		driver.switch_to_window(handle)

def verify_iframe(driver, selector):
	WebDriverWait(driver, wait_time).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, selector)))

def verify_elem(driver, selector, wait=wait_time):
	elem = WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
	return elem

def verify_elems(driver, selector):
	WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
	elems = driver.find_elements_by_css_selector(selector)
	return elems

def sleep(t):
	print('Sleeping for {0} seconds'.format(t))
	time.sleep(t) # Wait for a few seconds

def get_url(driver, url):
	print('Fetching {0}'.format(url))
	driver.get(url)

def load_home_page(driver, url):
	print('Loading {0}...'.format(url))
	driver.get(url)
	print('Authenticating via Global Login')
	elem = verify_elem(driver, 'input[name="userid"]')
	elem.clear()
	elem.send_keys(config_parser['Selenium']['USERNAME'])
	elem = verify_elem(driver, 'input[name="password"]')
	elem.clear()
	elem.send_keys(config_parser['Selenium']['PASSWORD'])
	elem = verify_elem(driver, 'input[name="btnSubmit"]')
	elem.click()
	# Accept terms and conditions
	elem = verify_elem(driver, 'input[name="successOK"]')
	elem.click()
	print('Authenticated')
	if driver.current_url != url:
		print('Url is not yet fully loaded, waiting for {0} seconds.'.format(3))
		sleep(10)

def verify_file(path, filename):
	full_path = os.path.join(path, filename)
	print('Verifying file exists: {0}'.format(full_path))
	while not os.path.exists(full_path):
		time.sleep(1)