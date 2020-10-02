import pywikibot as pb
import re
from datetime import datetime as dt
now = dt.utcnow()
bn = pb.Site('test','wikipedia')
bn.login()
r = pb.data.api.Request
ISO = "%Y-%m-%dT%H:%M:%SZ"
tracker = "Category:মুক্ত নয় হ্রাসকৃত ফাইল"
archiveID = re.compile("\/archive\/[^\/]+\/[^\/]+\/(\d+)")
furd_template = re.compile('\{\{ *মুক্ত নয় হ্রাসকৃত[^\}]*\}\}\s*')
csrf = bn.get_tokens(['csrf'])['csrf']
reason = u'বট কর্তৃক অ-মুক্ত চিত্রের পূর্ণ সংস্করণসমূহ সম্ভাব্য অ-ন্যায্য ব্যবহার বিবেচনা মুছে ফেলা হয়েছে'
summary = u'অ-মুক্ত চিত্রের পূর্ববর্তী সংস্করণসমূহ মুছে ফেলায় {{মুক্ত নয় হ্রাসকৃত}} অপসারণ'
limit = 5 #float('inf') #---- How many revisions to delete in total
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
    data = {
	    "action": "query",
	    "format": "json",
	    "prop": "imageinfo|revisions",
	    "generator": "categorymembers",
	    "utf8": 1,
	    "iiprop": "user|url|timestamp",
	    "iilimit": "max",
	    "iilocalonly": 1,
	    "gcmtitle": tracker,
	    "gcmtype": "file",
	    "rvprop":"content",
	    "rvslots":"main",
	    "gcmlimit":"max"
    }
    c = True
    while(c):
        batch = r(bn,parameters=data).submit()
        c = 'query-continue' in batch
        if(c):
            data['gcmcontinue'] = batch['query-continue']['categorymembers']['gcmcontinue']
        batch = batch['query']['pages']
        for i in batch:
            i = batch[i]
            name = i['title']
            if name[-4:].lower() == '.svg':
                #print("SVG found")
                continue
            infos = i['imageinfo']
            if((now - dt.strptime(infos[0]['timestamp'], ISO)).days < 7):
                	#print("7 days did not pass")
                	continue
            rev = i['revisions'][0]['slots']['main']['*']
            rev, n = furd_template.subn( '', rev, 1)
            if n is 0:
                #print("Skip as not template was found")
                continue
            ids = []
            for j in infos[1:]:
                if 'url' in j:
                    k = archiveID.search(j['url'])
                    if(k):
                        ids.append(k.group(1))
            if len(ids) is 0:
                # No version was deleted
                continue
            try:
                delete(name, ids)
                i = pb.FilePage(bn,name)
                i.text = rev
                i.save(summary)
            except Exception as e:
                print("Something occurred:%s" % e)
main()