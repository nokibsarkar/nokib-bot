import re
import json
import pywikibot as pb
r = pb.data.api.Request
b_numers = ["০", "১","২","৩","৪","৫","৬","৭","৮","৯"]
def en2bn(txt):
    txt = str(txt)
    st=""
    for i in txt:
        if(i.isdigit()):
            st+=numers[int(i)]
        else:
            st+=i
    return st
en = pb.Site("en","wikipedia")
bn = pb.Site("bn","wikipedia")
ref = re.compile("< *ref[^>]*>(?:(?!\< *\/ref *>).)+< *\/ref *>",re.DOTALL)
fil = re.compile("(?:\n*\*+ *|\n=+[^=]*=+\n|\{\|[^\|]+\||\s+[\.\,;\-]+\s*)",re.DOTALL|re.I)
inner = re.compile("\[\[ *(?:[^\]\|]+\|)?([^\]]+)\]\]")
image = re.compile("\[\[ *:? *(?:image|file|category) *:[^\]]+\]\]",re.I)
sep = re.compile(" +")
def count_word(txt):
    txt = ref.sub('',txt)
    txt = fil.sub('',txt)
    txt = image.sub('',txt)
    txt = inner.sub('\g<1>',txt)
    par = 0
    while True:
        length = len(txt)
        try:
            cursor = 0
            start = txt.index('{{')
            for i in range(start, length):
                if txt[i]=='{':
                    par+=1
                elif txt[i]=='}':
                    par-=1
                    if par==0:
                        txt = '%s%s' % (txt[:start], txt[i+1:])
                        break
                cursor = i
            if cursor == length - 1:
                break
        except:
            break
    return len(sep.split(txt))
n_articles = set()
def process(arts=[]):
    for i in arts:
        title = i['title']
        # check if already in bangla
        if('langlinks' in i):
            print("\tSkipping: '%s' already in bangla" % title)
            continue
        if(title in articles):
            print("\tSkipping: '%s' is already in the list" % title)
            continue
        if('revisions' not in i):
            skipped.add(title)
            print("\tSkipping: '%s' has no content" % title)
            continue
        wc = count_word(i["revisions"][0]["slots"]["main"]["*"])
        if(wc > 350 or wc < 150):
            print("\tSkipping: '%s' is very large and " % title)
            continue
        print("\tAdding %s"%title)
        n_articles.add(title)
# fetch already done list
patt = re.compile("\| *\[\[ *: *en *:([^\|\]]+)")
articles = patt.findall(pb.Page(bn,'উইকিপিডিয়া:নটর ডেম কর্মশালা ও এডিটাথন ২০২০/নিবন্ধ তালিকা').text)
articles = list(map(lambda x: x.strip(), articles))
def access(cat, count):
    skipped = set()
    print("Accessing %s" % cat)
    data = {
        "action": "query",
        "format": "json",
        "prop": "revisions|langlinks",
        "generator": "categorymembers",
        "rvprop": "content|size",
        "rvslots": "main",
        "lllang": "bn",
        "lllimit": "1",
        "gcmtitle": cat,
        "gcmtype": "page",
        "gcmlimit":"max"
        }
    res = r(site=en,parameters=data).submit()
    if 'query' not in res:
        print("Skipping %s" % cat)
        return 0
    arts = res['query']['pages'].values()
    process(arts)
    #Skipped articles
    print("Trying skipped articles")
    i = 0
    skipped = list(skipped) #json.loads(input("Enter article list"))
    l = len(skipped)
    data = {
            "action": "query",
            "format": "json",
            "prop": "revisions|langlinks",
            "rvprop": "content|size",
            "rvslots": "main",
            "lllang": "bn",
            "lllimit": "1",
            "titles":''
            }
    while(i < l):
        if i + 49 > l:
            data['titles'] = '|'.join(skipped[i:])
            i = l
        else:
            data['titles'] = '|'.join(skipped[i:i+49])
            i += 49
        res = r(site=en,parameters=data).submit()
        if 'query' not in res:
            print(res)
        arts = res['query']['pages'].values()
        process(arts)
    pg = pb.Page(bn,'User:নকীব বট/নিবন্ধ তালিকা/%s' % en2bn(count))
    pg.text = '{|class="wikitable"\n! বাংলা  \n! ইংরেজি\n! কাজ করছেন\n! জমাদানকৃত?\n! অবস্থা\n|-' if pg.text == "" else pg.text[:-2]
    for i in n_articles:
        s = '%s\n|[[]]\n|[[:en:%s|%s]]\n| \n| \n|\n|-' % (pg.text, i,i)
    pg.text = '%s\n|}' % pg.text
    pg.save()
    return 1
cats = [
"Category:Creepypasta",
"Category:Global ethics",
"Category:Environmental ethics",
"Category:English footballers",
"Category:American films",
"Category:Political Internet memes"
]
count = 4
for cat in cats:
    count += access(cat,count)