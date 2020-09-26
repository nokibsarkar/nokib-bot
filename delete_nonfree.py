import pywikibot as pb
import re
from datetime import datetime as dt
now = dt.utcnow()
bn = pb.Site('bn','wikipedia')
bn.login()
r = pb.data.api.Request
ISO = "%Y-%m-%dT%H:%M:%SZ"
furd_template = re.compile('\{\{ *মুক্ত নয় হ্রাসকৃত[^\}]*\}\}\s*')
csrf = bn.get_tokens(['csrf'])['csrf']
reason = u'বট কর্তৃক অ-মুক্ত চিত্রের পূর্ণ সংস্করণসমূহ সম্ভাব্য অ-ন্যায্য ব্যবহার বিবেচনা মুছে ফেলা হয়েছে'
limit = 5#00
def fetch_revs(pageid):
    pageid = str(pageid)
    data = {
    	'action':'query',
    	'format':'json',
    	'utf8':1,
    	'prop':'revisions',
    	'rvslots':'main',
    	'rvlimit':'max',
    	'rvprop':'user|timestamp|ids',
    	'pageids':pageid
    	}
    res = r(bn,parameters=data).submit()['query']['pages'][pageid]
    return res['revisions']
def delete(ids):
    global csrf
    data = {
	      "action": "revisiondelete",
	      "format": "json",
	      "type": "oldimage",
	      "ids": ids,
	      "hide": "content",
	      "reason": reason,
	      "token": csrf
    }
    res = r(bn,parameters=data).submit()
    if 'error' in res:
        if res['error']['code'] == 'badtoken':
            csrf = bn.get_tokens(['csrf'])['csrf']
            return delete(ids)
        print("Error occurred: ",res)
        return False
    return True
def main():
    cat = pb.Category(bn,'Category:মুক্ত নয় হ্রাসকৃত ফাইল').articles(namespaces=6)
    ids = []
    l = 0
    for i in cat:
        l1 = 0
        if i.title()[:-4].lower() is '.svg':
            # skip the svg files
            continue
        i = pb.FilePage(i)
        i.text, n = furd_template.subn('',i.text,1)
        if n is 0:
            # no template was defined
            continue
        revs = fetch_revs(i.pageid) # except the first one
        timestamp = dt.strptime(revs[0]['timestamp'], ISO) #Parse the timestamp
        if (now - timestamp).days < 7:
            # The latest upload is not expired of 7 days
            continue
        revs = revs[1:]
        if l is 5:
            break
        for rev in revs:
            #mark for deletion
            ids.append(rev['revid'])
            l += 1
            l1 += 1
            if l == limit:
                if(delete(ids)):
                    print(" Deleted All the revisions")
                    ids = []
                    l = 0
                    #break
        #l1 and i.save(u'পূর্বের সংস্করণগুলো মুছে ফেলায় {{মুক্ত নয় হ্রাসকৃত}} টেমপ্লেট অপসারণ')
    delete(ids)
    print("Deleted %d revisions" % len(ids))
main()