from flask import Flask, render_template, request, redirect, url_for, jsonify, json, Response, session, g, flash, request, make_response
from sqlalchemy import create_engine, and_, text
from sqlalchemy.orm import sessionmaker, exc
from databasesetup import *
from werkzeug.exceptions import abort
import hashlib
import codecs
from twisted.internet import reactor
import scrapy
from scrapy.crawler import CrawlerRunner
import re
#from minor_scrapy.minor_scrapy.spiders import reddit_spider
import os


app = Flask(__name__)
# initialise the database

engine = create_engine('sqlite:///scrape.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
dbsession = DBSession()

# open the index page
@app.route('/', methods=['GET', 'POST'])
def main():
    if g.user:  # check for user session
        if request.method == 'POST':  # webform submission
            url = request.form['site']
            url = url.replace("/", "%2f")
            return redirect(url_for('spider', url=url))  # run the spider
        return render_template('index.html')
    return redirect(url_for('signin'))
   # run the spider
@app.route('/run-spider/<url>')
def spider(url):
    if g.user:  # check for user session
        if 'reddit' in url:
            os.system('scrapy crawl reddit')  # run command
        else:
            return redirect(url_for('main'))
    # ...and so on...
        return render_template('spider.html')
    return redirect(url_for('signin.html'))

# display report
@app.route('/report/')


def report():
    if g.user:  # check for user session
        query = dbsession.query(Catches)
        return render_template('report.html', query=([catch.serialise for catch in query]))
    return redirect(url_for('signin'))
# generate dynamic query
@app.route('/report/search/', methods=['GET', 'POST'])
def advancedSearch():
    if g.user: # check for user session
        if request.method == 'POST':
            if request.form['field']:
                field = request.form['field']
            if request.form['param']:
                param = request.form['param']
                param = param.replace("/", "%2f")
            elif not request.form['param']:
                param = "%"
            return redirect(url_for('advancedReport', table="catches", field=field, param=param))
        return render_template('advanced.html')
    return redirect(url_for('signin'))
# generate dynamic query
@app.route('/report/<table>?<field>=<param>')
def advancedReport(table, field, param):
    if g.user: # check for user session
        param = param.replace("%2f", "/")
        query = dbsession.execute("select * from {0} where {0}.{1} like '%{2}%'".format(table, field, param))
        rows = query.fetchall()
        result = []
        for row in rows:
            result.append(dict(row))
        return render_template('report.html', table=table, field=field, param=param, query=result)
    return redirect(url_for('signin'))
# compare password with database
def check_password(hashed_password, user_password, salt):
    return hashed_password == hashlib.sha256((user_password.encode()) + salt).hexdigest()
# compare credentials with database
def validate(username, password):
    completion = False
    users = dbsession.query(User)
    for user in users:
        if user.username == username:
            completion = check_password(user.password, password, user.salt)
        return completion
# sign in user
@app.route('/signin/', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        session.pop('user', None)
        uname = request.form['username']
        pword = request.form['password']
        completion = validate(uname, pword)
        if completion == True:
            session['user'] = uname # create user session
            return redirect(url_for('main'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('signin.html', error=error)
# delete session
@app.route('/signout/')


def signout():
    session.pop('user', None)
    return redirect(url_for('main'))
# create user session
@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


if __name__ == '__main__':
    app.secret_key = "\xc2\x0f\xdc\x9d0\x10A\xfa:DO\xcf\xa8%\xf0\x8e\xc1\xcb=\xf8$\xaa\xc8\xfb"
    app.debug = True
    app.run()