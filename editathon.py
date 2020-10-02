from environment import *
# previously from setup import *
bn.login()
config = config['auditEditathon']
content = u"""{{ব্যবহারকারী:নকীব বট/সতর্কবার্তা}}
'''<big>সর্বশেষ হালনাগাদের সময়: {{সময় আগে|%s|purge=y}}</big>'''""" % dt.datetime.utcnow().isoformat()[:19]
def date_diff(d):
    d = dt.datetime.strptime(d,ISO)
    d = (now - d).days
    if d is 0:
        #less than an hour
        return 'এক দিনেরও কম সময় পূর্বে'
    return '%s দিন পূর্বে' % en2bn(d)

def fetch(m):
    global content
    txt = m.group(3)
    articles = re.compile(
    	"\| *[০১২৩৪৫৬৭৮৯]+ *\|\| *\[\[([^\]\|]+)(?:\|[^\]]+)?\]\] *\|\|((?:(?!\|\|).)+)"
    	)
    data = {
    	"action": "query",
	   "format": "json",
	   "prop": "revisions|categories",
	   "utf8": 1,
	   "rvprop": "timestamp|size",
	   "rvslots": "main",
	   "clcategories":u"বিষয়শ্রেণী:কাজ চলছে"
    }
    engs = []
    data["titles"] = [
     engs.append(i[1]) or i[0].strip() for i in articles.findall(txt)
    ]
    if len(data['titles']) == 0:
        return ''
    res = r(site=bn,parameters=data).submit()['query']['pages'].values()
    mp = dict(
    	[(i['title'],(en2bn(i['revisions'][0]['size']),date_diff(i['revisions'][0]['timestamp'])) if 'missing' not in i else ('','')) for i in res]
    )
    st = '%s\n%s' % (content, m.group(1)) + m.group(2).strip() + m.group(1) +'\n{|class="wikitable sortable" style="width:100%"\n|-\n!ক্রম!!নিবন্ধ!!ইংরেজি!!আকার!!সর্বশেষ সম্পাদনা\n|-\n'
    for i in range(len(data['titles'])):
        j = mp[data['titles'][i]]
        st += '|%s|| [[%s]] || %s || %s ||%s\n|-\n' % (
        	en2bn(i + 1),data['titles'][i], engs[i], j[0], j[1]
        	)
    content = st + '|}'
    return ''
def summary():
    patt = re.compile(
	    '\n(==+) *([^=]+)==+\n((?:(?!\n==+ *(?:[^=]+)==+\n).)+)',
	    re.DOTALL
    )
    source = pb.Page(bn,config['source'])
    target = pb.Page(bn,config['target'])
    patt.sub(fetch,source.text)
    target.text = content
    target.save(u"এডিটাথনের নিবন্ধ তালিকার অবস্থা হালনাগাদ করা হয়েছে")
summary()