import requests
from bs4 import BeautifulSoup

class Xoverflow:
    
    def __init__(self, url):
        self.url = url

    def parse_result(self):
        html_content = requests.get(self.url).content
        self.document = BeautifulSoup(html_content, "html.parser")      
        return self.document 
        
    def get_results(self):
        return str(self.parse_result().body)
