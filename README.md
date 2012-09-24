# PushBus

## Overview

When it's time to leave...
* I don't want to mess around with an app.
* I don't want to wait for location services to kick in.
* I really don't want to deal with geofencing.

Enter PushBus, which provides notifications like this:

![Example Notification](https://github.com/aleksandyr/PushBus/raw/master/readme_images/PushBus.png)

The data you need to see, constantly updated, with no other bells or whistles.

## Interpreting your notifications

    Your route - Your location - The name of your stop:
    Arrival Time: Minutes to Scheduled Arrival?
    Arrival Time: Minutes to Predicted Arrival!

The `?` indicates a "scheduled" arrival whereas the `!` indicates a "predicted"
arrival (generally more reliable; not always available; predictions are usually
only available for the last 20 minutes of waiting for a given stop.)

## Requirements

* Modern(-ish) Python installation.
* ujson helps, but isn't required.
* a OneBusAway API key.
* PushOver, a PushOver application key, and a PushOver user key.

## Configuring PushBus

You'll need a "pushbus.cfg" file with the following structure:

    [PushBus]
    OneBusAwayKey=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
    PushoverKey=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    PushoverUserKey=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

I can't include my keys for various reasons; I intend to fix this eventually.
(see the Future Work section.)

I haven't quite finished exporting the configuration bits to pushbus.cfg so
you'll need to read and edit pushbus.py to set up your stops, routes, and
schedule (unless you happen to share my exact preferences.)

Your stop and route comes from pages like this:

[http://onebusaway.org/where/standard/stop.action?id=1_29266]

(note the `id=1_292166` above)

If you filter down to a particular route, you might get a page like this:

[http://onebusaway.org/where/standard/stop.action?id=1_29266&route=1_8]

(note the `route=1_8` above)

## Configuring iOS

PushBus, depending on your configuration, will send one notification between
every one to five minutes during the hours you select. The notification rate
is determined by the 7500 requests per month that PushOver caps any single
application at (allows you five hours per weekday each 23-weekday month of
once-per-minute updates.) Notifications will never be sent more frequently than
once per minute.

The below settings are what I use. This prevents PushOver from ever waking my
device up (saves on battery and annoyance factor) and just shows the most
recent report (and therefore the most relevant one.)

This does cut down on how useful PushOver is for anything else but there's not
much else that can be done without writing a native application with a unique
push certificate, etc.

![Settings](https://github.com/aleksandyr/PushBus/raw/master/readme_images/Settings-p1.png)

![Settings (continued)](https://github.com/aleksandyr/PushBus/raw/master/readme_images/Settings-p2.png)

## Future Work

* Easy
** Easier configuration
** Instructions for Android
** Notifications when the schedule changes (home/work)
** Growl/Prowl/Howl compatibility
* Harder
** Make this a (simple) web service instead of requiring everyone to have a OBA key
** Simple Web UI to set up schedules and routes
** IFTTT-based configuration
*** Text IFTTT "pushbus home" - get your home schedule for the next hour
*** Text IFTTT "pushbus off/on" - turn pushbus off/on
*** Text IFTTT "pushbus oof" - turn pushbus off for the day
* Much Harder
** Exchange and/or Google Calendar integration (see below)
** Desktop application / integration with Notification Center
** Remove dependency on PushOver by writing my own app
*** Donations towards an iPhone dev license happily accepted; I might actually kickstart this assuming interest...

### Calendar Integration
I'm not sure whether or not this is a useful idea.

It would not be terribly difficult to use the Google Calendar API to create
virtual, moving, appointments that show when the next three relevant buses are
expected to arrive. There are lots of cases where this would be great...and many
more where it would be terrible. The advantage is removing the dependency on
PushOver but I could see this getting out of hand quickly...

## Miscellaneous Notes

* Buses arriving in the past will not be shown.
* Buses arriving more than an hour in the future will not be shown.