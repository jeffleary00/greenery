import re
import time
import serial
import logging
from greenery import serial_port
from greenery.apps.admin.models import Setting
from greenery.lib.ttycmd import cmd_codes


logfile = '/var/tmp/greenery.errors.log'
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',    
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('rfutils')
pause_seconds = 15
debug = False

"""
send a code to the serial tty.
response back should be either 'ok' or 'fail'

returns 0 on success. 
"""
def rf_transmit(chan, state):
    failure = 1
    base = None
    pin = None

    try:
        pin = Setting.query.filter(Setting.name == 'rf tx pin').first().value
        base = Setting.query.filter(Setting.name == 'rf tx base code').first().value
    except:
        pass

    if not base:
        logger.error("rf tx pin setting not found")
        return 1
    if not pin:
        logger.error("rf tx base code not found")
        return 1

    code = int(base)
    code += (chan << 1)
    code += state

    if debug:
        print("channel: %d" % chan)
        print("state: %d" % state)
        print("code: %d" % code)

    try:
        ser = serial.Serial(serial_port, 9600, 5)
        time.sleep(2)
        if not ser.isOpen:
            ser.open(serial_port)
        
        ser.flushInput()
    except Exception as x:
        logger.error(x)
        return 1

    cmd = "%d%02d%d\n" % (cmd_codes['tx'], pin, code)
    if debug:
        print("command: %s" % cmd)
    ser.write(cmd.encode('UTF-8'))
    line = ser.readline().decode().strip()
    if re.search(r'^ok', line, re.IGNORECASE):
        failure = 0

    ser.close()
    return failure


