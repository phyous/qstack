import sys
from src.scraper.xgoogle.search import GoogleSearch, SearchError
from selenium import webdriver
from PIL import Image
import StringIO
import base64

def main():
    search_query = ' '.join(sys.argv[1:])
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
    element = driver.find_element_by_id('answers')
    location = element.location
    size = element.size
    
    im = Image.open(StringIO.StringIO(base64.decodestring(driver.get_screenshot_as_base64())))
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    
    
    im = im.crop((left, top, right, bottom)) # defines crop points
    im.save('stackoverflow.png') # saves new cropped image

if __name__ == '__main__':
    main()