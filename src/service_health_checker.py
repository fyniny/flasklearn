#!/bin/python3
# run as root

import yaml
import os
import logging
import requests
from subprocess import PIPE, Popen
import sys

service_conf = 'service.yml'
logfile = 'svr.checker.log'

logging.basicConfig(filename=logfile,
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s %(pathname)s:%(lineno)d %(funcName)s %(message)s')

def read_conf():
    if not os.path.exists(service_conf):
        logging.error('Service configuration file not found')
        sys.exit(1)
    with open(service_conf, 'r') as f:
        svrconf = yaml.safe_load(f)

    tmplist = svrconf.get('services') or []
    svrlist = []
    logging.info('check service configuration')
    for tmp in tmplist:
        if tmp.__contains__('name') \
            and tmp.__contains__('url') \
                and tmp.__contains__('start_cmd') \
                    and tmp.__contains__('user'):
                        svrlist.append(tmp)
                        logging.info('configuration item is ok')
        logging.warning('configuration item is invalid, ignore(%s)' % tmp)
    
    logging.debug('svrlist "%s"', svrlist)
    return svrlist

def check_and_start_svr(svrlist):
    for svr in svrlist:
        try:
            requests.get(svr.get('url'), timeout=30)
            logging.info('service checker: service [%s] is running' % svr.get('name'))
        except Exception:
            logging.warning('service checker: service [%s] is closed, starting now' % svr.get('name'))
            shellcmd = ['su', '-c', 'bash -c \"%s\"' % svr.get('start_cmd'), '-', svr.get('user')]
            logging.debug('shell cmd = "%s"' % shellcmd)
            ins = Popen(shellcmd, stdin=PIPE, stdout=PIPE)
            ins.communicate(timeout=30)
            if ins.returncode != 0:
                logging.error('service checker: service [%s] is closed, and started failedly' % svr.get('name'))
                continue
            logging.info('service checker: service [%s] starts running' % svr.get('name'))

if __name__ == '__main__':
    if os.geteuid() != 0:
        logging.warning('service checker must be running as root user')
        sys.exit(1)
    svrlist = read_conf()
    check_and_start_svr(svrlist)
