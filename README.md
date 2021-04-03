# Cert Checker


    ansible-doc -M ansible/playbooks/library cert_checker
        CERT_CHECKER    (/Users/gsp/python/cert-checker/ansible/playbooks/library/cert_checker.py)
    
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
    
    
    **_AUTHOR: A.A.G.D a.k.a el bankero solitario elbankero@toomuchmoney.com_**
    
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
        
    
     
Installation:

    Clone the repo
    cd cert-checker
    create virtualenv using:
         python3 -m venv venv
    activate the venv:
        source venv/bin/activate
    install ansible:
        pip3 install ansible
    run with:
        ansible-playbook ansible/playbooks/cert-checker.yaml --tags all_servers
        adjust the address and the 'alert_on_days_before_expiry' vars accordingly
    output:
     ansible-playbook ansible/playbooks/cert-checker.yaml --tags all_servers
    
    PLAY [Check certs] *****************************************************************************************************************************************************************************************
    
    TASK [cert-checker : Exec cert check on all  servers] ******************************************************************************************************************************************************
    ok: [localhost] => (item={'key': 'www.oracle.com', 'value': {'group': 'database', 'port': 443}})
    ok: [localhost] => (item={'key': 'www.postgresql.org', 'value': {'group': 'database', 'port': 443}})
    ok: [localhost] => (item={'key': 'www.rbc.com', 'value': {'port': 443, 'group': 'finance'}})
    ok: [localhost] => (item={'key': 'www.abc.es', 'value': {'port': 443, 'group': 'news'}})
    ok: [localhost] => (item={'key': 'cuba.cu', 'value': {'port': 80, 'group': 'news'}})
    
    PLAY RECAP *************************************************************************************************************************************************************************************************
    localhost                  : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
    
    ❯ mail
    Mail version 8.1 6/6/93.  Type ? for help.
    "/var/mail/gsp": 4 messages 4 unread
    >U  1 gsp@Georges-MacBook-  Sat Apr  3 13:38  15/671   "Alert SSL server certificate for server www.oracle.com expiring in 225 days"
     U  2 gsp@Georges-MacBook-  Sat Apr  3 13:38  15/677   "Alert SSL server certificate for server www.postgresql.org expiring in 55 days"
     U  3 gsp@Georges-MacBook-  Sat Apr  3 13:38  15/665   "Alert SSL server certificate for server www.rbc.com expiring in 233 days"
     U  4 gsp@Georges-MacBook-  Sat Apr  3 13:38  15/663   "Alert SSL server certificate for server www.abc.es expiring in 137 days"
    ? 2
    Message 2:
    From gsp@Georges-MacBook-Pro.local  Sat Apr  3 13:38:29 2021
    X-Original-To: gsp
    Delivered-To: gsp@Georges-MacBook-Pro.local
    To: gsp@Georges-MacBook-Pro.local
    Subject:  Alert SSL server certificate for server www.postgresql.org expiring in 55 days
    Date: Sat,  3 Apr 2021 13:38:29 -0400 (EDT)
    From: gsp@Georges-MacBook-Pro.local (George San Pedro)
    
    **Certificate for: www.postgresql.org will expire on: 2021-05-28 which is 55 days ahead**