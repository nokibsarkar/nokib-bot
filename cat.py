# -*- coding: utf-8 -*
import pywikibot as pb
import json
import re
import datetime as dt
import time

now = dt.datetime.now()
bn = pb.Site("bn","wikipedia")
r = pb.data.api.Request
ISO = "%Y-%m-%dT%H:%M:%SZ"
is_no_ref = re.compile('<\/ *ref>|\{\{ *sfn *\|')
ref_space = re.compile("<\/ref>\s+<ref")
p_ref = re.compile("(। *)*(?P<ref>(<ref([^>]+)?>((?!<\/ref>)[\s\S])+<\/ref>\s*)+)(। *)+")
month = ["জানুয়ারি","ফেব্রুয়ারি","মার্চ","এপ্রিল","মে","জুন","জুলাই","আগস্ট","সেপ্টেম্বর","অক্টোবর","নভেম্বর","ডিসেম্বর"]
p_space = re.compile('(\S)(।+| +।+ *| *।+ {2,})+(<ref|\}\}|\{\{|\]\]|"|\S)')
interwiki = re.compile("\[\[ *:? *(?P<lang>[a-z]{2}) *:([^\|]+\|)?(?P<link>[^\]]+)\]\]")
talk_temp = re.compile(u"\{\{ *(?:আলাপ পাতা|[tT]alk page) *[\|\}]")
def p_space_s(match):
    global p_count
    l = match.group(3)
    if(match.group(2)!="। "):
        p_count+=1
    if len(l) is 1 and l not in skipTokens:
        return match.group(1)+"। "+l
    return match.group(1) + "।" + l
numers_bn = {"০":"0","১":"1", "২":"2", "৩":"3", "৪":"4", "৫":"5","৬":"6", "৭":"7","৮":"8", "৯":"9"}
working = re.compile("\{\{ *কাজ চলছে[^\}]*\}\}")
def correct(txt):
    if config['generalCorrection']['status'] is False:
        return [], txt
    global p_count
    summary = []
    ref = is_no_ref.search(txt) # check for refernces
    n = p_space.sub(p_space_s,txt)
    if(p_count):
        summary.append(u"দাঁড়ির অব্যবহিত পূর্বের ফাঁকাস্থান অপসারণ ও পরে একটি ফাঁকাস্থান যোগ")
        txt = n
        p_count = 0
    if(ref and config['generalCorrection']['shiftReference']):
        n = p_ref.subn("।\g<ref> ",txt)
        if(n[1]):
            summary.append("তথ্যসূত্র দাঁড়ির অব্যবহিত পরে স্থাপন ও তার পরে একটি ফাঁকাস্থান যোগ")
            txt = n[0]
        n = ref_space.subn("</ref><ref",txt)
        if(n[1]):
            summary.append("দুটি তথ্যসূত্রের মাঝের ফাঁকাস্থান অপসারণ")
            txt = n[0]
    elif(noref_c.search(txt) is None and config['generalCorrection']['addNoRef']):
        txt = noref_t + txt
        summary.append("{{উৎসহীন}} যোগ")
    if(summary!=[]):
        summary[0] ="সাধারণ পরিষ্করণ: "+summary[0]
    return summary, txt
p_count = 0
REF = ['০','১','২','৩','৪','৫','৬','৭','৮','৯'] # numer map
def en2bn(txt):
    txt = str(txt)
    s = ""
    for i in txt:
        try:
            s+= REF[int(i)]
        except:
            s+=i
    return s
noref_t = "{{উৎসহীন|date="+month[now.month -1] +" " + en2bn(now.year)+"}}\n"
noref_c = re.compile("\{\{\s*উৎসহীন\s*")
config =json.loads(pb.Page(bn,"user:নকীব বট/config.json").text)
skipTokens = config['generalCorrection']['spaceAfterPeriod']['singleSkipToken']
settings = json.loads(open("setting.json","r").read())
tagged = re.compile("\{\{ *আন্তঃউইকিসংযোগ প্রয়োজন *\}\}")
def has_iw(pageid):
    data = {
    "action": "query",
    "format": "json",
    "prop": "langlinkscount|pageprops",
    "pageids": pageid,
    "utf8": 1,
    "ppprop": "wikibase_item"
    }
    res = r(bn,parameters=data).submit()["query"]["pages"][pageid]
    return "pageprops" in res or "langlinkscount" in res
def patrolRecentChange():
    rc_start = settings["patrolRC"]["last_access"]
    rc_end = (now - dt.timedelta(hours=48)).strftime(ISO)
    work_end = now - dt.timedelta(days=config["workingTemplate"]["minDay"])
    data1 = {
    "action": "query",
    "format": "json",
    "utf8": True
    }
    data2 = {
          
       "list": "recentchanges",
       "rcstart": rc_start,
       "rcend": rc_end,
       "rcdir": "newer",
       "rcnamespace": "0",
       "rcprop": "title|timestamp|comment|ids",
       "rcshow": "!bot|!redirect",
       "rctype": "new",
        "rclimit":"max"
    }
    data3 = {
      "prop": "revisions",
      "rvprop": "timestamp|size",
      "generator": "categorymembers",
      "gcmtitle": u"বিষয়শ্রেণী:কাজ চলছে",
      "gcmtype": "page",
       "gcmlimit":"max",
      "gcmnamespace":"0",
        "gcmdir":"newer",
    "gcmsort": "timestamp",
      "gcmend": work_end
      }
    c = True
    while(c):
        data= dict(list(data1.items()) + list(data2.items()) + list(data3.items()))
        batch = r(bn,parameters=data).submit()
        #print(batch)
        c = "query-continue" in batch
        if(c):
            if("recentchanges" in batch["query-continue"]):
                data2["rccontinue"] = batch["query-continue"]["recentchanges"]["rccontinue"]
            else:
                data2={}
            if("categorymembers" in batch["query-continue"]):
                data3["gcmcontinue"] = batch["query-continue"]["categorymembers"]["gcmcontinue"]
            else:
                data3 = {}
        query = batch["query"]
        work = settings["patrolRC"]["backlog"]
        settings["patrolRC"]["backlog"] = []
        patrollable = []
        if("recentchanges" in query):
            patrollable = query["recentchanges"]
        if("pages" in query):
            work += list(query["pages"].values())
        if(config["workingTemplate"]["status"]): #access for working template
            for i in work:
                j = pb.Page(bn,i["title"])
                if "revisions" not in i:
                    print(i)
                    continue
                i=i["revisions"][0]
                if((now - dt.datetime.strptime(i["timestamp"],ISO)).days < config["workingTemplate"]["minDay"] or i["size"] < config["workingTemplate"]["minSize"]):
                    # not old and rich enough
                    continue
                summary, j.text = correct(j.text)
                summary.append(u"{{কাজ চলছে}} টেমপ্লেট অপসারণ")
                j.text = working.sub("", j.text,1)
                try:
                    if(summary==[]):
                        continue
                    summary[0] = u"সাধারণ পরিষ্করণ"+summary[0]
                    summary = ", ". join(summary)
                    j.save(summary)
                except:
                    pass
         #---- patrol New pages ----- #
        if(config["patrolRecentchanges"]["status"]):
            for i in patrollable:
                pg = pb.Page(bn, i["title"])
                if(pg.exists() is False or pg.isDisambig()):
                    continue
                #----Add {{talk page}}
                talk = pg
                if('Talk:'!= talk.namespace()):
                    talk = pg.toggleTalkPage()
                if(talk.namespace() == 'Talk:' and (talk.exists() == False or talk_temp.search(talk.text)==None)):
                    talk.text = u'{{আলাপ পাতা}}\n' + talk.text
                    talk.save(u"বট কর্তৃক আলাপ পাতায় {{আলাপ পাতা}} যোগ")
                #----
                summary = []
                if("অনুবাদ" in i["comment"]):
                    # the page has been translated
                    iw = has_iw(str(i["pageid"]))
                    if(iw is False): # interwiki not found
                        iw = interwiki.search(i["comment"])
                        if(iw):
                            iw = iw.group("lang")+":"+iw.group("link")
                            pg.text+= "\n[["+iw+"]]"
                            summary.append("আন্তঃউইকিসংযোগ স্থাপন ("+iw+"); ")
                        elif tagged.search(pg.text) is None:
                            pg.text = "{{আন্তঃউইকিসংযোগ প্রয়োজন}}\n" + pg.text
                            summary.append("{{আন্তঃউইকিসংযোগ প্রয়োজন}} যোগ; ")
                if(working.search(pg.text)):
                    settings["patrolRC"]["backlog"].append(i)
                    continue
                i, pg.text = correct(pg.text) # General correction
                summary += i
                try:
                    if(summary==[]):
                        continue
                    summary = ", ".join(summary)
                    pg.save(summary)
                except:
                    pass
    settings["patrolRC"]["last_access"] = rc_end
def manageCategory(site,conf):
    redirects = site.allpages(filterredir=True,namespace="Category",content=True)
    temp = "{{"+conf["template"]+"|%s}}"
    editcount = 0
    if(conf["patrolRequest"]["status"]):
        temp+="\n"+conf["patrolRequest"]["tracker"]
    f="# *("+conf["red_patt"]+") *\[\[ *:? *(("+conf["cat_patt"]+")( *:)+ *)(?P<target>[^\]\|]+)"
    fetch_t = re.compile(f)
    lag = 60 // conf["test"]["rate"]
    f_target = re.compile("\{\{ *("+conf["temp_patt"]+") *\| *(?P<ns>:? *("+conf["cat_patt"]+") *: *)?(?P<target>([^\}\|]+))")
    for i in redirects:
        target = fetch_t.search(i.text)
        if target is None:
            i.text = "{{db-r2|bot=নকীব বট}}\n" + i.text
            conf['proposeDeletion'] and i.botMayEdit() and i.save("Adding deletion request for cross namespace redirect")
            continue
        target = target.group("target")
        i.text = temp % target
        i.save(conf["red_summary"])
        editcount+=1
        if(editcount >= conf["test"]["count"]):
            return
        time.sleep(lag)
    cats = pb.Category(site,conf["tracker"]).members()
    cat_patt = "\[\[ *("+conf["cat_patt"]+") *: *%s *(?P<key>[\|\]])"
    l = len(conf["native_namespace"])+1
    for cat in cats:
        target = f_target.search(cat.text)
        try:
            target.group("ns")
            cat.text = f_target.sub("{{"+conf["template"]+"|"+target.group("target"),cat.text)
            cat.save(conf["ns_summary"])
            editcount+=1
            if(editcount >= conf["test"]["count"]):
                return
            time.sleep(lag)
        except:
            pass
        target = target.group("target")
        title = cat.title()[l:]
        subst = re.compile(cat_patt % re.escape(title))
        repl = "[["+conf["native_namespace"]+":"+target+"\g<key>"
        summary = conf["summary"].format(title,target)
        members = cat.members()
        for i in members:
            if(i.namespace()=="Template"):
                
                k = pb.Page(site,i.title()+conf["temp_subpage"])
                k.text = subst.sub(repl,k.text)
                if(k.exists()):
                    k.save(summary)
                    editcount+=1
                    if(editcount >= conf["test"]["count"]):
                        return
                    time.sleep(lag)
            k = subst.subn(repl,i.text)
            if(k[1] == 0):
                continue
            i.text = k[0]
            i.save(summary)
            editcount+=1
            if(editcount >= conf["test"]["count"]):
                return
            time.sleep(lag)
if(config["patrolRecentchanges"]["status"]):
    patrolRecentChange()
sites = settings["categoryRedirect"]["languages"]
for i in sites:
    site = pb.Site(i,"wikipedia")
    config = json.loads(pb.Page(site,u"User:নকীব বট/config.json").text)["categoryRedirect"]
    if(config["status"]):
        if config["test"]["status"] is False:
            config["test"]["count"] = float('inf') # edit count is unlimited
        manageCategory(site,config)
#-----
import editathon #Updating editathon data
#----
fp = open("setting.json","w")
fp.write(json.dumps(settings, ensure_ascii=False,indent=4))
fp.close()