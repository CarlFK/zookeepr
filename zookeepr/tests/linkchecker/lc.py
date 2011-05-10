#!/usr/bin/python

import cookielib, urllib2
import sys

host = 'trist:5000'
url = 'http://%s/person/signin' % (host,)
data = 'person.email_address=admin@zookeepr.org&person.password=password'

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
r = opener.open(url,data)

url2= r.geturl()
if url2  == 'http://%s/register/status' % (host,):
    # login redirects to this page
    # so continue

    # make a cookie file that looks like this:
    # note: docs show quotes around ="value" - the qutoes are not syntax.
    """
    Host: example.org
    Set-cookie: baggage=elitist
    Set-cookie: comment=hologram
    """
    print "Host: %s" % (host,)
    baggage="elitist"; comment="hologram"
    for c in cj: 
        print 'Set-cookie: %s=%s' % (c.name, c.value)
    sys.exit(0)

else:
    # login failed, try to debug

    h = r.read()
    for line in h.split('\n'):
        if "sign" in line.lower():
            print line

    sys.exit(1)
