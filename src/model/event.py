import datetime
from src.app import db
from sqlalchemy import text, desc

class Event(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.Integer, default=datetime.datetime.utcnow, index=True)
    type = db.Column(db.String(32), nullable=False)
    query = db.Column(db.Integer, db.ForeignKey('query.id'))
    current_result_idx = db.Column(db.Integer)
    next_result_idx = db.Column(db.Integer)

    def __init__(self, type, current_result_idx, next_result_idx):
        self.type = type
        self.current_result_idx = current_result_idx
        self.next_result_idx = next_result_idx

    def __repr__(self):
        return "type:{}, query:{}, current_result_idx:{}, next_result_idx:{}" \
            .format(self.type, self.query, self.current_result_idx, self.next_result_idx)
    
    @staticmethod
    def get_next_result(query):
        sql = text('SELECT next_result_idx FROM event WHERE query = {} order by id desc limit 1;'.format(query.id))
        result = [i for i in db.engine.execute(sql)]
        if result and len(result) > 0:
            return result[0][0]
        else:
            return None