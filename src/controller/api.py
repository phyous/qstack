from flask import Blueprint, jsonify, request

import os, time

from src.util.query_util import QueryUtil
from selenium import webdriver
from PIL import Image
from slacker import Slacker
import StringIO
import base64

api = Blueprint('api', __name__)


@api.route('/')
def home():
    return 'Hello Slack!'

driver = webdriver.PhantomJS()
driver.set_window_size(1024, 768)

@api.route('/api/qstack')
def get_gist():
    print request.args
    search_query = request.args['text']
    results = QueryUtil.search_domain("stackoverflow.com/questions", search_query, 1)
    stack_overflow_url = results[0]
    print stack_overflow_url
    
    token = os.environ['SLACK_TOKEN']  # found at https://api.slack.com/web#authentication
    slack = Slacker(token)

    try:
        filename = "./inbox/stackoverflow_{}.png".format(int(time.time()))
        QueryUtil.extract_image(stack_overflow_url, driver, filename, None)
    except Exception as e:
        reponse = "No results for for query '{}'".format(search_query)
        slack.chat.post_message(request.args['channel_id'], reponse)
        response_json = {'text': reponse}
        return jsonify(**response_json)
    
    ret = slack.files.upload(filename, channels=request.args['channel_id'], filename=filename, title=stack_overflow_url)
    print ret

    response_json = {'text': stack_overflow_url}
    return jsonify(**response_json)
