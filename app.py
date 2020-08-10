from flask import Flask, render_template, request, redirect, url_for, session, flash
from json import loads, dumps


#TODO find a better secret key
#TODO add discord connection Authme2
#TODO code admin interface
#TODO convert "assert" to if not x : raise error
#TODO add temporary padding for h2 in users
#TODO code visual (css) => wanna une ampoule go on of
#? sql library 


app = Flask(__name__)
app.secret_key="not my actual secret key :p"


# fonctions

def register_method():
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
    
    # connect user
    session['id']=id_d
    session['mail']=mail
    # return to home if successufuly registered
    return True

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
                    session["mail"] = mail
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
        if request.method == "POST":
            return redirect(url_for('home')) #? maybe
        flash("already logged")
        return redirect(url_for('mymps'))
    else:
        if request.method == "POST":
            
            if register_method():
                # return to home if successufuly registered
                flash('successfully registred')
                return redirect(url_for("home"))
            else:
                print("Error")
                flash("Try again")
        # return to register if first visit
        return render_template("register.html")

@app.route('/u/<user>')
def user(user):
    if user == session['id']:
        return redirect(url_for('mymps'))
    else:
        users = read_users()
        open_mp = users.get(user,"404")
        return render_template(
            "users.html",
            open_mp=open_mp,
            user=user
        )
        # if open_mp == "404":
        #     return render_template("usernone.html", user=user)
        # elif open_mp:
        #     return render_template("useron.html",user=user)
        # elif not open_mp:
        #     return render_template("useroff.html",user=user)
        # else:
        #     print("not possible")

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
    session.pop('mail',None)
    return redirect(url_for("home"))

@app.route('/account',methods=["POST","GET"])
def account():
    if request.method == "POST":
        
        # delete old informations
        accounts = read_accounts()
        accounts.pop(session['mail'],None)
        assert write_accounts(accounts)
        
        users = read_users()
        users.pop(session['id'],None)
        assert write_users(users)
        
        # write new information
        if register_method():
            flash("information successfuly updated")
            return redirect(url_for('home'))
    else :
        if 'id' in session:
            accounts = read_accounts()
            user_infos = accounts[session["mail"]]
            pwd = user_infos['password']
            id_user = user_infos['id']
            return render_template(
                "account.html",
                mail = session["mail"],
                pwd = pwd,
                id_user = id_user
            )
        else :
            flash("not connected")
            return redirect(url_for("login"))


# 404 error
@app.errorhandler(404)
def page_not_found(error):
    return "404", 404


# Run
if __name__ == '__main__':
    app.run(
        debug=True
    )
