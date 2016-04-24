import datetime
import json
from sqlalchemy import desc

from src.app import db

class Query(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.Integer, default=datetime.datetime.utcnow, index=True) 
    user_id = db.Column(db.String(128), index=True, nullable=False)
    channel_id = db.Column(db.String(128), index=True)
    app_id = db.Column(db.String(128), index=True, nullable=False)
    query_str = db.Column(db.Text, nullable=False)
    search_results = db.Column(db.Text, nullable=False)
    num_search_results = db.Column(db.Integer, nullable=False)
    events = db.relationship('Event',  backref='event', lazy='joined')
    
    
    def __init__(self, user_id, channel_id, app_id, query_str, search_results, events=None):
        self.user_id = user_id
        self.channel_id = channel_id
        self.app_id = app_id
        self.query_str = query_str
        self.search_results = json.dumps(search_results) 
        self.num_search_results = len(search_results)
        self.events = [] if events is None else events 
    
    def __repr__(self):
        return "id:{}, user_id:{}, channel_id:{}, app_id:{}, query_str:{}, #results:{}"\
            .format(self.id, self.user_id, self.channel_id, self.app_id, self.query_str[:20] + "...", self.num_search_results)

    def result_list(self):
        return json.loads(self.search_results)
    
    @staticmethod
    def find_latest_query(user_id, channel_id, app_id):
        return Query.query.filter_by(user_id=user_id, channel_id=channel_id, app_id=app_id).order_by(desc(Query.id)).first()
        