from src.scraper.xgoogle.search import GoogleSearch, SearchError
from PIL import Image
import StringIO
import base64

class QueryUtil:
    
    @staticmethod
    def search_domain(domain, search_query, num_results):
        try:
            gs = GoogleSearch("{}: {}".format(domain, search_query))
            gs.results_per_page = num_results
            results = gs.get_results()
            return [res.url.encode("utf8") for res in results]
        except SearchError, e:
            print "Search failed: %s" % e
            return []
    
    @staticmethod
    def extract_image(url, driver, output_file, selector_callback):
        driver.get(url)
        element = driver.find_element_by_class_name('answer')
        location = element.location
        size = element.size
    
        im = Image.open(StringIO.StringIO(base64.decodestring(driver.get_screenshot_as_base64())))
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
    
        im = im.crop((left, top, right, bottom))  # defines crop points
        im.save(output_file)  # saves new cropped image