from flask import Flask,Response,render_template
from flask_cors import CORS
import requests as http
import json,time,subprocess,os

app = Flask(__name__)
CORS(app)

here = os.getcwd()
if "\\" in here:
    slash = "\\"
else:
    slash = "/"
here+=slash

def responsify(status,message,data={}):
    code = int(status)
    a_dict = {"data":data,"message":message,"code":code}
    try:
        return Response(json.dumps(a_dict), status=code, mimetype='application/json')
    except:
        return Response(str(a_dict), status=code, mimetype='application/json')

def run_shell(cmd):
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  out, err = p.communicate()
  if err:
      return err
  else:
      try:
          return eval(out)
      except:
          return out

@app.route("/filehosting/get-file/<path:filename>")
def get_file(filename):
    try:
        return app.send_static_file(filename)
    except:
        return "<h1> Error Serving File: %s <h1>" % filename

def build_components():
    global NAVBAR, PDF_LIST
    NAVBAR = ""; PDF_LIST = ""
    def add_entry(entry):
        global NAVBAR, PDF_LIST
        title = entry["unit"]; url = entry["url"]
        NAVBAR+='<li class="list-group-item list-group-item-action bg-light" onclick="loadPage(`%s`)">%s</li>' % ("%s,%s"%(url,title),title)
        PDF_LIST+="%s,%s|"%(title,get_url_pdf(url))
        return None
    url = "http://3.130.5.83:9271/ods/fetch_records"
    payload = {
    	"tablename":"ContentModel",
    	"constraints":{}
    }
    HEADERS = {"Content-Type":"application/json"}
    data = http.post(url,json.dumps(payload),headers=HEADERS).json()["data"]
    build = map(add_entry,data)
    return NAVBAR,data[0]["unit"],PDF_LIST

def seed():
    return int(time.time())

def get_url_pdf(url):
    essential_name = "%s.pdf" % seed()
    fname = here+"static%s%s" % (slash,essential_name)
    cmd = "sudo google-chrome-stable --no-sandbox --headless --disable-gpu --print-to-pdf=%s %s" % (fname,url)
    run_shell(cmd)
    return "http://ec2-3-130-5-83.us-east-2.compute.amazonaws.com/filehosting/get-file/%s" % essential_name

@app.route("/AXA-current-state-architecture")
def load_website():
    NAVBAR,ACTIVE_LABEL,PDF_LIST = build_components()
    return render_template("index.html",NAVBAR=NAVBAR,ACTIVE_LABEL=ACTIVE_LABEL,PDF_LIST=PDF_LIST)

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

if __name__ == "__main__":
  app.run(host="172.31.29.36",port=2357,threaded=True)
