
JOBS = ['python', 'java', 'etc']
ZIPCODE = '#####' # Five digit zip
BASE_URL = "http://www.indeed.com/jobs?"
FROM_AGE = '1'
LIMIT = '10' # Default is 10
RADIUS = '25' # Default is 25

"""
Acceptable jobs types are:
	'fulltime'
	'parttime'
	'contract'
	'internship'
	'temporary'

	Note: You can only select ONE job type.

	Leave blank to view all job types.
"""
JOB_TYPE = ''

MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=''
MAIL_PASSWORD=''
MAIL_TO = [''] #put your email in the list