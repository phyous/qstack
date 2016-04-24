from flask import Blueprint, jsonify, request

import os, time, re

from src.app import db
from src.model import Query, Event, Command
from src.util.query_util import QueryUtil
from selenium import webdriver
from slacker import Slacker
from multiprocessing import Process

api = Blueprint('api', __name__)

@api.route('/')
def home():
    return 'Hello Slack!'

@api.route('/api/query/<int:id>', methods=['GET'])
def get_query(id):
    query = db.session.query(Query).get(id)
    db.session.commit()
    
    if query is None:
        return jsonify({'error': 'query not found'}), 404
    
    return jsonify( {'search_results':query.result_list()})

@api.route('/api/qstack')
def get_gist():
    argument = request.args['text']
    command = Command.parse(argument)
    if command == Command.LIST: return list_current_links(request)
    
    stack_overflow_url = retreive_url(command, request)
    
    if stack_overflow_url:
        p = Process(target=process_request_visual, args=(request, stack_overflow_url))
        p.start()
        response_json = {'text': "Retrieving result: {}".format(stack_overflow_url)}
        return jsonify(**response_json) 
    else:
        if command == Command.NEXT:
            response_json = {'text': "No next results found"}
        elif command == Command.QUERY:
            response_json = {'text': "No results found for {}".format(request.args['text'])}
        return jsonify(**response_json)

def list_current_links(req):
    existing_query = Query.find_latest_query(req.args["user_id"],req.args["channel_id"], req.args["team_id"])
    if existing_query:
        link_list = existing_query.result_list()
        response_json = {'text': "The following results were found for query <{}>:\n{}"
            .format(existing_query.query_str, '\n'.join(map(lambda x: str(x), link_list)))}
    else:
        response_json = {'text': "Please make a query before asking for result listing"}

    return jsonify(**response_json)

driver = webdriver.PhantomJS()
driver.set_window_size(1024, 768)
    
def process_request_visual(req, stack_overflow_url):
    token = os.environ['SLACK_TOKEN']  # found at https://api.slack.com/web#authentication
    slack = Slacker(token)

    try:
        filename = "./inbox/stackoverflow_{}.png".format(int(time.time()))
        QueryUtil.extract_image(stack_overflow_url, driver, filename, None)
    except Exception as e:
        reponse = "No results for for query '{}'".format(req.args['text'])
        slack.chat.post_message(request.args['channel_id'], reponse, username="qstack", icon_emoji=":zap:")
        response_json = {'text': reponse}
        return jsonify(**response_json)
    
    ret = slack.files.upload(filename, channels=request.args['channel_id'], filename=filename, title=stack_overflow_url)
    print ret

def retreive_url(command, req):
    if command == Command.NEXT:
        stack_overflow_url = retrieve_next_existing_session(req)
        return stack_overflow_url
    else:
        results = QueryUtil.search_domain("site:www.stackoverflow.com/questions/", req.args['text'], 20)
        regex = re.compile(".*www\.stackoverflow\.com/[Qq]uestions/\d+/")
        results = filter(lambda x: regex.match(x) is not None, results)
        store_new_session(req, results)
        stack_overflow_url = results[0]
        return stack_overflow_url

def store_new_session(req, search_results):
    event = Event(Command.QUERY, 0, 1)
    query = Query(req.args["user_id"],req.args["channel_id"], req.args["team_id"], req.args["text"], search_results)
    query.events = [event]
    db.session.add(query)
    db.session.commit()
    return

def retrieve_next_existing_session(req):
    existing_query = Query.find_latest_query(req.args["user_id"],req.args["channel_id"], req.args["team_id"])
    if existing_query:
        next_result = Event.get_next_result(existing_query)
        if next_result:
            if next_result < len(existing_query.result_list()):
                event = Event(Command.QUERY, next_result, next_result+1)
            else:
                event = Event(Command.QUERY, next_result, next_result)
            existing_query.events.append(event)
            db.session.commit()
            return existing_query.result_list()[next_result]
    return None