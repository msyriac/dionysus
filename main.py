'''
This script does the following:
1. read from an email template
2. replace "unknowns" in the template with decisions that are randomly selected
from pre-defined lists (this can be a list of places for Happy Hour, or a list of
phrases in the "personality" section of settings.yaml)
3. sends the email to recipients

This needs to be integrated with a daemon that sends email automatically at
pre-defined times.
'''

import numpy as np
import time
import yaml
import traceback
import getpass
import sys

def send_email(user, pwd, recipient, subject, body,mail_server="mail.astro.princeton.edu"):
    '''Sends email given username, password, recipient list, email subject and message
    body.
    '''
    import smtplib
    
    FROM = "dio"
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP(mail_server, 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail'
    except:
        traceback.print_exc()
        print "failed to send mail"


# get password from command line for now
# TODO accept location of password file so this can be automated
pwd = getpass.getpass()
recipient = "mathewsyriac@gmail.com" # set to myself for testing
user = "mathewm"
subject = "Happy Hour"
emailFile = "email_first_reminder.txt" # this is the first reminder email

# read from the possible choice of places
my_places = []
with open("listOfPlaces.txt") as f:
    for line in f:
        my_places.append(line.strip())

# decide on a location
np.random.seed(int(time.time()))
decisions = {}
decisions['_location'] = my_places[np.random.randint(0,len(my_places))]

# read the email template
with open(emailFile) as f:
    email = f.read()

# find unknowns marked by $ in the template
unknowns = [word[1:] for word in email.split() if word.startswith('$')]
    
# load settings               
with open('settings.yaml') as f:
    dataMap = yaml.safe_load(f)

# replace unknowns with either settings or decisions
for unknown in unknowns:
    try:
        d = dataMap[unknown]
    except KeyError:
        try:
            d = dataMap['personality'][unknown]
        except KeyError:
            try:
                d = decisions[unknown]
            except KeyError:
                d = "DERP"

    # if there are multiple possibilities, randomly decide
    if type(d) is list or type(d) is tuple:
        d = d[np.random.randint(0,len(d))]

    email = email.replace('$'+unknown,d)

# send email    
send_email(user, pwd, recipient, subject, email,mail_server=mserver)
