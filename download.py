### This scripts objective is given a url (https://www.wco.tv/anime/braceface), to create a folder (braceface) and download every episode. 
### This relies on selenium to fetch each download url. 

""" Be sure to download ChromeDriver from https://chromedriver.storage.googleapis.com/index.html?path=2.44/ and put in PATH """
import os
import shutil
import sys


from datetime import datetime
import requests

import os # File I/O
import time
import shutil
import glob

import util
from selenium.common.exceptions import TimeoutException

if len(sys.argv) < 2:
    print('Please supply url to download')
    sys.exit()

class Download(object):
    url = ''
    name = ''
    extension = ''
    def __init__(self):
        pass

def get_dir_name(base_url):
    tokens = base_url.split('/')
    return tokens[len(tokens)-1]

import urllib
def download_file(url, filename): # TODO: Replace with faster download. This streams the file, i want to save-as download
    # NOTE the stream=True parameter
    urllib.urlretrieve(url, filename)
    """ r = requests.get(url, stream=True)
    with open(os.path.join(full_dir_path, filename), 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return os.path.join(full_dir_path, filename) """

def get_html(url):
    print('Fetching {0}'.format(url))
    req = requests.get(url)

    return req.content

def extract_episode_urls(driver):
    """ Return a list of url, title sets """
    print('Extracting urls')
    urls = []
    elems = util.verify_elems(driver, '.cat-eps>a')
    for elem in elems:
        url = elem.get_attribute('href')
        title = url.split('/')[len(url.split('/'))-1]
        print(title)
        urls.append((title, url))
    return urls

def extract_direct_video_urls(driver, urls):
    """ Given a list of tuples (title, url), return a list of tuples with updated url 
        for direct video url"""
    vid_urls = []
    for url in urls:
        util.get_url(driver, url[1])
        
        frames = util.verify_elems(driver, 'iframe')
        frame_ids = []
        for frame in frames:
            frame_ids.append(frame.get_attribute('id'))

        print('ids: {0}'.format(frame_ids))
        for frame_id in frame_ids:
            #print('Switching to iframe: {0}'.format(frame.get_attribute('id')))
            util.switch_to_frame(driver, frame_id)
            try:
                elem = util.verify_elem(driver, 'video[id="video-js_html5_api"]', 1)
                print('Video found')
                elem = util.verify_elem(driver, 'source')
                vid_url = elem.get_attribute('src')
                print('vid url: {0}'.format(vid_url))
                vid_urls.append((url[0], vid_url, elem.get_attribute('type').split('/')[1]))
                break
            except TimeoutException:
                driver.switch_to.default_content()
   
    return vid_urls

base_url = sys.argv[1]
dir_name = get_dir_name(base_url)
full_dir_path = os.path.join(os.getcwd(), dir_name)

# Check if this folder exists
if not os.path.isdir(full_dir_path):
    os.mkdir(full_dir_path)

# Fetch all existing filenames so we can reduce # of fetches to website
existing_file_titles = []
for root, dir, files in os.walk(full_dir_path, topdown=True):
    tokens = files.split('.')
    filename = ''.join(tokens[:len(tokens)-1])
    existing_file_titles.append(filename)

print('Existing files: {0}'.format(existing_file_titles))

driver = util.init_chrome(full_dir_path)
util.get_url(driver, base_url)
urls = extract_episode_urls(driver)

# With urls to the individual video pages, we now use them to get direct video urls
direct_urls = extract_direct_video_urls(driver, urls)


driver.quit()

for url in direct_urls:
    filename = url[0] + '.' + url[2]
    fullpath = os.path.join(full_dir_path, filename)
    if (os.path.isfile(fullpath)):
        print('{0} already exists. Skipping'.format(filename))
    else:
        print('Downloading {0}'.format(filename))
        download_file(url[1], fullpath)
