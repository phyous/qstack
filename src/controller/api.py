from flask import Blueprint, jsonify, request

import sys,os,time
from src.scraper.xgoogle.search import GoogleSearch, SearchError
from selenium import webdriver
from PIL import Image
from slacker import Slacker
import StringIO
import base64

api = Blueprint('api', __name__)

@api.route('/')
def home():
    return 'Hello Slack!'

@api.route('/api/qstack')
def get_gist():
    print request.args
    search_query = ' '.join(request.args['text'])
    stack_overflow_url = None
    try:
        gs = GoogleSearch("stackoverflow.com: {}".format(search_query))
        gs.results_per_page = 1
        results = gs.get_results()
        stack_overflow_url = [res.url.encode("utf8") for res in results][0]
    except SearchError, e:
        print "Search failed: %s" % e
    
    print stack_overflow_url
    
    driver = webdriver.PhantomJS() # or add to your PATH
    driver.set_window_size(1024, 768) # optional
    driver.get(stack_overflow_url)
    element = driver.find_element_by_class_name('answer')
    location = element.location
    size = element.size
    
    im = Image.open(StringIO.StringIO(base64.decodestring(driver.get_screenshot_as_base64())))
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    
    im = im.crop((left, top, right, bottom)) # defines crop points
    filename = "./inbox/stackoverflow_{}.png".format(int(time.time()))
    im.save(filename) # saves new cropped image
    
    token = os.environ['SLACK_TOKEN']      # found at https://api.slack.com/web#authentication
    slack = Slacker(token)
    ret = slack.files.upload(filename, channels=request.args['channel_id'], filename=filename, title=stack_overflow_url)
    print ret

    response_json = {'text':stack_overflow_url}
    return jsonify(**response_json)