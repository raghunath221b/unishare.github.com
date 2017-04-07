from flask import Flask,render_template,request,redirect,url_for
import MySQLdb

app = Flask(__name__)

conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "",
                           db = "login_data")
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
