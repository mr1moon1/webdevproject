'''
Got help from this YouTube tutorial, for user authentication: l:https://github.com/PrettyPrinted/building_user_login_system

Things I'm still not sure how to do:
1. Minimize FOUC so it doesn't flash white on each new page (if that's still happening)
2. Change the color of a link as your mouse hovers over it
3. Use jinja to change the CSS :root variables
'''

import numpy as np
import pandas as pd
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DateField, SelectField#Boolean field is checkbox
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Email, Length
import email_validator
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import re
import random
import calendar #ticks
import datetime
from datetime import timedelta
from operator import attrgetter
from webcolors import rgb_to_hex #autostyle
from colorthief import ColorThief
from magic_background import magic_background
from wiki2artifacts import wiki2artifacts #autopopulate db

app = Flask(__name__)
Bootstrap(app)
file_path = os.path.abspath(os.getcwd())+"\database.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
app.config['SECRET_KEY'] = 'meow'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#===============================================================
# User authentication, eh :|

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(), unique=True)
	email = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class LoginForm(FlaskForm):
	#Three fields.
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
	remember = BooleanField('remember me')
	
class RegisterForm(FlaskForm):
	#username, email, and password fields.
	email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	username = StringField('username', validators = [InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators = [InputRequired(), Length(min=4, max=15)])

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	# Login form is a little more complicated than signup form, but it's still pretty easy.
	form = LoginForm()
	if form.validate_on_submit():
		print("here")
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			print("there is a user")
			correct_password_hash = user.password
			hashed_inputted_password = generate_password_hash(form.password.data, method='sha256')
			print(correct_password_hash)
			print(form.password.data)
			if check_password_hash(user.password, form.password.data):
				print("correct password")
				login_user(user, remember=form.remember.data)
				return redirect(url_for('dashboard'))
			else:
				print("Password is incorrect")
		return '<h1>INVALID USERNAME OR PASSWORD:'+form.username.data+' '+form.password.data+'</h1>'
	return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegisterForm()
	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data, method='sha256')
		new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(new_user)
		db.session.commit() #Add vs. commit -- idk lol, but u gotta do it
		return '<h1>A new user has been created!</h1>'
	return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
	return render_template('dashboard.html', name=current_user.username)
	
@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))
	
#==============================================================
# The classes defining the actual interesting meat of the project:

class Topic(db.Model):
	tid = db.Column(db.Integer, primary_key=True, autoincrement=True)
	title = db.Column(db.String(), unique=True)
	#artifacts = db.relationship('Artifact', backref='topic', lazy=True)
	style = db.relationship('Style', backref='atopic', lazy=True)
	artifacts = db.relationship('Artifact', backref='topic', lazy=True)
db.create_all()
class Artifact(db.Model):
	aid = db.Column(db.Integer, primary_key=True, autoincrement=True)
	title = db.Column(db.String())
	description = db.Column(db.String())
	date = db.Column(db.Date(), nullable=False)
	url = db.Column(db.String())
	atopic = db.Column(db.Integer, db.ForeignKey('topic.tid'), nullable=False)
db.create_all()
# auto-styling is a thing this website does.
class Style(db.Model):
	sid = db.Column(db.Integer, primary_key=True, autoincrement=True)
	title = db.Column(db.String())
	topic = db.Column(db.Integer, db.ForeignKey('topic.tid'), nullable=False)
	imgurl = db.Column(db.String())
	#-----------------------------------
	colors = db.Column(db.String()) #np string representation of a list
	tibidi = db.Column(db.String()) #np string representation of a list
		#^ [tackiest_index, brightest_index, darkest_index]
db.create_all()
	
#==================================================
# Autostyle:
	
# Notice how there's no style form? :) All it needs to go off of is the title of the topic, and it uses that string to make the aesthetic.
def color_knowledge(img, imgurl):
	print(imgurl)
	colorthief = ColorThief(imgurl)
	palette = colorthief.get_palette(quality=1000, color_count=10)
	
	brightness = []
	tackiness = []
	for p in palette:
		brightness.append(sum(p))
		tackiness.append(np.var(p))
		
	return colorthief, palette, brightness, tackiness

# Returns a tibidi (not packaged as a single list)
def colorbychance(ct, p, b, t):
	ti, bi, di = random.sample(range(len(p)),3)
	b_inorder = b.sort()
	t_inorder = t.sort()
	ti_picked = random.choice(t[-3:])
	bi_picked = random.choice(b[-3:])
	di_picked = random.choice(b[:2])
	print(p)
	print(p)
	print(p)
	print(type(p))
	for i in range(len(p)):
		if t[i]==ti_picked:
			ti = i
		if b[i]==bi_picked:
			bi = i
		if b[i]==di_picked:
			di = i
	if ti==bi or ti==di or bi==di:
		return colorbychance(ct, p, b, t)
	return ti, bi, di
	
def autostyle(topic_name, topic_index):
	img, imgurl = magic_background.magic_background(topic_name)
	ct, p, b, t = color_knowledge(img, imgurl)
	print(p)
	
	#Will want the colors from the palette representable in HTML-friendly hex form, so do that here:
	colors = []
	for rgbcolor in p:
		colors.append(rgb_to_hex(rgbcolor))
	
	'''
	#ti means tackiest_index
	ti = min(range(len(t)), key=t.__getitem__)
	
	#Doing a little cheat to get the brightness extremes; temporarily taking out the ti (so bi =/= ti) but then afterward the tackiest color will go back into the brightness measure... Or not, depending on list b will even get used after this function.
	bti = b[ti]
	b[ti] = (min(b) + max(b)) / 2 #lazy, not watertight way to hopefully ensure that b[ti] won't be considered the brightest OR the darkest...
	
	#bi means brightest_index
	bi = b.index(max(b))
	
	#di means darkest_index
	di = b.index(min(b))
	'''
	#--------------------------------------------
	# Redoing it all -- hopefully get better colors here:
	ti, bi, di = colorbychance(ct, p, b, t)
	
	#Now, put it in the table :)
	new_style = Style(title=topic_name, topic=topic_index, imgurl=imgurl, colors=np.array2string(np.array(colors)), tibidi=np.array2string(np.array([ti,bi,di])))
	db.session.add(new_style)
	db.session.commit()
	
#===================================================
# Forms:

class CreateTopicForm(FlaskForm):
	title = StringField('title', validators=[InputRequired(), Length(min=1, max=30)])
	panels = BooleanField('make background panels')
	collaborative = BooleanField('enable other users to contribute')
class CreateArtifactForm(FlaskForm):
	title = StringField('title', validators=[InputRequired(), Length(min=1, max=100)])
	description = StringField('description')
	date = DateField('date', format='%m/%d/%Y')
	url = StringField('url')
	atopic = SelectField('atopic', choices=db.session.query(Topic.title).all())
	
	#The following is what helps make sure that the topics list is updated, for the SelectField in this form.
	def __init__(self, *args, **kwargs):
		super(CreateArtifactForm, self).__init__(*args, **kwargs)
		self.atopic.choices = [(a.tid, a.title) for a in Topic.query.order_by(Topic.title)]
	
@app.route('/create_topic', methods=['GET', 'POST'])
def create_topic():
	form = CreateTopicForm()
	if form.validate_on_submit():
		new_topic = Topic(title=form.title.data)
		db.session.add(new_topic)
		db.session.commit()
		
		# Create the style:
		autostyle(new_topic.title, new_topic.tid)
		
		return '<h1>A new topic has been created!</h1>'
	return render_template('create_topic.html', form=form)
	
#HTML USED: create_artifact.html
@app.route('/create_artifact', methods=['GET', 'POST'])
def create_artifacts():
	form = CreateArtifactForm()
	if form.validate_on_submit():
		
		title = form.title.data
		description = form.description.data
		date = form.date.data
		url = form.url.data
		atopic = form.atopic.data
		
		print(title)
		print(description)
		print(date)
		print(url)
		print(int(atopic))
		
		new_artifact = Artifact(title=form.title.data, description=form.description.data, date=form.date.data, url=form.url.data, atopic=form.atopic.data) #atopic=Topic(tid=int(form.atopic.data)))
		db.session.add(new_artifact)
		db.session.commit()
		return '<h1>A new artifact has been created!</h1>'
	return render_template('create_artifact.html', form=form)
	
	
#=============================================================
# Other types of artifacts:

class YouTubeArtifact(Artifact): #inherits Artifact class
	pass
	
class ImageArtifact(Artifact): #inherits Artifact class
	pass

class WikiArtifact(Artifact): #inherits Artifact class
	pass

	
#=============================================================
# ???:

# Starting off real simple: just display the artifacts.
@app.route('/all_artifacts')
def all_artifacts():
	artifacts=Artifact.query.all()
	return render_template('all_artifacts.html', artifacts=artifacts)
	
# Helper function to decide where to locate the things.
def find_extreme_dates(items):
	earliest_date = None
	latest_date = None
	if items:
		earliest_date = items[0].date
		latest_date = items[0].date
	for item in items:
		if item.date < earliest_date:
			earliest_date = item.date
		if item.date > latest_date:
			latest_date = item.date
	return earliest_date, latest_date
	
def find_relative_lengths(items, overall_depth, start_depth):
	start_date, end_date = find_extreme_dates(items)
	overall_length = end_date - start_date
	
	# This'll probably happen if there are no artifacts listed for the topic, because...
	# The query to get artifacts of a specified topic would return an empty set.
	# & of course, the maximum distance of scalars within an empty set, would... probably be zero? Or infinity. Either way, Python seems to assume it as zero in this setting.
	if overall_length==0:
		print("For anyone who is reading the console, you might be interested to learn that the find_relative_lengths() method is returning None, perhaps because the function was given an empty set...")
		return None
	
	lengths = {}
	depths = {}
	for item in items:
		time_since_start = item.date - start_date
		relative_length = time_since_start / overall_length
		relative_length_dict = {item.aid : relative_length}
		absolute_depth_dict = {item.aid : relative_length*overall_depth+start_depth}
		lengths.update(relative_length_dict)
		depths.update(absolute_depth_dict)
	return lengths, depths
	
#Find the absolute pixel depths for each item. 
def find_absolute_depths(artifacts, start_depth, overall_depth, relative_depths):
	absolute_depths = []
	for artifact in artifacts:
		absolute_depth = start_depth + overall_depth * relative_depths[artifact.aid]
		localdict = {artifact.aid : absolute_depth}
		absolute_depths.append(localdict)
	return absolute_depths
	
#=====================================================
# Ticks: (ABANDONED feature, at least for the time being...)

def create_ticks(artifacts, overall_depth=1, start_depth=0):
	#By default, this just returns ratios (because the denominator, overall_depth, is 1.)
	
	month_ticks = [] #A tick for the first day of every month
	first_artifact = min(artifacts, key=attrgetter('date'))
	last_artifact = max(artifacts, key=attrgetter('date'))

	i = 0
	current_date = first_artifact.date
	while current_date < last_artifact.date:
		if current_date.day==1: #The first day of the month
			current_ratio = (current_date - first_artifact.date) / (last_artifact.date - first_artifact.date)
			
			current_pixel_depth = current_ratio * overall_depth + start_depth
		
			month_ticks.append([i, str(str(calendar.month_name[current_date.month])+" "+str(current_date.year)),current_ratio, current_pixel_depth])
			
			i += 1
			
		current_date += timedelta(days=1)
		
	'''
	Each list should contain items that each contain the following contents:
	{ 
		tick[0]	 unique number for ease of naming the auto-generated CSS style components,
		
		tick[1]	 human-readable label that is a formal name of the time,
		
		tick[2]	 the depth that the tick should go down in the page (expressed in absolute amount of pixels for that specific page) ~~> Could maybe change to express as ratios, to help with future modularity of this code, but it's probably worth just leaving as is, at least for now.
	}
	x2
	'''
	return month_ticks
	
#=====================================================
# The front-facing pages:
	
@app.route('/timeline')
def timeline():
	topic_name = request.args.get('topic')
	if topic_name==None:
		topic_name = random.randrange(1, Topic.query.count())
		
	colors=None
	tackycolor=None
	brightcolor=None
	darkcolor=None
	imgurl=None
	style = Style.query.join(Topic).filter(Topic.title==topic_name).first() #hope this works?
	if style:

		colors = style.colors
		colors = re.sub("[\[\]\n\']","",colors)
		#Got so sick of debugging external array-to-list methods, we'll just do it the slow way:
		colors = colors.split(" ")
		tibidi = style.tibidi
		ti = int(tibidi[1])
		bi = int(tibidi[3])
		di = int(tibidi[5])
		tackycolor = colors[ti]
		brightcolor = colors[bi]
		darkcolor = colors[di]
		
		imgurl=style.imgurl
		
	print(topic_name)	
	ticks = request.args.get('ticks')
	overall_depth=1000
	start_depth = 0
	
	artifacts = Artifact.query.join(Topic).filter(Topic.tid==topic_name).all()
	topic = Topic.query.filter(Topic.tid==topic_name).first()
	if not str(topic_name).isnumeric():
		artifacts = Artifact.query.join(Topic).filter(Topic.title==topic_name).all()
		topic = Topic.query.filter(Topic.title==topic_name).first()
			
	if not artifacts:
		return render_template('empty_topic.html', topic=topic)
		
	if len(artifacts)==1:
		artifact = artifacts[0]
		return render_template('one_topic.html', topic=topic, artifact=artifact)
	
	# And the following is what is intended to happen from this function:
	relative_depths, absolute_depths = find_relative_lengths(artifacts, overall_depth, start_depth)
	
	month_ticks = None
	week_ticks = None
	if ticks:
		month_ticks = create_ticks(artifacts, overall_depth=overall_depth, start_depth=start_depth)
		print(month_ticks)
		for tick in month_ticks:
			print(tick[2])
	
	return render_template('timeline.html', artifacts=artifacts, relative_depths=relative_depths, overall_depth=overall_depth, start_depth=start_depth, absolute_depths=absolute_depths, topic=topic, ticks=ticks, month_ticks=month_ticks, num_artifacts=len(artifacts), tackycolor=tackycolor, panelcolor=brightcolor, textcolor=darkcolor, imgurl=imgurl, style=style)
	
@app.route('/artifact')
def artifact():

	# given in the URL: localhost.com/artifact?artifact=<artifact id or title>
	input = request.args.get('artifact')
	
	# If no artifact given, let's just do a random artifact whynot.
	if not input:
	
		input = random.randrange(1,Artifact.query.count()) # Remember that you can't query to the 0th Artifact... it seems like the autoincrement starts from 1.
		
	# Now, give the URL the chance to give either an int input (to be the id of an artifact) or a string input (to be the title of an artifact)
	if str(input).isnumeric():
		artifact = Artifact.query.get(input)
	else:
		artifact = Artifact.query.filter(Artifact.title==input)
		
	# Artifact might be None, so I'll try to make sure it's not that.
	if artifact:
		topic = Topic.query.get(artifact.atopic)
		return render_template('artifact.html', artifact=artifact, topic=topic)
		
	# If artifact was None:
	return '<h1>Oops... looks like there was probably no artifact to present.</h1>'
	
# Get links for each timeline.
def timeline_links(topics):
	links = []
	for topic in topics:
		link = None
		links.append(link)
	return links
	
@app.route('/topics')
@app.route('/timelines')
def timelines():
	topics = Topic.query.all()
	links = timeline_links(topics)
	return render_template('topics.html', topics=topics, links=links)
	
#===============================================================
# I was too lazy to manually create example artifacts, so I made a module to scrape tables on Wikipedia, to make each timeline more quickly. This took several days.

# :| couldn't find a function that converts "May 2, 2008" to "05/02/2008" so i make it
def month_string_to_number(string):
	'''
	Copypasted this function from:	https://stackoverflow.com/questions/3418050/month-name-to-month-number-and-vice-versa-in-python
	'''
	m = {
		'jan': 1,
		'feb': 2,
		'mar': 3,
		'apr':4,
		 'may':5,
		 'jun':6,
		 'jul':7,
		 'aug':8,
		 'sep':9,
		 'oct':10,
		 'nov':11,
		 'dec':12
		}
	s = string.strip()[:3].lower()

	try:
		out = m[s]
		return out
	except:
		raise ValueError('Not a month')
def convertdatetime(string): #string
	a = string
	print(a)
	b = re.sub(",","",a)
	print(b)
	c = str.split(b)
	print(c)
	things = c
	#c[0] = month_string_to_number(c[0])
	#[0] month [1] day [2] year
	#d = str(c[0])+"/"+str(c[1])+"/"+str(c[2])
	monthindex = 0
	dayindex = 1
	yearindex = 2
	for i in range(2):
		if not things[i].isnumeric():
			monthindex = i
			things[i] = month_string_to_number(things[i])
		elif len(things[i])==4:
			yearindex = i
		else:
			dayindex = i
	return datetime.date(int(things[yearindex]),int(things[monthindex]),int(things[dayindex]))

def scrape_wiki(topic, url, tablename=None):
	df = wiki2artifacts(url=url, tablename=tablename, topic=topic) #returns a df
	#df.to_sql(topic, index=False, if_exists='append', con=db.session)
	for index, row in df.iterrows():
		title=row['title']
		date=row['date']
		#date=datetime.strptime(date, '%m/%d/%Y')
		date = convertdatetime(date)
		
		description=row['description']
		url=row['url']
		atopic=row['atopic']
		
		artifact = Artifact(title=title, date=date, description=description, url=url, atopic=atopic)
		db.session.add(artifact)
		db.session.commit()

def addtopic(title):
	new_topic = Topic(title=title)
	tid = new_topic.tid
	db.session.add(new_topic)
	db.session.commit()
	return tid
	
	
db.create_all()
if __name__ == '__main__':
	
	# Should make functions after this line, to bulk-scrape wiki pages to populate the Artifacts table.
	#addtopic("English monarchy accessions")
	
	'''
	url="https://en.wikipedia.org/wiki/List_of_British_coronations"
	tablename="Kings and queens of England (1066–1603)"
	scrape_wiki(topic=8, url=url, tablename=tablename)
	'''
	app.run(debug=True)