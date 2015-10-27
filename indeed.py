#!/bin/usr/python
import requests
from bs4 import BeautifulSoup
from config import JOBS, ZIPCODE, BASE_URL, LIMIT, FROM_AGE,\
 				JOB_TYPE, RADIUS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME,\
 				MAIL_PASSWORD, MAIL_TO, DB_PATH
import sqlite3
from local_server import app, mail
from flask.ext.mail import Message
from flask import render_template
from multiprocessing import Process
#from threading import Thread


def create_search_urls(baseURL, jobs, zipcode, limit, job_type, radius):
	"""
	Create the search URL's for each individual job.

	We could use the 'requests.get(url, params=stuff)'
	but I wanted to have each function be as small as possible.
	"""
	urls = []

	for job in jobs:
		job = job.replace(' ','+')

		urls.append(baseURL + 'q=' + job + '&l=' + zipcode\
			+ '&limit=' + limit + '&jt=' + job_type + '&radius='\
			+ radius)

	return urls

def create_requests_objects(search_urls):
	"""
	Given a list of URL's, we iterate through each
	and create a list of each requests object to be
	returned out.
	"""
	r_objects = []

	for url in search_urls:
		r_objects.append(requests.get(url))

	return r_objects

def parse_request_objects(r_objects, db_path):
	"""
	With the request objects we pass, we make a
	soup object of each and within the HTML text, we locate
	the div '   row result', within each of the divs contains
	all the information we really need to be able to create our
	message body.
	"""
	results = []
	for r in r_objects:
		soup = BeautifulSoup(r.text)
		print('Checking jobs')
		for job in soup.find_all(class_="  row  result"):
			# Loop through all instances of results
			if add_to_database(str(job.h2.a['href']), db_path):
				# If the link already exists within the database don't
				# add it to our results (we're checking the link above btw)
				results.append(
					dict(
						title = job.h2.a['title'],
						link = 'https://www.indeed.com' + job.h2.a['href'],
						summary = job.find(class_="summary").getText()
					)
				)
		print('Finished storing jobs')

	return results

def init_db(db_path):
	"""
	Connect and create our database if need be.
	"""
	sql = sqlite3.connect(db_path)
	cur = sql.cursor()

	cur.execute('CREATE TABLE IF NOT EXISTS oldjobs(LINK TEXT)')
	print('Loaded database')

def add_to_database(link, db_path):
	"""
	Connect to our database and check if the given 'link' already
	exists within the database. If it does we return 'False' to
	prevent from adding that particular job posting to our email.

	If the 'link' does not exist in our database, then we simply
	add it in and return 'True' to signify that we successfully
	added it to the database and we can continue on with creating
	our email.
	"""
	sql = sqlite3.connect(db_path)
	cur = sql.cursor()

	cur.execute('SELECT * FROM oldjobs WHERE LINK=?', (link,))
	
	if not cur.fetchone():
		cur.execute('INSERT INTO oldjobs VALUES(?)', (link,))
	else:
		return False

	# Commit and return True to signify a succesful insert
	sql.commit()
	return True

def send_email(subject, sender, recipients, results):
	"""
	We send the email with the given subject, whos sending the email,
	our intended recipeients, and our 'results'.

	Results is all the job postings which did not already exist within
	our database, and thus are job postings we have not yet seen.

	We make sure to use the 'with app.app_context()' part since we're
	using the flask only 'render_template' function which requires the
	app context to function.

	Our async email handling is disabled simply because there really
	shouldn't be any need for it, but I left it in there just in case
	anyone wants to use it.
	"""
	print('Sending email')
	msg = Message(subject, sender=sender, recipients=recipients)
	with app.app_context():
		msg.html = render_template('email_form.html',results=results)
		mail.send(msg)
	print('Sent email')

def run_server():
	"""
	This is the function we have the 'Process' call to ensure that
	Flask is up and running for us to send out emails.
	"""
	print('Starting local server')
	app.run()

if __name__ == "__main__":
	"""
	First we have a new 'Process' targetting our run_server function,
	we then create our database, followed with: creating the urls for
	each job, getting each respective requests object, and grabbing
	each new job posting.

	After all that, we send out an email to our 'MAIL_USERNAME' alongside
	our 'results', which are all the new job postings.

	Lastly, we just terminate our running Flask server.
	"""
	server = Process(target=run_server)
	server.start()

	init_db(DB_PATH)
	search_urls = create_search_urls(BASE_URL, JOBS, ZIPCODE, LIMIT, JOB_TYPE, RADIUS)
	r_objects = create_requests_objects(search_urls)
	parsed_results = parse_request_objects(r_objects, DB_PATH)

	send_email(
				'New Job Alerts!!',
				MAIL_USERNAME,
				MAIL_TO,
				parsed_results)

	server.terminate()
	print('Terminated local server')
	server.join()
