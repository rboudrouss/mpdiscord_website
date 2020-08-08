from flask import Flask, render_template, request, redirect, url_for, session, flash
from json import loads,  dumps
app = Flask(__name__)
app.secret_key="not my actual secret key :p" # TODO find a better secret key
# TODO account modification & compress useron,useroff,usernone.html in one file
# TODO code admin interface


# fonctions
def write_users(users):
    with open("./data/users.json",'w') as f:
        f.write(dumps(users,sort_keys=True, indent=4))
    return True

def read_users():
    with open("./data/users.json",'r') as f:
        accounts = loads(f.read())
    return accounts

def write_accounts(accounts):
    with open("./data/accounts.json",'w') as f:
        f.write(dumps(accounts,sort_keys=True, indent=4))
    return True

def read_accounts():
    with open("./data/accounts.json",'r') as f:
        accounts = loads(f.read())
    return accounts

# web app
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
    if 'id' in session:
        flash("already logged")
        return redirect(url_for('mymps'))
    else:
        if request.method == "POST":
            
            # information requests
            mail=request.form["mail"]
            pwd=request.form["password"]
            
            # get accounts
            accounts = read_accounts()
            
            # login teatement
            if accounts.get(mail,False):
                if accounts[mail]["password"] == pwd:
                    session["id"] = accounts[mail]["id"]
                    print("logged in as", session["id"])
                    flash("successfully logged")
                    return redirect(url_for('mymps'))
                else:
                    flash('wrong password')
                    print("wrong password")
            else:
                flash('wrong email')
                print("wrong email")
        # return to login page in case of error or first visit
        return render_template("login.html")

@app.route('/register',methods=["POST","GET"])
def register():
    # global IDUSER
    if 'id' in session:
        flash("already logged")
        return redirect(url_for('mymps'))
    else:
        if request.method == "POST":
            
            # request informations
            mail=request.form["mail"]
            pwd=request.form["password"]
            id_d = request.form["id"]
            
            # create a new account
            accounts = read_accounts()
            accounts[mail]={
                "id":id_d,
                "password": pwd
            }
            assert write_accounts(accounts)
            
            # Create a new user
            users = read_users()
            users[id_d]="on"
            assert write_users(users)
            
            # return to home if successufuly registered
            flash('successfully registred')
            return redirect(url_for("home"))
        # return to register if first visit
        return render_template("register.html")

@app.route('/u/<user>')
def user(user):
    users = read_users()
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
    users = read_users()
    return render_template("userlist.html",users=users)

@app.route('/mymps',methods=["POST","GET"])
def mymps():
    if 'id' in session:
        users = read_users()
        if request.method == "POST":
            users[session["id"]] = "on" if users[session["id"]] == "off" else "off"
            assert write_users(users)
        return render_template("mymps.html", mp = users[session["id"]])
    else:
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    session.pop('id',None)
    return redirect(url_for("home"))

@app.route('/account')
def account():
    return redirect(url_for("home"))


@app.errorhandler(404)
def page_not_found(error):
    return "404", 404

if __name__ == '__main__':
    app.run(debug=True)