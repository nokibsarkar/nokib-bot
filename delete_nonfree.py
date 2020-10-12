from environment import *
# previously 
bn.login()
tracker = "Category:হ্রাসকৃত অ-মুক্ত ফাইল"
archiveID = re.compile("\/archive\/[^\/]+\/[^\/]+\/(\d+)")
furd_template = re.compile('\s*\{\{ *মুক্ত নয় হ্রাসকৃত[^\}]*\}\}\s*')
try:
    csrf = bn.get_tokens(['csrf'])['csrf']
except KeyError as e:
    print("CSRF Token could not be fetched. May be you have not logged in")
    exit()
reason = u'[[উইকিপিডিয়া:চ৫|চ৫]] অনুসারে অ-মুক্ত চিত্রের পূর্ববর্তী সংস্করণ মুছে ফেলা হয়েছে'
summary = u'অ-মুক্ত চিত্রের পূর্ববর্তী সংস্করণ মুছে ফেলায় {{মুক্ত নয় হ্রাসকৃত}} অপসারণ'
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
	    "prop": "imageinfo",
	    "generator": "categorymembers",
	    "utf8": 1,
	    "iiprop": "url|timestamp",
	    "iilimit": "max",
	    "iilocalonly": 1,
	    "gcmtitle": tracker,
	    "gcmtype": "file",
	    "gcmlimit": "max"
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
                print("SVG found")
                continue
            infos = i['imageinfo']
            if((now - dt.datetime.strptime(infos[0]['timestamp'], ISO)).days < 7):
                	print("7 days did not pass")
                	continue
            #if 'templates' not in i:
                #print("Skip as not template was found")
                #continue
            ids = []
            for j in infos[1:]:
                if 'url' in j:
                    k = archiveID.search(j['url'])
                    if(k):
                        ids.append(k.group(1))
            if len(ids) == 0:
                print("No version was deletable for %s" % name)
                continue
            try:
                delete(name, ids)
                i = pb.FilePage(bn,name)
                i.text = furd_template.sub( '', i.text, 1)
                i.save(summary)
            except Exception as e:
                print("Something occurred:%s" % e)
main()
