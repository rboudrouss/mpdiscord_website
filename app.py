from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from json import loads, dumps
from requests_oauthlib import OAuth2Session
import os
from secret_client_key import client_secret #! change before deploy

#TODO code admin interface
#TODO convert "assert" to if not x : raise error
#TODO code visual (css) => wanna une ampoule go on off
#TODO eviter de donner l'email aussi dans le accounts
#TODO 
#? do we really need the email?
#? sql library 

# Disable SSL requirement
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Settings for your app
base_discord_api_url = 'https://discordapp.com/api'
client_id = r'742766849783103539' 
client_secret = client_secret #! change before deploy
scope = ['identify', 'email']
token_url = 'https://discordapp.com/api/oauth2/token'
authorize_url = 'https://discordapp.com/api/oauth2/authorize'



# flask app
app = Flask(__name__)
app.secret_key= os.urandom(24)


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

@app.route('/login')
def login():
    redirect_uri= request.url_root+'oauth_callback'
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    login_url, state = oauth.authorization_url(authorize_url)
    session['state'] = state
    return redirect(login_url)

@app.route("/oauth_callback")
def oauth_callback():
    redirect_uri= request.url_root+'oauth_callback'
    discord = OAuth2Session(client_id, redirect_uri=redirect_uri, state=session['state'], scope=scope)
    token = discord.fetch_token(
        token_url,
        client_secret=client_secret,
        authorization_response=request.url,
    )
    session['discord_token'] = token
    return redirect(url_for('registering'))

@app.route("/registering")
def registering():
    discord = OAuth2Session(client_id, token=session['discord_token'])
    response = discord.get(base_discord_api_url + '/users/@me')
    infos = response.json()
    
    session['id']=infos['id']
    accounts = read_accounts()
    if not infos['id'] in accounts:
        accounts[infos['id']]={
            'username':infos['username'],
            'discriminator':infos['discriminator'],
            'avatar':infos['avatar'],
            'email':infos['email']
        }
        assert write_accounts(accounts)
    
        users = read_users()
        users[session['id']]=True
        assert write_users(users)
    
    flash(u'logged in successfuly !','success')
    return redirect(url_for('home'))

@app.route('/admin')
def admin():
    return "admin"

@app.route('/u/<user>')
def user(user):
    if 'id' in session:
        print('session id',session['id'], user)
        if user == session['id']:
            return redirect(url_for('mymps'))
    else:
        users = read_users()
        accounts = read_accounts()
        open_mp = users.get(user,"404")
        if open_mp=='404':
            abort(404)
        return render_template(
            "users.html",
            open_mp=open_mp,
            user=user,
            accounts=accounts
        )

@app.route('/userlist')
def userlist():
    users = read_users()
    accounts = read_accounts()
    return render_template(
        "userlist.html",
        users=users,
        accounts=accounts
    )

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
    session.pop('discord_token',None)
    flash(u'logged out successfuly !','success')
    return redirect(url_for("home"))

# 404 error
@app.errorhandler(404)
def page_not_found(error):
    return "404", 404


# Run
if __name__ == '__main__':
    app.run(
        debug=True
    )
