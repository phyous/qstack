from flask import Flask
from flask.ext.testing import TestCase
from src.controller import api


class TestInitViews(TestCase):

    render_templates = False

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True

        app.register_blueprint(api.api)

        return app

    def test_root_route(self):
        res = self.client.get('/')
        print res