from __init__ import login_manager
from flask import render_template, request, redirect, url_for, g, session
from flask_login import login_required, logout_user, login_user, current_user
from sso.sso_login import SSO_User
from main_app import app, log
from app_config import *
from gfss_parameter import public_name, debug
from util.ip_addr import ip_addr
from os import environ
import requests 
import json


@login_manager.user_loader
def loader_user(id_user):
    log.debug(f"LM. Loader ID User: {id_user}")
    # return User().get_user_by_name(id_user)
    return SSO_User().get_user_by_name(id_user)


@app.after_request
def redirect_to_signing(response):
    if response.status_code == 401:
        return redirect(url_for('view_root') + '?next=' + request.url)
    return response
    

@app.before_request
def before_request():
    g.user = current_user


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    log.info(f"LM. LOGOUT. USERNAME: {session['username']}, ip_addr: {ip_addr()}")
    logout_user()
    username = session['username']
    if 'username' in session:
        session.pop('username', None)
    if 'password' in session:
        session.pop('password', None)
    if 'info' in session:
        session.pop('info', None)
    if 'status_anketa' in session:
        session.pop('status_anketa', None)
    if '_flashes' in session:
        session['_flashes'].clear()

    req_json = {'ip_addr': f'{ip_addr()}'}

    resp = requests.post(url=f'{sso_server}/close', json=req_json)

    if resp.status_code != 200:
        log.info(f'----------------\n\tLOGOUT\n\tОшибка {resp.status_code} соединения {username} с сервером SSO\n----------------')
        return redirect(url_for('view_root'))

    resp_json = resp.json()

    if 'status' in resp_json and resp_json['status'] !=200:
        log.info(f'----------------\n\tLOGOUT\n\tОшибка закрытия сессии. Статус: {resp_json['status']}/{ip_addr()}\n----------------')

    return redirect(url_for('view_root'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'styles' not in session:
        if "STYLE" in environ:
            session['styles']=environ["STYLES"]
        else:
            session['styles']=styles
    
    if '_flashes' in session:
         session['_flashes'].clear()
    
    user = ''
    json_user = ''

    if request.method == "GET":
        req_json = {'ip_addr': f'{ip_addr()}'}
        resp = requests.post(url=f'{sso_server}/check', json=req_json)

        log.info(f'LOGIN. GET. CHECK. \n\taddr: {sso_server}/check\n\tREQ_JSON: {req_json}\n\tRESP: {resp}')
        if resp.status_code == 200:
            resp_json=resp.json()
            log.debug(f'LOGIN. GET. RESP_JSON: {resp_json}')
            if 'status' in resp_json and resp_json['status'] == 200:
                json_user = resp_json['user']
                log.debug(f'LOGIN GET. json_user: {json_user}')
                session['username'] = json_user['login_name']
            else:
                log.info(f'----------------\n\tLOGIN_PAGE. GET.\n\tUSER not Registred\n\tIP_ADDR: {ip_addr()}\n----------------')
                return render_template('login.html')

    if request.method == "POST":
        session['username'] = request.form.get('username')
        session['password'] = request.form.get('password')

        req_json = {'login_name': session['username'], 'password': session['password'], 'ip_addr': ip_addr() }
        log.debug(f'LOGIN_PAGE. POST. REQUEST JSON: {req_json}')

        resp = requests.post(url=f'{sso_server}/login', json=req_json)
        if resp.status_code != 200:
            log.info(f'----------------\n\tLOGIN_PAGE. Ошибка {resp.status_code} соединения с сервером SSO\n----------------')
            return render_template('login.html')

        resp_json=resp.json()
        log.debug(f'LOGIN POST. resp_json: {resp_json}/{type(resp_json)}')
        if resp_json['status'] !=200:
            log.info(f'----------------\n\tLOGIN_PAGE. POST.\n\tUSER {session['username']}/{session['password']} not Registred\n----------------')
            return render_template('login.html', info='Неверна Фамилия (или ИИН) или пароль в Windows')

        json_user = resp_json['user']
        # session['username'] = json_user['login_name']
        # session['password'] = json_user['password']
        log.info(f'LOGIN POST. json_user: {json_user}')

    # Если такой username существует и объект user создался, надо проверить пароль и вытащить атрибуты
    if json_user:
        log.debug(f'LOGIN. json_user: {json_user}')
        user = SSO_User().get_user_by_name(json_user)

        if not user:
            log.info(f"LOGIN_PAGE. ERROR LOGIN. New object user is empty. MAY BE USER'S DEP_NAME in LDAP not in list permit_deps in APP_CONFIG.PY")
            return render_template('login.html')

        login_user(user)

        next_page = request.args.get('next')
        if next_page is not None:
            log.info(f'LOGIN_PAGE. SUCCESS AUTHORITY. GOTO NEXT PAGE: {next_page}')
            return redirect(next_page)
        else:
            return redirect(url_for('view_root'))
    
    return render_template('login.html')
