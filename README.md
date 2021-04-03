# cert-checker

❯ ansible-doc -M ansible/playbooks/library cert_checker
> CERT_CHECKER    (/Users/gsp/python/cert-checker/ansible/playbooks/library/cert_checker.py)

        The module connects to a lists of hosts sequentially on a given port and reports whether cert will expire before the number of days specified in a variable

OPTIONS (= is mandatory):

- alert_on_days_before_expiry
        The number of days between now and the cert expiry date, that will trigger an email. In other words if this variable is less or equal to the number of days
        left to reach the cert expiration date, an email will be triggered. If set to 60, an email will be fired for any cert expiring in 60 or less days from now.
        [Default: (null)]

- from_address
        The From address field in the header of the email
        [Default: (null)]

- port
        Port where the TLS service is listening on
        [Default: (null)]

= send_mail
        Sends alert_email if condition is met
        [Default: True]

= server
        FQDN of the server to check


- timeout
        The number of seconds we wait for the socket to go into the ESTABLISHED state
        [Default: 6 seconds]

= to_address
        The recipient field written in the email header



AUTHOR: Aliep Alberto Gonzalez y Diaz a.k.a el bankero solitario  elbankero@toomuchmoney.com

EXAMPLES:

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

Installation