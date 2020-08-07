from flask import Flask, render_template
from json import loads
app = Flask(__name__)
IDUSER = "anonymous"

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/on')
def on():
    return render_template("useron.html")

@app.route('/off')
def off():
    return render_template("useroff.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/u/<user>')
def user(user):
    with open("./static/data/users.json",'r') as f:
        users = loads(f.read())
        open_mp = users.get(user,"Not a user")
        if open_mp == "on":
            return render_template("useron.html",user=user)
        elif open_mp == "off":
            return render_template("useroff.html",user=user)
        else:
            return render_template("usernone.html", user=user)
    return open_mp

@app.route('/userlist')
def userlist():
    with open("./static/data/users.json",'r') as f:
        users = loads(f.read())
        return render_template("userlist.html",users=users)


if __name__ == '__main__':
    app.run(debug=True)