from datetime import date
import datetime
import os
from flask import Flask,request,session,g,redirect,url_for,abort,\
	render_template,flash
import sqlite3

DATABASE = 'blog.db'
DEBUG=True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app=Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])




def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql',mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close
        
@app.route('/', methods=['GET','POST'])
def show_posts():
    cur = g.db.execute('select * from posts')
    entries = [dict(title=row[0], post=row[1], user=row[2], time=row[3]) for row in cur.fetchall()]
    return render_template('show.html', entries=entries)
    
@app.route('/add', methods=['GET','POST'])
def add_post():
	if request.method == 'POST':
		head=request.form['title']
		body=request.form['body'] 
		un=request.form['user']
		t=datetime.datetime.now()
		g.db.execute('insert into posts (title, post, user, time) values (?, ?, ?, ?)',[head,body,un,t])
		g.db.commit()
		flash('Inserted')
		return redirect(url_for('show_posts'))
	return render_template('add.html')

@app.route('/test', methods=['GET','POST'])
def testing():
	if request.method == 'POST':
		txt=request.form['title']
		return txt
	return render_template('add.html')

@app.route('/edit', methods=['GET','POST'])
def edit_post():
    if request.method == 'POST':
        un=request.form['user1']
        t=request.form['time1']
        cur = g.db.execute('select * from posts where user == ? and time == ?',(un,t))
        entries = [dict(title=row[0], post=row[1], user=row[2], time=row[3]) for row in cur.fetchall()]
        return render_template('edit.html', entries=entries)
    return redirect(url_for('show_posts'))

@app.route('/update', methods=['GET','POST'])
def update():
	if request.method == 'POST':
		head=request.form['title']
		name=request.form['oldUser']
		oldTime=request.form['oldTime']
		body=request.form['body'] 
		un=request.form['user']
		t=datetime.datetime.now()
		g.db.execute('update posts set title=?,post=?,user=?,time=? where user==? and time=?',(head,body,un,t,name,oldTime))
		g.db.commit()
		flash('Inserted')
		return redirect(url_for('show_posts'))
	return render_template('add.html')

@app.route('/delete', methods=['GET','POST'])
def delete_post():
    if request.method == 'POST':
        un=request.form['user1']
        t=request.form['time1'] 
        cur = g.db.execute('delete from posts where user== ? and time== ?',(un,t))
        g.db.commit()
    return redirect(url_for('show_posts'))
if __name__ == '__main__':
	app.run()

