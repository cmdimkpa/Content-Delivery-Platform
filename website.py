from flask import Flask,Response,render_template,request,redirect
from flask_cors import CORS
import requests as http
import json,time,subprocess,os,base64
from boto.s3.connection import S3Connection
from boto.s3.key import Key

app = Flask(__name__)
CORS(app)

here = os.getcwd()
if "\\" in here:
    slash = "\\"
else:
    slash = "/"
here+=slash

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

comps = map(lambda x:x.split(":")[-1],run_shell("cat /home/ubuntu/S3AppDatabase.config").split("\r\n"))[:-1]
conn = S3Connection(comps[0], comps[-1], host="s3.%s.amazonaws.com" % comps[1])
try:
    bucket = conn.create_bucket(comps[2])
except:
    bucket = conn.get_bucket(comps[2])

def newS3FileURL(keyname,stringdata):
    key = Key(bucket); key.key = keyname; key.content_type = 'text/html'; key.set_contents_from_string(stringdata)
    return "https://content-delivery-platform.s3.us-east-2.amazonaws.com/%s" % keyname

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

def build_components():
    global NAVBAR, PDF_LIST
    NAVBAR = ""; PDF_LIST = ""
    def add_entry(entry):
        global NAVBAR, PDF_LIST
        title = entry["unit"]; url = entry["url"]; pdf = entry["pdf"]
        NAVBAR+='<li class="list-group-item list-group-item-action bg-light" onclick="loadPage(`%s`)">%s</li>' % ("%s,%s"%(url,title),title)
        if not pdf:
            pdf = get_url_pdf(url)
            hit = "http://3.130.5.83:9271/ods/update_records"
            payload = {
            	"tablename":"ContentModel",
            	"constraints":{
                    "ContentModel_id":entry["ContentModel_id"]
                },
                "data":{
                    "pdf":pdf
                }
            }
            HEADERS = {"Content-Type":"application/json"}
            response = http.post(hit,json.dumps(payload),headers=HEADERS)
        PDF_LIST+="%s,%s|"%(title,pdf)
        return None
    hit = "http://3.130.5.83:9271/ods/fetch_records"
    payload = {
    	"tablename":"ContentModel",
    	"constraints":{}
    }
    HEADERS = {"Content-Type":"application/json"}
    data = http.post(hit,json.dumps(payload),headers=HEADERS).json()["data"]
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
    try:
        NAVBAR,ACTIVE_LABEL,PDF_LIST = build_components()
        return render_template("index.html",NAVBAR=NAVBAR,ACTIVE_LABEL=ACTIVE_LABEL,PDF_LIST=PDF_LIST)
    except:
        return "<h1>404: No pages found, add a page to view</h1>"

@app.route("/AXA-current-state-architecture/add-content",methods=["POST"])
def add_content():
    formdata = request.get_json(force=True)
    required = ["b64"]; missing = [x for x in required if x not in formdata]
    if missing:
        return responsify(404,"Not Found: these parameters are missing %s" % missing)
    return responsify(200,newS3FileURL("%s.html"%seed(),base64.b64decode(formdata["b64"])))

@app.route("/AXA-current-state-architecture/add-page")
def new_page():
    args = dict(request.args)
    required = ["title","url"]; missing = [x for x in required if x not in args]
    if missing:
        return responsify(404,"Not Found: these parameters are missing %s" % missing)
    try:
        title = args["title"][0]; url = args["url"][0]
        hit = "http://3.130.5.83:9271/ods/new_record"
        payload = {
            	"tablename":"ContentModel",
            	"data":{
            		"unit":title,
            		"url":url,
                    "pdf":""
            	}
            }
        HEADERS = {"Content-Type":"application/json"}
        response = http.post(hit,json.dumps(payload),headers=HEADERS)
        task = build_components()
        return redirect("http://ec2-3-130-5-83.us-east-2.compute.amazonaws.com/AXA-current-state-architecture",302)
    except Exception as error:
        return responsify(400,"Error: %s" % str(error))

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

if __name__ == "__main__":
  app.run(host="172.31.29.36",port=2357,threaded=True)
