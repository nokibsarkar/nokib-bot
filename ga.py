
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