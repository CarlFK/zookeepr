#!/bin/bash -xe

# http://linkchecker.sourceforge.net/man1/linkchecker.1.html

SITE="http://2011.pyohio.org"
SITE="http://trist:5000"
# curl -s --cookie-jar po_auth.coki --data person.email_address=admin@zookeepr.org --data person.password=password  $SITE/person/signin 
# curl -s --cookie po_auth.coki $SITE/ |grep Sign
./lc.py > auth.coki

./linkchecker \
 --threads=-1 \
 --recursion-level=0 \
 --pause=1 \
http://trist:5000/admin/index

exit
 --cookiefile=auth.coki \
 --no-warnings \
# $SITE
