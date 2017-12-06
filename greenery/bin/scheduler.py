#!/usr/bin/python3


"""

check all existing Schedule objects, and if one of them should be run now,
run the change.

"""

import os
import sys
import re
import datetime
import logging
sys.path.append( os.environ.get('GREENERY_WEB','/var/www/greenery') )
from greenery import db
from greenery.apps.schedule.models import Schedule
from greenery.apps.outlet.models import Outlet


logfile = '/var/tmp/greenery.errors.log'
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',    
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('scheduler')


def main():
    now = datetime.datetime.now()
    wkday = now.date().strftime("%A")
    scheds = Schedule.query.all()
    for s in scheds:
        if not s.runs_on(wkday):
            continue

        for k, t in {'on': s.on_time, 'off': s.off_time}.items():
            hour, minute = to_24h(t)
            if minute == now.minute and hour == now.hour:
                state = 0
                if k == 'on':
                    state = 1

                o = Outlet.query.get(s.outlet_id)
                if not o:
                    logger.error("no outlet with id %d", s.outlet_id)

                try:
                    if state == 1:
                        rval = o.on()
                    else:
                        rval = o.off()

                    if rval:
                        logger.warning("outlet id %d state change to %d failed" % (o.id, state))
                    else:
                        o.state = state
                        db.session.commit()
                except Exception as x:
                    logger.error(x)


"""
takes a time-string, and returns a tuple (hour, min)
the hour is in 24 hour format.
If there was an error it will return (None, None)
"""
def to_24h(strng):
    hour = None
    minute = None
    match = re.search(r'(\d+):(\d+)\s*(am|pm)?', strng, re.IGNORECASE)
    if match:
        minute = int(match.group(2))
        hour = int(match.group(1))
        if match.group(3):
            if re.search(r'am', match.group(3), re.IGNORECASE) and hour == 12:
                hour = 0
            if re.search(r'pm', match.group(3), re.IGNORECASE) and hour < 12:
                hour = int(match.group(1)) + 12
        
    return (hour, minute)


if __name__ == '__main__':
    main()

