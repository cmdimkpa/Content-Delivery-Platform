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

@app.route("/AXA-current-state-architecture")
def load_website():
    return render_template("site.html")

if __name__ == "__main__":
  app.run(host="172.31.33.45",port=2357,threaded=True)
