#Expects that you have a "home" schedule - overrides otherwise.
#Ignores weekend/weekday logic
#Ignores the restriction that buses must be arriving within the hour
DEBUG = False

LOCATIONS = {
  'home':{'stop':'1_29266', 'route':'1_8'},
  'work':{'stop':'1_2255', 'route':'1_8'},
}

#Quick and dirty lookup table for display names.
NAMES = {
  '1_29266':"Cap Hill / Denny Way",
  '1_2255':"Westlake / Denny Way",
  '1_8' : "Route 8",
  'work' : "Work",
  'home' : "Home",
}

#Simple 0 to 23 index of hours in the day.
SCHEDULE = [
  None, #0000
  None, #0100
  None, #0200
  None, #0300
  None, #0400
  None, #0500
  None, #0600
  None, #0700
  'home', #0800
  'home', #0900
  'home', #1000
  None, #1100
  None, #1200
  None, #1300
  None, #1400
  None, #1500
  'work', #1600
  'work', #1700
  'work', #1800
  'work', #1900
  None, #2000
  None, #2100
  None, #2200
  None, #2300
]

#PushOver allows for 7500 messages per month.
#There are no more than 23 weekdays in a month.
#This gives us 326 messages per day or 5 hours of full coverage.
#PushBus will calculate the delay between pushes so as to avoid breaking
#that cap of 7500 - future work could check PushOver for remaining calls
#(no API for this; would have to screen-scrape) and then calculate the
#remaining days that need coverage.
DELAY = (60 * 23 * 60 * len([x for x in SCHEDULE if x is not None])) / 7500
if DELAY < 60:
  DELAY = 60 #No point in having finer-than-one-minute updates.

if DEBUG:
  print "[DEBUG] Calculated delay of %d based on %d hours per day" % (DELAY, len([x for x in SCHEDULE if x is not None]) )

import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('pushbus.cfg')

ONEBUS_KEY = config.get("PushBus", "OneBusAwayKey")
PUSH_KEY = config.get("PushBus", "PushoverKey")
USER_KEY = config.get("PushBus", "PushoverUserKey")

if DEBUG:
  print "[DEBUG] ONEBUS_KEY = '%s'" % ONEBUS_KEY
  print "[DEBUG] PUSH_KEY = '%s'" % PUSH_KEY
  print "[DEBUG] USER_KEY = '%s'" % USER_KEY

if DEBUG:
  URI = 'http://api.onebusaway.org/api/where/arrivals-and-departures-for-stop/%s.json?key='+ONEBUS_KEY+'&minutesBefore=10&minutesAfter=600'
else:
  URI = 'http://api.onebusaway.org/api/where/arrivals-and-departures-for-stop/%s.json?key='+ONEBUS_KEY+'&minutesBefore=10&minutesAfter=65'
PUSH_URI = 'https://api.pushover.net/1/messages.json'

def push_message(title, message, timestamp):
  payload = {
    "token": PUSH_KEY,
    "user" : USER_KEY,
    "message": message,
    "title" : title,
    "timestamp" : timestamp,
  }   
  urllib2.urlopen("https://api.pushover.net/1/messages.json", urlencode(payload) )
  if DEBUG:
    print "[DEBUG] Pushed message to PushOver"

RANKING = [('predictedDepartureTime', '!'),('predictedArrivalTime', '!'),('scheduledDepartureTime', '?'),('scheduledArrivalTime', '?')]

try:
  #ujson is quite a bit faster than the regular json implementation.
  import ujson as json
except ImportError:
  import json

import time, urllib2
from urllib import urlencode

print "[INFO] PushBus is running."
while True:
  is_weekend = time.localtime().tm_wday > 4
  if not is_weekend or DEBUG:
    hour = time.localtime().tm_hour
    loc = SCHEDULE[hour]
    if DEBUG:
      loc = "work"
    if loc is not None:
      stopId = LOCATIONS[loc]['stop']
      routeId = LOCATIONS[loc]['route']
      req = URI % (stopId)
      if DEBUG:
        print "[DEBUG] Fetching %s" % req
      data = json.load(urllib2.urlopen(req))
      
      now = int(time.time())
      
      #iOS allows for four lines per notification before truncation happens.
      #Pushover uses one line for the "title" so we have three lines remaining.
      arrivals = [x for x in data['data']['arrivalsAndDepartures'] if x['routeId'] == routeId][:3]
      
      times = []
      for arr in arrivals:
        for rank in RANKING:
          if rank[0] in arr and arr[rank[0]] != 0:
            times.append((int(arr[rank[0]]/1000), rank[1]))
            break
      
      output = [(time.strftime("%I:%M%p", time.localtime(x[0])),
                 x[0]-now, x[0], x[1]) for x in times]
      
      stop = NAMES[stopId]
      route = NAMES[routeId]
      location = NAMES[loc]
      
      minutes = []
      
      for o in output:
        departs = o[0]
        sc = o[1] / 60
        if sc < 0:
          #ignore any bus that's already gone.
          #the value of "minutesBefore" appears to be ignored by OneBusAway.
          continue
        hr = sc / 60
        mn = sc % 60
        if hr > 0 and not DEBUG:
          #When in debug mode, pretend that everything is within the hour.
          continue
        
        tm = o[2] #Raw timestamp - useful for debugging/backdating.
        rank = o[3]
        minutes.append("%s: %s%s" % (departs, mn, rank))
      title = "%s - %s - %s" % (route, location, stop)
      message = "\n".join(minutes)
      print title
      print message
      print '--EOM--'
      if len(minutes) > 0:
        #If no bus is arriving in the next hour...no message.
        push_message(title, message, tm)
  time.sleep(DELAY) #See above notes about push limits