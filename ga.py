import re
import json
import datetime as dt
import time
import pywikibot as pb
import os
from PIL import Image as im
bn = pb.Site("bn","wikipedia")
def en2bn(txt):
    refs = ["০", "১","২","৩","৪","৫","৬","৭","৮","৯"]
    txt = str(txt)
    st=""
    for i in txt:
        if(i.isdigit()):
            st+=refs[int(i)]
        else:
            st+=i
    return st
now = dt.datetime.now()
yesterday = now - dt.timedelta(days=1)
config = json.loads(pb.Page(bn,"user:নকীব বট/config.json").text)
r = pb.data.api.Request
ISO = "%Y-%m-%dT%H:%M:%SZ"
months = "((জান|ফেব্র)ুয়ার[িী]|ম(ে|ার্চ)|এপ্রিল|জু(ন|লা[ইঈ])|[অআ]গা?[সষ]্ট|((সেপ্ট|ন[বভ]|ডিস)েম্|অক্টো)[ভব]র)"
no ="০১২৩৪৫৬৭৮৯"
classes = re.compile("\|\s*(?P<p>(মান|শ্রে[ণন]ী|[cC]lass|[qQ]uality))\s*=[^\|\}]*")
rea_template = re.compile("\{\{\s*ভালো নিবন্ধ পুনর্মূল্যায়ন\s*\|\s*(?:1=\s*)?(?P<topic>[^\|]+)\|\s*(?:2=\s*)?(?P<page>\S{1,2})\s*\|\s*(?:3=)?(?P<user>[^\|\}]+)[^}]*\}\}")
entry_pref = "#\s*\{\{\s*([Gg]ANentry|প্রভানিভুক্তি)\s*\|\s*(1\s*=\s*)"
entry_suf = "(\|\s*(2\s*=\s*)?(?P<page>[^\}\|]*))?\}\}[^[]*(?P<user>\[\[\s*([uU]ser|ব্যবহারকারী)\s*:[^\]]+\]\])(?P<ext>((?!\s*#\s*\{\{|<\!\-\-).)*)"
date = re.compile("(?P<date>["+no+"]{1,2} "+months+",? ["+no+"]{4}|"+months+" ["+no+"]{2},? ["+no+"]{4})")
entry = re.compile(entry_pref+"(?P<name>[^\|\}]+)"+entry_suf)
res_patt = re.compile("\{\{\s*(?P<status>([Ff]ailed|[Dd]elisted)?)[gG]A\s*[^\}]*\}\}")
ga_tag = re.compile("\{\{\s*(ভালো নিবন্ধ|[gG]ood article)\s*\}\}")
Users = re.compile("(\{\{\s*([pP]ing|উত্তর)\s*\||\[\[\s*([uU]ser|ব্যবহারকারী)\s*:)\s*(?P<uname>[^\|\}\]]+)")
level = re.compile("<\$নববি(\S)\$>")
gan_template = re.compile("\{\{\s*([gG]A nominee|ভালো নিবন্ধের জন্য মনোনীত)\s*(?P<ext>\|[^\}]+)\}\}")
#------Article history Start ----#
Ah = re.compile("\{\{\s*([aA]rticleHistory|নিবন্ধ ইতিহাস)\s*\|(?P<ext>[^\}]+)\}\}")
Ah_fetch = re.compile("(?P<cond>(?![^}]+\|\s*action)\|\s*action(?P<index>\d+)([^=]*)=[^|]*)(?P<pres>((?!\|\s*current)[^}])*)\|\s*currentstatus\s*=[^|]*(?P<pret>((?!\|\s*topic)[^}])*)\|\s*topic\s*=[^|]+(?P<end>(\|[^}]+)?)")
ah_fetch = re.compile("\|\s*action(?P<n>\d+)\s*=\s*([^\s]+)(((?!\|\s*action\d+\s*=)[\s\S])+)")
# ---- Article History End -----#
uname = re.compile("\[\[\s*([uU]ser|ব্যবহারকারী)\s*:\s*(?P<uname>[^\|\]]+)")
pat = re.compile("#\s*\{\{\s*(প্রভানিভুক্তি|[gG]ANentry)\s*\|\s*(1=)?(?P<title>[^\|\}]+)(\|\s*(2=)?(?P<page>[^\}]*))?\}\}[^\[]*\[\[\s*([uU]ser|ব্যবহারকারী)\s*:\s*(?P<user>[^\|]+)(?P<ext>((?!\s+(#\s*\{\{\s*(প্রভানিভুক্তি|[gG]ANentry|))|<\!\-\-).)*)")
gan_fetch = re.compile("\|\s*status\s*=\s*(?P<status>[^\|\}]*)(((?!\|\s*note).)*\|\s*note\s*=\s*(?P<note>[^\|\}]*))?")
gan_pref = "উইকিপিডিয়া:প্রস্তাবিত ভালো নিবন্ধ/"
g = pb.Page(bn,gan_pref[:-1])
IPcheck = re.compile("(([0-9a-fA-f]{1,4}:?){8}|([0-9]{1,3}\.?){4})")
cats = json.loads(pb.Page(bn,"user:নকীব বট/category.json").text)
TALK = re.compile("\{\{\s*(আলাপ পাতা|[tT]alk page)\s*\}\}")
# constants are delclared
# start functions
def getRevs(title,limit=9,token=None,timestamp=None,prop=["content","ids","user","tags","timestamp"]):
    data = {
        "action":"query",
        "format":"json",
        "prop":"revisions",
        "titles":title,
        "rvlimit": limit,
        "rvprop": prop,
        "rvslots":"main"
 
    }
    if(token):
        data["rvcontinue"] = token
    if(timestamp):
        data["rvstart"] = timestamp
    res = r(bn,parameters=data).submit()
    token = None
    if("query-continue" in res):
        token = res["query-continue"]["revisions"]["rvcontinue"]
    return list(res["query"]["pages"].values())[0]["revisions"], token
def getRevDate(title='আলাপ:'):
    R = {
    	'timestamp':dt.datetime.now()
    	}
    limit = 10
    c = True
    revs = [None]
    user = False
    token = ''
    while(c):
        i = 1
        last = [revs[-1]]
        revs, token = getRevs(title,token = token)
        revs = last + revs
        stable = 0 #last stable revision
        del last 
        while(i < limit):
            if("mw-rollback" in revs[i]['tags'] and user is False):
                user = None
                #print("Rollback",i)
                i += 1
                continue
            if user is None:
                user = revs[i]['user']
                #print("Rollback of ",user)
                i += 1
                continue
            if user is not False:
                if user == revs[i]['user']:
                    #print(" Skipping rollbacked",i)
                    i+=1
                    continue
                user = False
            if "mw-undo" in revs[i]['tags'] or "mw-manual-revert" in revs[i]['tags']:
                #print("Undo",i)
                i += 2
                continue
            if res_patt.search(revs[i]['slots']['main']['*']) is None:
                if(stable ^ -1):    
                    i = stable
                c = False
                R['timestamp'] = revs[i - 1]['timestamp']
                break
            #fetch the revision ID
            i += 1
            stable = i
    title = title[5:] #main page
    revs, token = getRevs(title, timestamp = R['timestamp'])
    R['oldid'] = revs[0]['revid']
    return R
def status(txt,d=""):
    switcher ={
        "onreview":"পর্যালোচনাধীন",
        "on review":"পর্যালোচনাধীন",
        "onReview":"পর্যালোচনাধীন",
        "পর্যালোচনাধীন":"পর্যালোচনাধীন",
        "onhold":"স্থগিত",
        "স্থগিত":"স্থগিত",
        "onHold":"স্থগিত",
        "on hold":"স্থগিত",
        "2nd":"২য় মতামত",
        "2nd opinion":"২য় মতামত",
        "2nd Opinion":"২য় মতামত",
        "2ndOpinion":"২য় মতামত",
        "২য় মতামত":"২য় মতামত",
        "২য়":"২য় মতামত",
        "2ndopinion":"২য় মতামত"
    }
    return switcher.get(txt,d)
def getCat(title):
    R={
        "date":"",
    "cat":"",
    "page":"১"
    }
    patt = re.compile(entry_pref+re.escape(title)+entry_suf)
    for cat in cats.values():
        t = pb.Page(bn,gan_pref+cat)
        k = patt.search(t.text)
        if(k):
            try:
                R["cat"] = cat
                R["catpage"]=t
                R["page"] = k.group("page")#bangla
                R["user"] = k.group("user")
                ext = k.group("ext")
                k = date.search(ext)
                if(k):
                    R["date"] = k.group("date")
            except:
                pass
            R["removed"] = patt.sub("",t.text)
            return R
def manageGATalk():
    cat = pb.Category(bn,"বিষয়শ্রেণী:" + config["goodArticle"]["tracker"]).members()
    for talk in cat:
        title = talk.title()[5:] #main article's title
        main = pb.Page(bn,title) #main article
        check = res_patt.search(talk.text)
        R = {}
        mx = "1"
        ah = Ah.search(talk.text)
        subst=""
        cond=""
        first = True # is it first evaluation
        if(ah):
            #already has the template
            params = ah.group("ext")
            k = Ah_fetch.search(params)
            #----beta start ----#
            m = ah_fetch.findall(params)
            for pa in params:
                if(p[1]=="GAN"):
                    first = False
                    break
            mx = str(len(params)+1)
            #----beta end ----
            #mx = str(int(k.group("index")) + 1 )
            cond = k.group("cond")
            subst+=cond + k.group("pres")
        subst += "\n| action"+mx+"\t= GA"
        c = getCat(title)
        
        if(c):
            R["topic"] = c["cat"]
            R["no"] = c["page"]
            R["catpage"] = c["catpage"]
            R["removed"] = c["removed"]
            R["user"] = c["user"]
        else:
            R["topic"] = ""
            R["no"] = "১"
        R["link"] = "/ভালো নিবন্ধ"+R["no"]
        #if(mx == "1"):
        #-----beta ---#
        if(first):
        #----beta ---
            subst+= "N"#first assessment
        else:
            subst+="R"#reassessment
        try:
            R["date"] = check.group("date")
            R["oldid"]=k.group("oldid")
        except:
            c = getRevDate(talk.title())
            R["oldid"] = str(c["oldid"])
            R["date"]=c["timestamp"]
            #try fetching
            pass
        subst += "\n| action"+mx+"date\t= "+R["date"]
        subst+="\n| action"+mx+"link\t= "+R["link"]#adding link to review pag
        k = check.group("status")
        item = main.data_item()
        if(k=="delisted" or k=="Delisted"):
            R["result"] = "delisted"
            R["status"] = "DGA"
            #notify the user
            R["bnstatus"] = "অনুত্তীর্ণ"
        elif(k=="failed" or k=="Failed"):
            R["result"] = "failed"
            R["status"] = "FGAN"
            item.setSitelink({"site":"bnwiki","title":main.title(),"badges":[]},summary="ভালো নিবন্ধের তালিকা হতে অপসারণ")
            #add badge to wikidata
            #notify the user
            R["bnstatus"] = "অনুত্তীর্ণ"
        else:
            R["result"] = "listed"
            R["status"] = "GA"
            item.setSitelink({"site":"bnwiki","title":main.title(),"badges":["Q17437798"]},summary="ভালো নিবন্ধের খেতাব যুক্ত")
            talk.text = classes.sub("| \g<p> = ভালো",talk.text)
            tagged = ga_tag.search(main.text)
            if(not(tagged)):
                main.text = "{{ভালো নিবন্ধ}}\n" + main.text
                try:
                    main.save("{{ভালো নিবন্ধ}} যুক্ত করেছি")
                except:
                    pass
            elif(tagged.group(0)[1]=="o"):
                main.text = ga_tag.sub("{{ভালো নিবন্ধ}}",main.text)
                try:
                    main.save("{{ভালো নিবন্ধ}} বাংলা ভাষায় করেছি")
                except:
                    pass
            #notify the user
            R["bnstatus"] = "উত্তীর্ণ"
        try:
            u = uname.search(R["user"])
            u = u.group("uname")#username
            n = pb.User(bn,"user:"+u)
            while(n.isRedirectPage()):
                n = n.getRedirectTarget()
            u = n.toggleTalkPage()
            u.text+= "\n{{subst:ভালো নিবন্ধ বিজ্ঞপ্তি|নিবন্ধ="+main.title()+"|ফলাফল = " +R["bnstatus"]+"}}\n ~~~~ "
            config["goodArticle"]["notifyNominator"] and u.save("মনোনীত নিবন্ধ "+R["bnstatus"]+" হয়েছে")
        except:
            pass
        subst+="\n| action"+mx+"result\t= "+R["result"]
        subst+="\n| action"+mx+"oldid\t= "+R["oldid"]#adding oldid
        if(ah):
            subst+= "\n| currentstatus\t= "+R["status"]
            pret = ""
            end=""
            try:
                pret= ah.group("pret") #text before topic parameter
                end = ah.group("end")
            except:
                pass
            subst+= pret + "\n| topic\t= " + R["topic"] + end
            talk.text = talk.text.replace(cond,subst,1)
        else:
            subst = "{{নিবন্ধ ইতিহাস" + subst 
            subst+= "\n| currentstatus\t= "+R["status"]
            subst+= "\n| topic\t= "+R["topic"]+"\n}}\n"
            s = TALK.subn("{{আলাপ পাতা}}\n"+subst,talk.text)
            if(s[1]):
                talk.text = s[0]
            else:
                talk.text = "{{আলাপ পাতা}}\n"+subst + talk.text
        talk.text = res_patt.sub("",talk.text) #remove {{GA}}/{{failedGA}}/{{delistedGA}}
        talk.text = gan_template.sub("",talk.text)
        try:
            talk.save("{{নিবন্ধ ইতিহাস}} যুক্ত/হালনাগাদ করা হয়েছে")
            t=R["catpage"]
            t.text = R["removed"]
            t.save("[["+talk.title()[5:]+"]] ভুক্তি অপসারণ")
        except:
            print(talk.title()," could not be edited")
            pass
def to_s(k,s=""):
    if(k==None):
        k=s
    return k
def manageNominee():
    D ={} #{"category":{"prefix":"","suffix":"","note":"","status":""}
    warns = config["manageRevPage"]["warnings"] 
    data ={
            "action":"query",
            "format":"json",
            "prop":"revisions",
            "rvprop":"content|ids",
            "rvslots":"main",
            "pageids":"|".join(list(cats.keys())) #keys are pageids and values are category names
     }
    pages = r(parameters=data,site=bn).submit()["query"]["pages"]
    for id in cats.keys():
        page = pages[id]
        D[cats[id]]=[]
        txt = page["revisions"][0]["slots"]["main"]["*"]
        entries = pat.finditer(txt)
        for entry in entries:
            R = {}
            R["title"] = entry.group("title")
            talk = pb.Page(bn,"talk:"+R["title"])
            R["page"] = to_s(entry.group("page"),"১").strip()
            R["user"] = to_s(entry.group("user")).strip()
            rev_template = re.compile("\{\{\s*(([Tt]alk|আলাপ)\s*:\s*[^/]+)?\/ভালো? নিবন্ধ"+R["page"]+"\s*\}\}")
            try:
                R["date"] = date.search(entry.group("ext")).group("date").strip()
            except:
                print("date could not be fetched")
            R["topic"] = cats[id]
            R["status"] = ""
            pg = pb.Page(bn,"talk:"+R["title"])
            revPage = pb.Page(bn,pg.title()+"/ভালো নিবন্ধ"+R["page"])
            rex = revPage.exists() 
            if(rex and config["manageRevPage"]["status"]): #review page exists
                R["status"] = "পর্যালোচনাধীন"
                rev = dt.datetime.strptime(revPage.getLatestEditors()[0]["timestamp"],ISO)
                day = (now - rev).days #day have passed
                summary = ""
                revSum = ""
                reviewer = pb.Page(bn,"user talk:"+revPage.oldest_revision["user"])
                nominator = pb.Page(bn,"user talk"+R["user"])   
                if(day >= warns[0]):
                    lev = level.search(revPage.text) #level of warning
                    if(lev):
                        lev = lev.group(0)
                        if(day > warns[1] and lev =="১"):
                        # notify reviewer
                            reviewer.text += "\n{{subst:user:নকীব বট/বিজ্ঞপ্তি/২|"+main.title()+"|"+talk.title()+"}}"
                            revSum = main.title() + " - দ্বিতীয় পর্যায়ের বিজ্ঞপ্তি প্রদান করা হয়েছে"
                            # update level
                            revPage.text = level.sub("<$নববি২$>",revPage.text,count=1)
                            summary = "পর্যালোচককে দ্বিতীয় পর্যায়ের বিজ্ঞপ্তি দেয়া হয়েছে"
                        elif(day > warns[2] and lev == "২"):
                           # notify reviewer
                            reviewer.text+="\n{{subst:user:নকীব বট/বিজ্ঞপ্তি/৩প|"+main.title()+"|"+talk.title()+"}}"
                            revSum = main.title() + " - তৃতীয় পর্যায়ের বিজ্ঞপ্তি দেয়া হয়েছে"
                           # notify nominator
                            nominator.text+="\n{{subst:user:নকীব বট/বিজ্ঞপ্তি/৩ম|"+main.title()+"|"+talk.title()+"|reviewer = "+reviwer.title()[17:]+"}}"
                            try:
                                nominator.save(main.title() + " - স্থগিতাবস্থার ব্যাপারে সর্বশেষ পর্যায়ের বিজ্ঞপ্তি দেয়া হয়েছে (মনোনয়ক)")
                            except:
                                pass
                           # update level
                            summary = "মনোনয়ক ও পর্যালোচককে স্থগিতাবস্থা সম্পর্কে জানানো হয়েছে"
                            revPage.text = level.sub("<$নববি৩$>",revPage.text,count=1)
                        elif(day > warns[3] and lev == "৩"):
                            #notify reviwer
                            reviewer.text += "{{subst:user:নকীব বট/বিজ্ঞপ্তি/৪প|"+main.title()+"|" + nominator.title()[17:]+"}}"
                            revSum = "চূড়ান্ত পর্যায়ের বিজ্ঞপ্তি প্রদান করা হয়ে হয়েছে"
                           #notify nominator
                            nominator.text+="\n{{subst:user:নকীব বট/বিজ্ঞপ্তি/৪ম|"+main.title()+"|"+talk.title()+"|"+reviewer.title()[17:]+"}}"
                            try:
                                nominator.save()
                            except:
                                pass
                           #notify project
                            pj = pb.Page(bn,"উইকিপিডিয়া আলাপ:উইকিপ্রকল্প ভালো নিবন্ধ")
                            pj.text += "{{subst:user:নকীব বট/বিজ্ঞপ্তি/৪প্র|"+main.title()+"|"+reviwer.title()[17:]+ "|" + nominator.title()[17:]+"}}"
                            pj.save("[["+ main.title()+ "]] নিবন্ধটি প্রায় দেড়মাসের বেশি সময় ধরে স্থগিতাবস্থা বজায় থাকায় মূল প্রকল্পে জানানো হয়েছে",quiet=True)
                           #update level
                            summary = "পর্যালোচক সম্ভবত ব্যস্ত; তাই মূল প্রকল্পে অবহিত করা হয়েছে। এই ব্যাপারে পর্যালোচক ও মনোনয়ককেও জানানো হয়েছে"
                            revPage.text = level.sub("<$নববি৪$>",revPage.text,count=1)
                    else:
                        #"mention all the users")
                        subst = Users.findall(revPage.text)
                        s = set()
                        for i in subst:
                            s.add(i[3])
                        s.discard(u'নকীব বট')
                        subst = u"[[ব্যবহারকারী:" + "|]], [[ব্যবহারকারী:".join(s) +"|]]"
                        revPage.text+= u"\n=== পর্যালোচনার অগ্রগতি ===\nপ্রিয় " + subst
                        revPage.text += u"<br/>{{subst:user:নকীব বট/বিজ্ঞপ্তি/১}}"
                        summary = u"সংশ্লিষ্ট সকলকে অবহিত করতে বিজ্ঞপ্তি"
                    try:
                        revPage.save(summary,quiet=True)
                    except:
                        print(u"পর্যালোচনা পাতা সম্পাদনা সম্ভব হয় নি")
                        pass
                    try:
                        reviewer.save(revSum,quiet=True)
                    except:
                        print("পর্যালোচককে বার্তা দেয়া সম্ভব হয় নি")
                        pass
            gan = gan_template.search(pg.text)
            subst = "{{ভালো নিবন্ধের জন্য মনোনীত\n | "
            subst += str(R["date"])+"\n | nominator\t= [[ব্যবহারকারী:"+R["user"]+"|]]\n"
            subst += " | page\t= " + R["page"] + "\n | subtopic\t= " + R["topic"]
            if(gan and gan.group("ext")):
                gan = gan_fetch.search(gan.group("ext"))
                R["status"] = status(gan.group("status").strip(),R["status"])
                if(not(rex)):
                    R["status"] = ""
                R["note"] = to_s(gan.group("note")).strip()
                subst+= "\n | status\t= " +R["status"]+"\n | note\t= "+R["note"]+"\n}}"
                talk.text = gan_template.sub(subst,talk.text)
                if(rex and not(rev_template.search(talk.text)) and config["goodArticle"]["addRevPage"]):
                    talk.text+="\n{{"+revPage.title()+"}}"  
            else:
                #{{GAN}} template was not used
                subst+= "\n | status\t= "+R["status"]+"\n | note\t=\n}}"
                s = TALK.subn("{{আলাপ পাতা}}\n"+subst,talk.text)
                if(s[1]):
                    talk.text = s[0]
                else:
                    talk.text = "{{আলাপ পাতা}}\n"+subst + talk.text
                if(rex and not(rev_template.search(talk.text)) and config["goodArticle"]["addRevPage"]):
                    talk.text+="\n{{"+revPage.title()+"}}" ##add the link of review page
            try:
                 talk.save("{{ভালো নিবন্ধের জন্য মনোনীত}}",quiet=True)
            except:
                 pass
            #D[cats[id]].append(R)
def manageGAR():
    pages = pb.Category(bn,u"বিষয়শ্রেণী:পুনর্মূল্যায়ন প্রয়োজন এমন ভালো নিবন্ধ").members()
    R ={}
    for i in cats.values():
        R[i] ={
            'content':'',
            'summary':[]
            }
    nom_summary = u"[[%s]] নিবন্ধের পুনর্মূল্যায়নের জন্য ভুক্তি যোগ"
    repl_summary = u"{{ভালো নিবন্ধের জন্য মনোনীত}}"
    for i in pages:
        title = i.title(with_ns=False)
        k = rea_template.search(i.text)
        topic, page, user = (k.group("topic").strip(), k.group("page").strip(), k.group("user").strip())
        repl = u"{{ভালো নিবন্ধের জন্য মনোনীত\n|~~~~~\n|nominator=%s\n|page=%s\n|subtopic=%s\n|status=\n|note=\n}}" % (user,page,topic)
        nom = u"\n# {{প্রভানিভুক্তি|1=%s|2=%s}} - [[User:%s|]] ~~~~~" % (title, page, user)
        i.text = rea_template.sub(repl, i.text)
        i.save(repl_summary)
        R[topic]['content'] += nom
        R[topic]['summary'].append(title)
    for i in R:
        if(R[i]['content'] == ""):
            continue
        pg = pb.Page(bn,gan_pref + i)
        pg.text += R[i]['content']
        pg.save(nom_summary % ("]], [[".join(R[i]['summary']) ))
#--Image resize
temp = re.compile(u"\{\{ *(?:non-free reduce|মুক্ত নয় হ্রাস করুন) *[^\}]+\}\}",re.I)
#attribute to zervick
from xml.etree import ElementTree as etree
# is there a good way to get rid of this function?
def prepare_options(options):
    if 'width' not in options:
        options['width'] = None
    if 'height' not in options:
        options['height'] = None
    if 'longest' not in options:
        options['longest'] = None
    if 'shortest' not in options:
        options['shortest'] = None
    if 'margin' not in options:
        options['margin'] = '0'
    if 'trim' not in options:
        options['trim'] = False
    if 'frame' not in options:
        options['frame'] = False
def parse_length(value, def_units='px'):
    """Parses value as SVG length and returns it in pixels, or a negative scale (-1 = 100%)."""
    if not value:
        return 0.0
    parts = re.match(r'^\s*(-?\d+(?:\.\d+)?)\s*(px|in|cm|mm|pt|pc|%)?', value)
    if not parts:
        raise Exception('Unknown length format: "{}"'.format(value))
    num = float(parts.group(1))
    units = parts.group(2) or def_units
    if units == 'px':
        return num
    elif units == 'pt':
        return num * 1.25
    elif units == 'pc':
        return num * 15.0
    elif units == 'in':
        return num * 90.0
    elif units == 'mm':
        return num * 3.543307
    elif units == 'cm':
        return num * 35.43307
    elif units == '%':
        return -num / 100.0
    else:
        raise Exception('Unknown length units: {}'.format(units))

def resize_svg(tree, options):
    prepare_options(options)
    svg = tree.getroot()
    if 'width' not in svg.keys() or 'height' not in svg.keys():
        raise Exception('SVG header must contain width and height attributes')
    width = parse_length(svg.get('width'))
    height = parse_length(svg.get('height'))
    viewbox = re.split('[ ,\t]+', svg.get('viewBox', '').strip())
    if len(viewbox) == 4:
        for i in [0, 1, 2, 3]:
            viewbox[i] = parse_length(viewbox[i])
        if viewbox[2] * viewbox[3] <= 0.0:
            viewbox = None
    else:
        viewbox = None
    if width <= 0 or height <= 0:
        if viewbox:
            width = viewbox[2]
            height = viewbox[3]
        else:
            raise Exception('SVG width and height should be in absolute units and non-zero')
    if not viewbox:
        viewbox = [0, 0, width, height]

    # read and convert size and margin values
    margin = parse_length(options['margin'], 'mm')
    twidth = None
    theight = None
    if options['width']:
        twidth = parse_length(options['width'], 'mm')
    if options['height']:
        theight = parse_length(options['height'], 'mm')
    if options['longest']:
        value = parse_length(options['longest'], 'mm')
        if width > height:
            twidth = value
        else:
            theight = value
    if options['shortest']:
        value = parse_length(options['shortest'], 'mm')
        if width < height:
            twidth = value
        else:
            theight = value

    # twidth and theight are image dimensions without margins
    if twidth:
        if twidth < 0:
            twidth = -width * twidth
        elif twidth > 0:
            twidth = max(0, twidth - margin * 2)
    if theight:
        if theight < 0:
            theight = -height * theight
        elif theight > 0:
            theight = max(0, theight - margin * 2)

    if not twidth:
        if not theight:
            twidth = width
            theight = height
        else:
            twidth = theight / height * width
    if not theight:
        theight = twidth / width * height

    # set svg width and height, update viewport for margin
    svg.set('width', '{}px'.format(twidth + margin * 2))
    svg.set('height', '{}px'.format(theight + margin * 2))
    offsetx = 0
    offsety = 0
    if twidth / theight > viewbox[2] / viewbox[3]:
        # target page is wider than source image
        page_width = viewbox[3] / theight * twidth
        offsetx = (page_width - viewbox[2]) / 2
        page_height = viewbox[3]
    else:
        page_width = viewbox[2]
        page_height = viewbox[2] / twidth * theight
        offsety = (page_height - viewbox[3]) / 2
    vb_margin = page_width / twidth * margin
    svg.set('viewBox', '{} {} {} {}'.format(
        viewbox[0] - vb_margin - offsetx,
        viewbox[1] - vb_margin - offsety,
        page_width + vb_margin * 2,
        page_height + vb_margin * 2))

    # add frame
    if options['frame']:
        nsm = {
            'inkscape': 'http://www.inkscape.org/namespaces/inkscape',
            'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd'
        }
        layer = etree.SubElement(svg, 'g', nsmap=nsm)
        layer.set('{{{}}}groupmode'.format(nsm['inkscape']), 'layer')
        layer.set('{{{}}}label'.format(nsm['inkscape']), 'Frame')
        layer.set('{{{}}}insensitive'.format(nsm['sodipodi']), 'true')
        frame = etree.SubElement(layer, 'path')
        frame.set('style', 'fill:#ffffff;stroke:none')
        bleed = min(page_width, page_height) / 100
        frame.set('d', 'M {0} {1} v {3} h {2} v -{3} z M {4} {5} h {6} v {7} h -{6} z'.format(
            -viewbox[0] - vb_margin - offsetx - bleed,
            -viewbox[1] - vb_margin - offsety - bleed,
            page_width + (vb_margin + bleed) * 2,
            page_height + (vb_margin + bleed) * 2,
            viewbox[0], viewbox[1],
            viewbox[2], viewbox[3]))


def process_stream(options):
    options = {
    	'height':'100px',
    	'width':'10px'
    	}
    

def get_dimension(dim, threshold = 0.05, target = 100000):
    width = dim[0]
    height = dim[1]
    ratio = width/height
    width = (target*ratio)**0.5
    height = width/ratio
    dr = 1 - width*height/dim[0]/dim[1] #percentage of change
    if dr <= threshold:
        return None
    return int(width), int(height)
def thumb(path):
    k = im.open(path)
    dim = get_dimension(k.size, config['reduceImage']['tag']['minDeltaRate'], config['reduceImage']['tag']['resolution'])
    if dim is None:
        print('Skipping')
        return False
    k.thumbnail(dim,im.ANTIALIAS)
    try:
        #--- Save with metadata
        exif = k.info["exif"]
        k.save(path,exif=exif)
    except:
        #---Save without metadata
        k.save(path)
    return True
def fetch_csrf(k):
    return k
def reduceFUR():
    svg_tag = config['reduceImage']['tag']['tracker'] % ('svg')
    summary = config['reduceImage']['uploadSummary']
    files = pb.Category(bn,u"বিষয়শ্রেণী:" + config['reduceImage']['tracker']).members()
    for i in files:
        i = pb.FilePage(i) #Render as File page
        title = i.title(as_filename=True, with_ns=False).replace('_',' ')
        if(i.download(title) == False):
            continue
        t = False
        if(title[-4:].lower() == '.svg'):
            with open (title,"r") as fp:
                tree = etree.parse(fp)
            dim = i.latest_file_info
            dim = get_dimension(dim.size, config['reduceImage']['tag']['minDeltaRate'], config['reduceImage']['tag']['resolution'])
            if dim is not None:
                t = True
                resize_svg(tree, options)
                tree.write(title)
        else:
            t = thumb(title)
        i.text = temp.sub(u"{{subst:furd}}", i.text,1)
        if(t == False):
            #---Remove the tag
            i.save(u'ইতিমধ্যেই হ্রাসকৃত চিত্র হওয়ায় ট্যাগ পরিবর্তন')
            os.remove(title)
            #---Skip
            continue
        try:
            bn.upload(
                source_filename = title,
                filepage = i,
                 comment = summary,
                 ignore_warnings = fetch_csrf
                 )
            i.save(summary)
        except:
            print("Couldn't upload")
        os.remove(title)
#### Declaring Constants of archiving ###
Archive = {}
defaults = [ #default setting
    ('max-day',config['archiveTalk']['defaults']['maxDay']), #talks before 7 days will be archived
    ('archive-format','আদর্শ'), #the link of archive index to be updated
    ('archive-pattern',config['archiveTalk']['defaults']['archivePattern']), #to calculate next archive
    ('on-subpage','হ্যাঁ'), #whether the archival is on subpage
    ('current-index','1'), #current index of archive
    ('archive-size', config['archiveTalk']['defaults']['archiveSize']), #minimum size to create a new archive
    ('string','\n'),
    ('archive-month',''),
    ('archive-day',1),
    ("$",'1'),
    ("y1",str(yesterday.year)),
    ("y2",str(now.year)),
    ("m1",str(yesterday.month).zfill(2)),
    ("m2",str(now.month).zfill(2))
]
numers = {
    '০':'0',
    '১':'1',
    '২':'2',
    '৩':'3',
    '৪':'4',
    '৫':'5',
    '৬':'6',
    '৭':'7',
    '৮':'8',
    '৯':'9'
}
numer_group = ''.join(numers.keys())
months ={ # month mapping
    'জানুয়ারি':'Jan',
    'ফেব্রুয়ারি':'Feb',
    'মার্চ':'Mar',
    'এপ্রিল':'Apr',
    'মে':'May',
    'জুন':'Jun',
    'জুলাই':'Jul',
    'আগস্ট':'Aug',
    'সেপ্টেম্বর':'Sep',
    'অক্টোবর':'Oct',
    'নভেম্বর':'Nov',
    'ডিসেম্বর':'Dec'
}
month_patt = '(?:জানু|ফেব্রু)য়ারি|ম(?:ার্চ|ে)|এপ্রিল|জু(?:ন|লাই)|আগস্ট|(?:(?:সেপ্ট|নভ|ডিস)েম্|অক্টো)বর'
date_patt = re.compile('(['+numer_group+']{1,2} ('+ month_patt+') ['+ numer_group+']{4}) \(ইউটিসি\)\s*(?:(?:\{\{ *[Aa]bot *\}\}|\|\}|<!--(?:(?!-->)[\s\S])*-->|<\/\S+>)\s*)*$')
DATE = '%d %b %Y' #pattern of the date
setting = re.compile('\{\{\s*স্বয়ংক্রিয় সংগ্রহশালা\s*([^\}]*)\}\}')
setting_fetch = re.compile('\| *([^= ]+) *= *([^\n\|]+)')
section = re.compile('(\s*\n=+ *(?P<section>[^=]+)=+\n(?:(?!\n=+[^=]+=+\n)[\s\S])*)')
NS =[
    '[wW](?:ikipedia|[Pp])|উইকিপিডিয়া',
    'আলাপ|[Tt]alk',
    '[Uu]ser talk|ব্যবহারকারী আলাপ',
    '',
    '[wW](?:ikipedia|[Pp]) talk|উইকিপিডিয়া আলাপ',
    ''
]
ns_map ={
    "TALK":1,
    "আলাপ":1,
    "USER TALK":2,
    "ব্যবহারকারী আলাপ":2,
    "WIKIPEDIA":0,
    "WP":0,
    "উইকিপিডিয়া":0
}
c_patt = re.compile('\s*\| *current-index *= *\d*\s*|$')
b_numers = ['০','১','২','৩','৪','৫','৬','৭','৮','৯']
ns_patt = re.compile('(?:((?:আলাপ|ব্যবহারকারী|টেমপ্লেট|বিষয়শ্রেণী|উইকিপিডিয়া|বিশেষ|Talk|user|wikipedia|template|category|WP)(?: talk| আলাপ)?):)?(.+)',re.I)
sep = re.compile("\s*,\s*")
#### Constant declared #####
###--- Declaring util function ----#
def fetch_setting(txt):
    k = setting.search(txt)
    if(k and k.group(1)):
        k = k.group(1)
        k = dict(defaults + setting_fetch.findall(k) + [('string',k)])
        k['$'] = k['current-index']
        print(type(k['$']))
        k["max-day"] = int(k["max-day"])
        k["archive-size"] = int(k["archive-size"])
        k["on-subpage"] = k["on-subpage"] is not "না" or k["archive-pattern"][0] is "/"
        k['archive-month'] = sep.split(k['archive-month'].strip())
        k['archive-day'] = int(k['archive-day'])
        if(k['archive-format']=='বর্ধিত'):
            if(len(k['$']) == 12):
                k['y1'] = k['$'][:4]
                k['m1'] = k['$'][4:6]
                k['y2'] = k['$'][6:10]
                k['m2'] = k['$'][10:12]
            else:
                k['y2'] = str(now.year)
                k['m2'] = str(now.month).zfill(2) #padding with zero
                k['y1'] = k['y2']
                k['m1'] = k['m2']
        k["$"] = int(k["$"])
        return k
    return dict(defaults)
def is_old(txt):
    try:
        k = date_patt.search(txt) # the month in localised
        month = k.group(2)
        month_e = months[month] # convert to English
        txt = to_en(k.group(1).replace(month,month_e)) # localise to english
        k = dt.datetime.strptime(txt,DATE) #parse the date
        return (now - k).days >= Archive["config"]["max-day"]
    except: # an error occured so stay safe and skip
        return False
def to_en(txt):
    s = ""
    for i in txt:
        try:
            s += numers[i]
        except:
            s+=i
    return s
def to_bn(txt):
    txt = str(txt)
    s = ""
    for i in txt:
        try:
            s+=b_numers[int(i)]
        except:
            s+=i
    return s
def size(t):
    return 
def archive_section(match):
    content = match.group(1)
    if(is_old(content)):
        title = match.group(2).strip()
        Archive['sections'].append(title)
        Archive["content"] += content
        return ""
    return content # skip the section
def fetch_backlink(title):
    ns, title = ns_patt.match(title).groups()
    backlink = "(\[\[ *(?:"
    ns = ns_map[ns.upper()]
    ns = NS[ns]
    title = re.escape(title)
    backlink += ns +") *: *" + title + " *#([^\|\]]+))" #add a colon
    return re.compile(backlink)
def fix_backlink(match):
    s = match.group(2).strip()
    if s in Archive['sections']:
        Archive['fixed-section'] += 1
        return "[[%s#%s" % (Archive['title'], s)
    return match.group(1)
def check_overflow(pg, prefix): # old archive has been overloaded
    condition = now.month in Archive['config']['archive-month'] #current month is specified
    condition = condition and Archive['config']['archive-day'] == now.day
    if(Archive['config']['archive-month'] == ['']):
        condition = condition or Archive['config']['archive-size'] <= len(pg.text.encode('utf-8'))
    if(condition):#Condition for new archive satisfied
        Archive['config']['$'] += 1
        if(Archive['config']['archive-format']=='বর্ধিত'):
            Archive['config']['y1'] = Archive['config']['y2']
            Archive['config']['m1'] = Archive['config']['m1']
            Archive['config']['y2'] = str(now.year)
            Archive['config']['m2'] = str(now.month).zfill(2)
            Archive['config']['$'] = Archive['config']['y1'] + Archive['config']['m1'] + Archive['config']['y2'] + Archive['config']['m2']
        title = index.sub(index_s,Archive['config']['archive-pattern'])
        if(Archive['config']['on-subpage']):
            title = prefix + title
        pg = pb.Page(bn,title)
        pg.text = '{{সংগ্রহশালার স্বয়ংক্রিয় পরিভ্রমণ}}' + pg.text
        pg.save("নতুন সংগ্রহশালার সূচনা")
index = re.compile('(\$|[my][12])')
def index_s(m):
    return to_bn(Archive['config'][m.group(1)])
#--- Util functions declared-----
#----- Main archival function------
def archive():
    pages = pb.Category(bn,u'বিষয়শ্রেণী:'+config['archiveTalk']['tracker']).members()
    global Archive
    for i in pages:
        Archive = {
            'config':fetch_setting(i.text),
            'content':'',
            'sections':[],
            'size':0,
            'fixed-section':0,
            'backlinks':0
        }
        i.text = section.sub(archive_section,i.text)
        if(len(Archive['sections']) == 0):
            #No section was archived
            continue
        #--Set the current archive page ---
        title = index.sub(index_s, Archive['config']['archive-pattern'])
        if(Archive['config']['on-subpage']):
            title = i.title() + title
        Archive['title'] = title
        pg = pb.Page(bn, title)
        summary = u'বট কর্তৃক %sটি অনুচ্ছেদ স্বয়ংক্রিয়ভাবে সংগ্রহশালায় স্থানান্তর' % to_bn(len(Archive['sections']))
        pg.text += Archive['content']
        pg.save(summary) #archive page
        backlink = fetch_backlink(i.title())
        backlinks = i.backlinks(follow_redirects = False)
        for j in backlinks:
            Archive['fixed-section'] = 0
            j.text = backlink.sub(fix_backlink,j.text)
            if Archive['fixed-section'] is 0:
                #no fix
                continue
            j.save(summary + u'িত হওয়ায় %sটি সংযোগ ঠিক করা হয়েছে' % (to_bn(Archive['fixed-section'])))
            Archive['backlinks'] += 1  
        check_overflow(pg, i.title())
        t = c_patt.sub('\n|current-index = %s\n' % Archive['config']['$'], Archive['config']['string'], 1)
        i.text = setting.sub('{{স্বয়ংক্রিয় সংগ্রহশালা\n' + t + '}}',i.text, 1) # update current index
        if(Archive['backlinks']):
            summary += u' এবং %sটি পশ্চাৎসংযোগ ঠিক করা হয়েছে' % (to_bn(Archive['backlinks']))
        i.save(summary) # main page
if(config['archiveTalk']['status']):
    archive()
if(config["reduceImage"]['status']):
    reduceFUR()
if(config["goodArticle"]["status"]):
    manageGATalk()
    manageGAR()
    if(config["goodArticle"]["manageNominee"]["status"]):
        config = config["goodArticle"]["manageNominee"]
        manageNominee()