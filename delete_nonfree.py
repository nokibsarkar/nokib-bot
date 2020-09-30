import pywikibot as pb
import re
from datetime import datetime as dt
now = dt.utcnow()
bn = pb.Site('test','wikipedia')
bn.login()
r = pb.data.api.Request
ISO = "%Y-%m-%dT%H:%M:%SZ"
furd_template = re.compile('\{\{ *মুক্ত নয় হ্রাসকৃত[^\}]*\}\}\s*')
csrf = bn.get_tokens(['csrf'])['csrf']
reason = u'বট কর্তৃক অ-মুক্ত চিত্রের পূর্ণ সংস্করণসমূহ সম্ভাব্য অ-ন্যায্য ব্যবহার বিবেচনা মুছে ফেলা হয়েছে'
limit = 5 #float('inf') #---- How many revisions to delete in total
def fetch_revs(pageid):
    pageid = str(pageid)
    data = {
    	'action':'query',
    	'format':'json',
    	'utf8':1,
    	'prop':'revisions',
    	'rvslots':'main',
    	'rvlimit':'max',
    	'rvprop':'user|ids',
    	'pageids':pageid
    	}
    res = r(bn,parameters=data).submit()['query']['pages'][pageid]
    return res['revisions']
def delete(name,ids):
    global csrf
    data = {
	    "action": "revisiondelete",
	    "format": "json",
	    "type": "oldimage",
      "target": name,
	    "ids": ids,
	    "hide": "content",
	    "reason": reason,
	    #"tags": "কপিরাইট লঙ্ঘন",
	    "token": csrf
}
    res = r(bn,parameters=data).submit()
    print(res)
    if 'error' in res:
        if res['error']['code'] == 'badtoken':
            csrf = bn.get_tokens(['csrf'])['csrf']
            return delete(name,ids)
        print("Error occurred: ",res)
        return False
    return True
def main():
    cat = pb.Category(bn,'Category:মুক্ত নয় হ্রাসকৃত ফাইল').articles(namespaces=6)
    for i in cat:
        if i.title()[:-4].lower() is '.svg':
            # skip the svg files
            continue
        i = pb.FilePage(i)
        i.text, n = furd_template.subn('',i.text,1)
        if n is 0:
            # no template was defined
            continue
        revs = fetch_revs(i.pageid) # except the first one
        if (now - i.latest_file_info.timestamp).days < 7:
            # The latest upload is not expired of 7 days
            continue
        revs = revs[1:]
        ids = []
        for rev in revs:
            #mark for deletion
            ids.append(rev['revid'])
        if(len(ids)):
            delete(
               	i.title(),
            	   ids
            	) and i.save(
            	   u'পূর্বের সংস্করণগুলো মুছে ফেলায় {{মুক্ত নয় হ্রাসকৃত}} টেমপ্লেট অপসারণ'
            	)