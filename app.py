from time import sleep, strftime

import RPi.GPIO as GPIO
from flask import Flask, render_template, request, url_for
from flask_apscheduler import APScheduler
from pprint import pprint

from config import Config

app = Flask(__name__)
app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# this is the GPIO port we use on the Raspberry PI
RELAIS = 17 

GPIO.setmode(GPIO.BCM) # use GPIO numbers instead of board 
GPIO.setup(RELAIS, GPIO.OUT)

data = {'is_on': False, 'status': 'OFF', 'todo': 'on', 'joblist':'no jobs here', 'coffee_hour': '0', 'coffee_minute': '0'}

def update_status(action):
    global data
    if action == 'on':
        data['is_on'] = True
        data['status'] = 'ON'
        data['todo'] = 'off'
    if action == 'off':
        data['is_on'] = False 
        data['status'] = 'OFF'
        data['todo'] = 'on'
    if action == 'joblist':
        data['joblist'] = list_jobs()
    if action == 'pause_coffee':
        nix = 0 # TODO: http://apscheduler.readthedocs.io/en/latest/modules/job.html#apscheduler.job.Job.reschedule

def log(message):
    with open('coffeepi.log', 'a') as f: #open logfile for appending
        message = '[%(time_now)s]: %(message)s \n' % {"time_now": strftime("%Y-%m-%d %H:%M"), "message": message}
        f.write(message)
        print (message) #for live viewing

def turn_on(): 
    log('Turning on...')
    GPIO.output(RELAIS, GPIO.HIGH)
    update_status('on')
    update_status('joblist')

def turn_off():
    wait_time = 3
    log('turning off...')
    # for some reason my machine does not want to turn off immediately.
    GPIO.output(RELAIS, GPIO.HIGH)
    sleep(wait_time)
    GPIO.output(RELAIS, GPIO.LOW)
    sleep(wait_time)
    GPIO.output(RELAIS, GPIO.HIGH)
    sleep(wait_time)
    GPIO.output(RELAIS, GPIO.LOW)
    update_status('off')
    update_status('joblist')
   

@app.route('/')
def index():
    update_status('joblist')
    return render_template('index.html', data=data)

@app.route('/coffee/on', methods=['GET','POST'])
def coffee_on(): 
    tun_on()
    return render_template('index.html', data=data)

@app.route('/coffee/off', methods=['GET','POST'])
def coffee_off():
    turn_off()
    return render_template('index.html', data=data)

@app.route('/coffee/reschedule', methods=['GET', 'POST'])
def coffee_reschedule():
    coffee_job = 'cron_coffee'
    coffee_hour = int(request.form['coffeehour'])
    coffee_minute = int(request.form['coffeeminute'])
    if 0 <= coffee_hour <= 23 and 0 <= coffee_minute <= 59: # we check for invalid time input
        job =  scheduler.get_job(coffee_job)
        job.reschedule('cron', hour=coffee_hour, minute=coffee_minute)
        #scheduler.reschedule_job(coffee_job, hour=coffee_hour, minute=coffee_minute)
        log('coffetime rescheduled to: ' + str(coffee_hour) + ":" + str(coffee_minute))
    update_status('joblist')
    return render_template('index.html', data=data)



@app.route('/job/list')
def list_jobs():
    global data
    joblist = ''
    for job in scheduler.get_jobs():
        job =  scheduler.get_job(job.id)
        for f in job.trigger.fields:
            if f.name == 'hour':
                hour = f
            if f.name == 'minute':
                minute = f
        if job.name == 'cron_coffee': #this should be somewhere else. we dte the job schedule for display from here.
            data['coffee_hour'] = hour
            data['coffee_minute'] = minute
        joblist += '%(jobname)s : %(jobhour)s:%(jobminute)s' % {"jobname": job.name, "jobhour": hour, "jobminute": minute}
    return joblist 

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, use_reloader=False)
