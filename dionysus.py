#!/usr/bin/python2
from __future__ import print_function
import time, sys, yaml, os
from daemon import runner
import datetime as dt
import pytz
from dateutil import parser
import getpass
import calendar
import numpy as np
import traceback

def randFromList(d):
    return d[np.random.randint(0,len(d))]

def location_decision(my_places,weights):

    try:
        with open('/tmp/dionysus_last_time.txt', 'r') as myfile:
            last_time=myfile.read().replace('\n', '').strip()
    except:
        last_time = ""

        
    # weights should sum to 1 for multinomial
    weights /= np.sum(weights)

    decision = last_time
    while decision.strip()==last_time:
        idx = np.where(np.random.multinomial(1, weights))[0]
        decision = my_places[idx[0]]

    with open('/tmp/dionysus_last_time.txt', "w") as text_file:
        text_file.write(decision)
                
    return decision


def try_email_authenticate(user, pwd,mail_server="mail.astro.princeton.edu"):
    """Before starting the daemon (which might only try accessing the mail
    server a week later), we want to make sure the credentials entered are valid.
    """
    
    import smtplib
    try:
        server = smtplib.SMTP(mail_server, 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.close()
        print('dio: Successfully authenticated.')
    except:
        traceback.print_exc()
        print("dio: Authentication failed.")
        sys.exit(1)


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
        print('dio: Successfully sent mail.')
    except:
        traceback.print_exc()
        print("dio: Failed to send mail.")




def process_email(email_body,data_map,list_of_places_file=None):    
    decisions = {}
    if list_of_places_file is not None:
        # read from the possible choice of places
        places_weights = np.genfromtxt(list_of_places_file,
                                       delimiter=",",
                                       names=True,
                                       dtype=['U128', float, 'U128'])
        my_places = places_weights['name']
        weights = places_weights['weight']
        patios = np.array([s.strip().lower() in ['true','t','y','yes','yep'] for s in places_weights['patio']])

        import weather_info as w
        woeid = 2476729 # Princeton, NJ
        nice_out,weather,temperature = w.is_it_nice_out(woeid)

        if nice_out:
            my_places = my_places[np.where(patios)]
            weights = weights[np.where(patios)]
            data_map['weather'] = "(It's nice out today, so I picked a place that has a patio.)"
        else:
            data_map['weather'] = ""

        # decide on a location
        np.random.seed(int(time.time()))
        decisions['_location'] = location_decision(my_places,weights)

    # find unknowns marked by $ in the template
    unknowns = [word[1:] for word in email_body.split() if word.startswith('$')]

    dataMap = data_map

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
            d = randFromList(d)

        email_body = email_body.replace('$'+unknown,d)

    return email_body

def check_if_time(frequency,trigger_day,time_zone_string,trigger_time,tolerance):
    today = dt.date.today()
    if frequency=='weekly':
        assert trigger_day in [calendar.day_name[x] for x in xrange(7)], "Unrecognized day name."
        isDay = (calendar.day_name[today.weekday()]==trigger_day)
        if not(isDay): return False
    else:
        raise NotImplementedError

    timezone=pytz.timezone(time_zone_string)
    time_now = dt.datetime.now(tz=timezone)

    datestring = dt.datetime.strftime(dt.datetime.today().date(),format='%b %d %Y')

    passtime = trigger_time
    dtin = parser.parse(passtime)
    dtin_aware = timezone.localize(dtin)
    if abs((dtin_aware-time_now).total_seconds())<tolerance:
        return True
    else:
        return False
        
    

class App():
    def __init__(self,daemon_command,yaml_file,time_interval_sec=60,tolerance_seconds=180):
        self.dir = os.path.dirname(os.path.abspath(__file__))
        self.stdin_path = '/dev/null'
        self.stdout_path = self.dir+'/dio_out_'+str(time.time())+".log"
        self.stderr_path = self.dir+'/dio_err_'+str(time.time())+".log"
        self.pidfile_path =  '/tmp/dionysus_daemon.pid'
        self.pidfile_timeout = 5
        self.interval = time_interval_sec
        self.tolerance = tolerance_seconds
        assert self.tolerance>self.interval

        self.last_day_reminder = -1
        self.last_day_location = -1

        # get user credentials
        if daemon_command!="stop":
            with open(yaml_file) as f:
                self.settings = yaml.safe_load(f)
            self.username = getpass.getpass("Username for accessing "+self.settings['email']['mail_server']+": ")
            self.pwd = getpass.getpass()

            try_email_authenticate(self.username, self.pwd,mail_server=self.settings['email']['mail_server'])
            print("dio: Daemon is running.")
            

    def run(self):
        
        while True:

            now_day = dt.datetime.today().day
            '''
            if check_if_time(self.settings['frequency'],
                             self.settings['trigger_day'],
                             self.settings['time_zone'],
                             self.settings['trigger_time_reminder'],
                             tolerance=self.tolerance) and (now_day!=self.last_day_reminder):
                print("Time to send a reminder...")
                self.last_day_reminder = dt.datetime.today().day
                with open(self.dir+"/email_first_reminder.txt") as f:
                    email_body = f.read()

                email_body = process_email(email_body,self.settings)
                send_email(self.username, self.pwd,
                           self.settings['email']['recipients'],
                           randFromList(self.settings['email']['subject']),
                           email_body,
                           self.settings['email']['mail_server'])
            '''
            
            if check_if_time(self.settings['frequency'],
                             self.settings['trigger_day'],
                             self.settings['time_zone'],
                             self.settings['trigger_time_location'],
                             tolerance=self.tolerance) and (now_day!=self.last_day_location):

                print("Time to send location...")
                self.last_day_location = dt.datetime.today().day

                with open(self.dir+"/email_location.txt") as f:
                    email_body = f.read()

                email_body = process_email(email_body,self.settings,
                                           list_of_places_file=self.dir+"/listOfPlaces.csv")
                send_email(self.username, self.pwd,
                           self.settings['email']['recipients'],
                           randFromList(self.settings['email']['subject']),
                           email_body,
                           self.settings['email']['mail_server'])
            
            time.sleep(self.interval)


def test(yaml_file):
    dir = os.path.dirname(os.path.abspath(__file__))
    with open(yaml_file) as f:
        settings = yaml.safe_load(f)
    with open(dir+"/email_location.txt") as f:
        email_body = f.read()
    email_body = process_email(email_body,settings, \
                               list_of_places_file=dir+"/listOfPlaces.csv")
    print(email_body)

def main(argv):
    try:
        yamlFile = sys.argv[2]
    except:
        assert sys.argv[1]=="stop", "No settings yaml file specified."
        yamlFile = None

    if sys.argv[1]=="test":
        test(sys.argv[2])
        sys.exit()
        
    app = App(sys.argv[1],yamlFile)
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.do_action()
    
if (__name__ == "__main__"):
    main(sys.argv)


