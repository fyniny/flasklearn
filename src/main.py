from functools import wraps
from os import stat
import re
import sys
from gevent.pywsgi import WSGIServer
from flask import Flask, request
import daemon
from getopt import getopt

app = Flask(__name__)

ipv4reg = '^((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}$'

class wrapperapp(object):
    def __init__(self):
        self.count = 0
    def wrap_counter(self, func):
        @wraps(func)
        def doafterwrap(*args, **kwargs):
            return func(count=self, *args, **kwargs)
        return  doafterwrap   

wrapperappins = wrapperapp()

def check_params(params, pattern):
    return re.search(pattern, params)

@app.route('/')
@wrapperappins.wrap_counter
def index(count):
    count.count += 1
    count = count.count
    return 'hello world %d' % count

@app.route('/register', methods=['POST'])
@wrapperappins.wrap_counter
def register(count):
    count.count += 1
    count = count.count
    if request.mimetype != 'application/json':
        return {'code': -1, 'msg': 'mimetype %d' % count}
    data = request.get_json()
    ip = data.get('ip') or ''
    if not check_params(ip, ipv4reg):
        return {'code': -1, 'msg':'invalid param %d' % count}
    return {'code': 0, 'msg':  '%d' % count}

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return {'code': 0, 'msg': 'ok'}


def parse_opt(argv):
    o = {'daemon': False}
    opts, args = getopt(argv, 'c:d', ['start', 'stop', 'restart', 'daemon', 'status'])
    for opt, arg in opts:
        if opt in ['-d', '--daemon']:
            o['daemon'] = True
        if opt == '--start':
            o['start'] = True
        if opt == '--stop':
            o['stop'] = True
        if opt == '--status':
            o['status'] = True
        if opt == '--restart':
            o['restart'] = True
        if opt == '-c':
            o['conf'] = arg
        
    return o

def stop(pidfile):
    if daemon.check_process(pidfile):
        daemon.stop_daemon(pidfile)

def start(pidfile, d=True):
    try:
        if d:
            daemon.daemonize(pidfile)
        svr = WSGIServer(('', 9999), app)
        svr.serve_forever() 
    except Exception as e:
        print(e)
        return 

def status(pidfile):
    if daemon.check_process(pidfile):
        print("Process running")
        return
    print("Process is inactived")

def main(): 
    opts = parse_opt(sys.argv[1:])
    pidfile = '/tmp/daemon.pid'

    if opts.get('stop'):
        stop(pidfile)
        return

    if opts.get('start'):
        start(pidfile, opts.get('daemon'))
        return

    if opts.get('status'):
        status(pidfile)
        return
    
    if opts.get('restart'):
        stop(pidfile)
        start(pidfile, True)

    print("%s [ -c | -d | --start | --stop | --daemon | --status | --restart ]" % sys.argv[0])
    if opts.get('conf'):
        print("conf file: %s" % opts.get('conf'))

if __name__ == '__main__':
    main()          
