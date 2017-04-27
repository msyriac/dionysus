#!/usr/bin/python2
from __future__ import print_function
import time, sys, yaml
from daemon import runner
import datetime as dt
import pytz
from dateutil import parser
import getpass
import calendar

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
    def __init__(self,daemon_command,yaml_file,time_interval_sec=3):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/dionysus_daemon.pid'
        self.pidfile_timeout = 5
        self.interval = time_interval_sec

        # get user credentials
        if daemon_command!="stop":
            self.username = getpass.getpass("Username for accessing mail-server:")
            self.pwd = getpass.getpass()
            with open('settings.yaml') as f:
                self.settings = yaml.safe_load(f)

                
            

    def run(self):
        while True:
            
            print(check_if_time(self.settings['frequency'],self.settings['trigger_day'],self.settings['time_zone'],self.settings['trigger_time_reminder'],tolerance=30))
            time.sleep(self.interval)



try:
    yamlFile = sys.argv[2]
except:
    assert sys.argv[1]=="stop", "No settings yaml file specified."
    yamlFile = None
            
app = App(sys.argv[1],yamlFile)
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
