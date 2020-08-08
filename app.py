from flask import Flask, render_template,request,redirect,url_for
from json import loads,dumps
app = Flask(__name__)
IDUSER = ""

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/on')
def on():
    return render_template("useron.html")

@app.route('/off')
def off():
    return render_template("useroff.html")

@app.route('/admin')
def admin():
    return "admin"

@app.route('/login', methods=['POST','GET'])
def login():
    global IDUSER
    if request.method == "POST":
        mail=request.form["mail"]
        pwd=request.form["password"]
        with open("./static/data/accounts.json",'r') as f:
            accounts = loads(f.read())
            if accounts.get(mail,False):
                if accounts[mail]["password"] == pwd:
                    IDUSER = accounts[mail]["id"]
                    print("logged in as", IDUSER)
                    return redirect(url_for('mymps'))
                else:
                    print("wrong password")
            else:
                print("wrong email")
    return render_template("login.html")

@app.route('/register',methods=["POST","GET"])
def register():
    global IDUSER
    if request.method == "POST":
        mail=request.form["mail"]
        pwd=request.form["password"]
        id_d = request.form["id"]
        with open("./static/data/accounts.json",'r') as f:
            accounts = loads(f.read())
        accounts[mail]={
            "id":id_d,
            "password": pwd
        }
        with open("./static/data/accounts.json",'w') as f:
            f.write(dumps(accounts,sort_keys=True, indent=4))
        return redirect(url_for("home"))
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

@app.route('/mymps',methods=["POST","GET"])
def mymps():
    if not IDUSER:
        with open("./static/data/users.json",'r') as f:
            users = loads(f.read())
            mps_statu = users[IDUSER]
        if request.method == "POST":
            with open("./static/data/users.json",'r') as f:
                users = loads(f.read())
            users[IDUSER] = "on" if users[IDUSER] == "off" else "off"
            with open("./static/data/users.json",'w') as f:
                f.write(dumps(users,sort_keys=True, indent=4))
        return render_template("mymps.html", mp = mps_statu)
    else:
        return redirect(url_for("login"))

@app.errorhandler(404)
def page_not_found(error):
    return "404", 404

if __name__ == '__main__':
    app.run(debug=True)