#!/usr/bin/env python
# -*- coding: utf-8 -*-

ANSIBLE_MATADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'bankero@rbc.com'
}

DOCUMENTATION = '''
---
module: cert_checker

short_description: Module to report on soon to expire certs as defined by a variable

version_added: "1.0"

description:
    - "The module connects to a lists of hosts sequentially on a given port and reports whether cert will expire before 
    the number of days specified in a variable"

options:
        
    send_mail:
        description:
            - Sends alert_email if condition is met
        required: true
        default: true
    from_address:
        description:
            - The From address field in the header of the email
    to_address:
        description:
            - The recipient field written in the email header
        required: true
    server:
        description:
            - FQDN of the server to check
        required: true
    port:
        description:
            - Port where the TLS service is listening on
        required: False
        
    alert_on_days_before_expiry:
        description:
            - "The number of days between now and the cert expiry date, that will trigger an email. In other words
            if this variable is less or equal to the number of days left to reach the cert expiration date, an email
            will be triggered. If set to 60, an email will be fired for any cert expiring in 60 or less days from now."
            
    timeout:
        description:
            - The number of seconds we wait for the socket to go into the ESTABLISHED state
        required: false
        default: 6 seconds
author:
    - Aliep Alberto Gonzalez y Diaz a.k.a el bankero solitario  elbankero@toomuchmoney.com
'''

EXAMPLES = r'''
- name: Exec cert check on all  servers
  cert_checker:
    port: "{{ item.value.port | d(443) }}"
    send_mail: "{{ item.value.send_mail | d(true) }}"
    from_address: 'certchecker@bankero.com'
    to_address: 'gsp'
    servers: "{{ item.key }}"
    timeout: "{{ timeout | d(6) }}"
    alert_on_days_before_expiry: "{{ alert_on_days_before_expiry | d(30) }}"
  with_dict: "{{ servers }}"
  tags:
    - all_servers
    
send_mail: True
alert_on_days_before_expiry: 5000
timeout: 4
from_address: 'certchecker@bankero.com'
to_address: 'gsp'
port: 443


servers:
  www.oracle.com:
    group: database
    port: 443
  www.postgresql.org:
    group: database
    port: 443
  www.rbc.com:
    port: 443
    group: finance
  www.abc.es:
    port: 443 # No port given take default
    group: news
  cuba.cu:
    port: 80 # No SSL here should not exit
    group: news
    send_mail: False # do not send mail regardless of the expiration date
  www.network.com:
    port: 58292 # test conn timeout, random port likely to be closed
    group: news
'''
import datetime
import socket
import ssl
import subprocess


def ssl_expiry_datetime(server, port, timeout, module):
    # ssl_info['subject'][-1:][0][0][-1:][0]
    ssl_context = ssl.create_default_context()

    try:
        with socket.create_connection((server, port), timeout) as sock:
            with ssl_context.wrap_socket(sock, server_hostname=server, do_handshake_on_connect=True) as ssock:
                ssock.settimeout(timeout)
                if ssock:
                    ssl_info = ssock.getpeercert()
    except (socket.gaierror, socket.timeout, socket.error):
        pass
        return
    except Exception as e:
        module.fail_json(msg=f'Error in connecting to server: {server}: {e}')
        return
    return ssl_info


def call_to_mailx(server, expire_date, days_to_live, module, from_address, to_address):
    subject = f'Alert SSL server certificate for server {server} expiring in {str(days_to_live)} days'
    msg_body = f'Certificate for: {server} will expire on: {expire_date.strftime("%Y-%m-%d")} which is {str(days_to_live)} days ahead'
    echo = subprocess.Popen(['echo', f'{msg_body}'], stdout=subprocess.PIPE)
    mail = subprocess.Popen(['mailx', f'-s {subject}', f'{to_address}'], stdin=echo.stdout)
    stdout, stderr = mail.communicate()
    if stderr or stdout:
        module.fail_json(msg=f'Error: {stderr.decode("utf-8")}')
    return


def main():
    module = AnsibleModule(argument_spec=dict(
        send_mail=dict(required=True, type='bool'),
        servers=dict(required=True, type='str'),
        alert_on_days_before_expiry=dict(required=True, type='int'),
        port=dict(required=False, type='str'),
        from_address=dict(required=True, type='str'),
        to_address=dict(required=True, type='str'),
        group=dict(required=False, type='str'),
        timeout=dict(required=False, type='int'))
    )

    servers = module.params['servers']
    port = module.params['port']
    send_mail = module.params['send_mail']
    timeout = module.params['timeout']
    alert_on_days_before_expiry = module.params['alert_on_days_before_expiry']
    from_address = module.params['from_address']
    to_address = module.params['to_address']

    now = datetime.datetime.now()
    ssl_dateformat = r'%b %d %H:%M:%S %Y %Z'
    try:
        ssl_info = ssl_expiry_datetime(servers, port, timeout, module)
        if ssl_info:
            expire_date = datetime.datetime.strptime(ssl_info['notAfter'], ssl_dateformat)
            if expire_date:
                days_to_live = expire_date - now
                if int(days_to_live.days) <= int(alert_on_days_before_expiry) and send_mail:
                    call_to_mailx(servers, expire_date, days_to_live.days, module, from_address, to_address)
    except Exception as e:
        module.fail_json(msg=f'Error is: {e}')

    module.exit_json(changed=False)


from ansible.module_utils.basic import AnsibleModule

main()
