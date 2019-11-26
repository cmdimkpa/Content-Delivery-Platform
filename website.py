from flask import Flask,Response,render_template
from flask_cors import CORS
import requests as http
import json

app = Flask(__name__)
CORS(app)

global BASE_HTML

BASE_HTML = """

<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <meta charset="utf-8">
    <title>AXA Current State Architecture</title>
    <link rel="stylesheet" type="text/css" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.js" charset="utf-8"></script>
  </head>
  <body>
    __NAVBAR__
  </body>
</html>

"""

def responsify(status,message,data={}):
    code = int(status)
    a_dict = {"data":data,"message":message,"code":code}
    try:
        return Response(json.dumps(a_dict), status=code, mimetype='application/json')
    except:
        return Response(str(a_dict), status=code, mimetype='application/json')

@app.route("/filehosting/get-file/<path:filename>")
def get_file(filename):
    try:
        return app.send_static_file(filename)
    except:
        return "<h1> Error Serving File: %s <h1>" % filename

def build_navbar():
    url = "http://3.130.5.83:9271/ods/fetch_records"
    payload = {
    	"tablename":"ContentModel",
    	"constraints":{}
    }
    HEADERS = {"Content-Type":"application/json"}
    data = http.post(url,json.dumps(payload),headers=HEADERS).json()["data"]
    BASE_NAV = """

    """
    return BASE_NAV

def build_html():
    global BASE_HTML
    BASE_HTML = BASE_HTML.replace("__NAVBAR__",build_navbar())
    return BASE_HTML

def new_site(html):
    homepage = "/home/ubuntu/website/templates/site.html"
    p = open(homepage,"wb+"); p.write(html); p.close()
    return None

@app.route("/AXA-current-state-architecture")
def load_website():
    new_site(build_html())
    return render_template("site.html")

if __name__ == "__main__":
  app.run(host="172.31.29.36",port=2357,threaded=True)
