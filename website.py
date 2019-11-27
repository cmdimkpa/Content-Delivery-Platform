from flask import Flask,Response,render_template
from flask_cors import CORS
import requests as http
import json

app = Flask(__name__)
CORS(app)

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
    global NAVBAR
    NAVBAR = ""
    def add_entry(entry):
        global NAVBAR
        title = entry["unit"]; url = entry["url"]
        NAVBAR+='<li class="list-group-item list-group-item-action bg-light" onclick="loadPage(`%s`)">%s</li>' % ("%s,%s"%(url,title),title)
        return None
    url = "http://3.130.5.83:9271/ods/fetch_records"
    payload = {
    	"tablename":"ContentModel",
    	"constraints":{}
    }
    HEADERS = {"Content-Type":"application/json"}
    data = http.post(url,json.dumps(payload),headers=HEADERS).json()["data"]
    build = map(add_entry,data)
    return NAVBAR,data[0]["unit"]

@app.route("/AXA-current-state-architecture")
def load_website():
    NAVBAR,ACTIVE_LABEL = build_navbar()
    return render_template("index.html",NAVBAR=NAVBAR,ACTIVE_LABEL=ACTIVE_LABEL)

if __name__ == "__main__":
  app.run(host="172.31.29.36",port=2357,threaded=True)
