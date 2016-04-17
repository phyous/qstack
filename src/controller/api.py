from flask import Blueprint, jsonify, request

import os, time

from src.util.query_util import QueryUtil
from selenium import webdriver
from slacker import Slacker
from multiprocessing import Process

api = Blueprint('api', __name__)


@api.route('/')
def home():
    return 'Hello Slack!'


@api.route('/api/qstack')
def get_gist():
    p = Process(target=process_request_visual, args=(request,))
    p.start()
    response_json = {'text': "processing request"}
    return jsonify(**response_json)

driver = webdriver.PhantomJS()
driver.set_window_size(1024, 768)
    
def process_request_visual(req):
    print req.args
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
        slack.chat.post_message(request.args['channel_id'], reponse, username="qstack", icon_emoji=":zap:")
        response_json = {'text': reponse}
        return jsonify(**response_json)
    
    ret = slack.files.upload(filename, channels=request.args['channel_id'], filename=filename, title=stack_overflow_url)
    print ret
