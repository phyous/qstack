import sys
from src.scraper.xgoogle.search import GoogleSearch, SearchError
from src.scraper.xoverflow import Xoverflow
from src.rendering.webkit2png import WebkitRenderer
from src.rendering.scripts import init_qtgui

from PyQt4.QtCore import QTimer
from PyQt4.QtWebKit import QWebSettings

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
    res = stack_overflow_url
    
    def renderer_func():
        renderer = WebkitRenderer()
        renderer.width = 800
        renderer.height = 600
        renderer.timeout = 10
        renderer.wait = 1
        renderer.format = "png"
        renderer.grabWholeWindow = False
        renderer.renderTransparentBackground = False
        renderer.qWebSettings[QWebSettings.JavascriptEnabled] = True
    
        outfile = open("stackoverflow.png", "w")
        renderer.render_to_file(res, outfile)
        outfile.close()

    app = init_qtgui()
    QTimer.singleShot(0, renderer_func)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()