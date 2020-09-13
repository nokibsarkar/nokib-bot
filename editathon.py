from setup import *
config = config['auditEditathon']
content = u"""'''তালিকাটি একটি [[ব্যবহারকারী:নকীব বট|বটের]] মাধ্যমে হালনাগাদ করা হয়। সুতরাং আপনি যদি হাতে কোনো হালনাগাদ করেও থাকেন, তবে পরবর্তী হালনাগাদের সময় আপনার সম্পাদনা বাতিল হয়ে যেতে পারে।
সর্বশেষ হালনাগাদের সময়: {{সময় আগে|%s}}'''""" % dt.datetime.utcnow().isoformat()[:19]
def date_diff(d):
    d = dt.datetime.strptime(d,ISO)
    d = (now - d).total_seconds()
    if d < 3600:
        #less than an hour
        return 'এক ঘন্টারও কম সময় পূর্বে'
    if d < 86400:
        #less than a day but more than an hour
        d = int(d*0.000277777)
        return '%s ঘন্টা পূর্বে' % en2bn(d)
    #less than a day but more than an hour
    d = int(d*0.00001157407)
    return '%s দিন পূর্বে' % en2bn(d)

def fetch(m):
    global content
    txt = m.group(2)
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
    st = '%s\n==' % content + m.group(1) + '==\n{|class="wikitable sortable" style="width:100%"\n|-\n!ক্রম!!নিবন্ধ!!ইংরেজি!!আকার!!সর্বশেষ সম্পাদনা\n|-\n'
    for i in range(len(data['titles'])):
        j = mp[data['titles'][i]]
        st += '|%s|| [[%s]] || %s || %s ||%s\n|-\n' % (
        	en2bn(i + 1),data['titles'][i], engs[i], j[0], j[1]
        	)
    content = st + '|}'
    return ''
def summary():
    sects = config['sections']
    patt = re.compile(
	    '\n== *({0}) *==\n((?:(?!\n== *(?:{0}) *==\n).)+)'.format('|'.join(sects)),
	    re.DOTALL
    )
    source = pb.Page(bn,config['source'])
    target = pb.Page(bn,config['target'])
    patt.sub(fetch,source.text)
    target.text = content
    target.save(u"এডিটাথনের নিবন্ধ তালিকার অবস্থা হালনাগাদ করা হয়েছে")
summary()