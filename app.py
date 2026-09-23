import os, secrets
from urllib.parse import urlencode
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for, send_from_directory, flash
from riot_api import RiotAPI, RiotAPIError
from stats import build_dashboard
load_dotenv()
app=Flask(__name__); app.secret_key=os.getenv('FLASK_SECRET_KEY',secrets.token_hex(32))
CLIENT_ID=os.getenv('RIOT_CLIENT_ID',''); REDIRECT_URI=os.getenv('RIOT_REDIRECT_URI','http://127.0.0.1:5000/oauth/callback'); REGION=os.getenv('RIOT_REGION','europe')
riot=RiotAPI(CLIENT_ID,os.getenv('RIOT_CLIENT_SECRET',''),REDIRECT_URI,REGION)
@app.after_request
def headers(r):
    r.headers['X-Content-Type-Options']='nosniff'; r.headers['X-Frame-Options']='SAMEORIGIN'; r.headers['Referrer-Policy']='strict-origin-when-cross-origin'; return r
@app.get('/')
def index(): return render_template('index.html',logged_in=bool(session.get('access_token')))
@app.get('/riot.txt')
def riot_txt(): return send_from_directory(app.root_path,'riot.txt',mimetype='text/plain')
@app.get('/health')
def health(): return {'status':'ok'}
@app.get('/login')
def login():
    if not CLIENT_ID: flash('RIOT_CLIENT_ID не настроен.'); return redirect(url_for('index'))
    state=secrets.token_urlsafe(32); session['oauth_state']=state
    q=urlencode({'client_id':CLIENT_ID,'redirect_uri':REDIRECT_URI,'response_type':'code','scope':'openid offline_access','state':state})
    return redirect('https://auth.riotgames.com/authorize?'+q)
@app.get('/oauth/callback')
def callback():
    if request.args.get('error'): flash('Riot Sign On: '+request.args.get('error_description',request.args['error'])); return redirect(url_for('index'))
    code=request.args.get('code'); state=request.args.get('state'); expected=session.pop('oauth_state',None)
    if not code: flash('Riot не вернул authorization code.'); return redirect(url_for('index'))
    if not expected or not state or not secrets.compare_digest(expected,state): flash('Ошибка OAuth state.'); return redirect(url_for('index'))
    try:
        t=riot.exchange_code(code); session['access_token']=t['access_token']; session['refresh_token']=t.get('refresh_token'); session['account']=riot.get_account(t['access_token']); return redirect(url_for('profile'))
    except RiotAPIError as e: flash(f'Ошибка Riot API: {e}'); return redirect(url_for('index'))
@app.get('/profile')
def profile():
    token=session.get('access_token')
    if not token: return redirect(url_for('login'))
    try:
        account=session.get('account') or riot.get_account(token); session['account']=account
        return render_template('profile.html',account=account,data=build_dashboard(riot,token,account['puuid']))
    except RiotAPIError as e:
        rt=session.get('refresh_token')
        if rt:
            try:
                t=riot.refresh_access_token(rt); session['access_token']=t['access_token']; session['refresh_token']=t.get('refresh_token',rt); account=riot.get_account(t['access_token']); session['account']=account
                return render_template('profile.html',account=account,data=build_dashboard(riot,t['access_token'],account['puuid']))
            except RiotAPIError: pass
        session.clear(); flash(f'Сессия Riot недействительна: {e}'); return redirect(url_for('index'))
@app.get('/logout')
def logout(): session.clear(); return redirect(url_for('index'))
if __name__=='__main__': app.run(host='127.0.0.1',port=5000,debug=True)
