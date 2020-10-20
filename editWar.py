# -*- coding: utf-8 -*-
import re
import datetime as dt
import json
import pywikibot as pb
bn = pb.Site("bn","wikipedia")
r = pb.data.api.Request
ISO = "%Y-%m-%dT%H:%M:%SZ"
MIME = re.compile('image\/(.+)')
non_free = re.compile('\{\{\s*(?:মুক্ত নয়|non-free) *(?!হ্রাস(?:কৃত| কর(?:ুন|বেন না))|(?:no )?reduced?)',re.I)
tagged = re.compile('\{\{\s*(?:মুক্ত নয়|non-free) (?:হ্রাস(?:কৃত| কর(?:ুন|বেন না))|(?:no )?reduced?)', re.I)
config =json.loads(pb.Page(bn,"user:নকীব বট/config.json").text)
settings = None
with open("realtime.json","r") as fp:
    settings = json.loads(fp.read())
patt = ''
with open('illegal_username.txt','r') as fp:
    patt = fp.read()
patt = re.compile(
	patt,
	re.I
	)
cases = ""
now = dt.datetime.now()
month = ["জানুয়ারি","ফেব্রুয়ারি","মার্চ","এপ্রিল","মে","জুন","জুলাই","আগস্ট","সেপ্টেম্বর","অক্টোবর","নভেম্বর","ডিসেম্বর"]
now_st = int(now.strftime('%s')) // 86400 #Days from 01-01-1970
last_access = settings["editWar"]["last_access"]
def en2bn(txt):
    txt = str(txt)
    Ref = ["০","১","২","৩","৪","৫","৬","৭","৮","৯"]
    s=""
    for i in txt:
        try:
            s+=Ref[int(i)]
        except:
            s+=i
    return s
def fetch(title,total=10):
    data = {
            "action":"query",
            "format":"json",
            "formatversion": 2,
            "prop":"revisions",
            "titles": title,
            "rvlimit": total,
            "rvprop":"tags|user|ids"
        }
    data = r(site=bn,parameters=data).submit()
    return data["query"]["pages"][0]["revisions"]
def detect_edit_war():
    global last_access, now, settings, config
    trusted = config['editWar']["trustedUsers"]
    LOG = pb.Page(bn,u"user:নকীব বট/সম্পাদনা যুদ্ধ/"+en2bn(int(settings["editWar"]["count"]/10 + 1)))
    admin = pb.Page(bn,"উইকিপিডিয়া:প্রশাসকদের আলোচনাসভা")
    backlog = settings['editWar']['backlog']
    R = [{},{}]
    data1 = {
            "action":"query",
            "format":"json", 
            "list":"recentchanges",
            "rctype":"edit",
            "rcend":now,
            "rcdir":"newer",
            "rclimit":"max",
            "rctag":"mw-undo",
            "rcstart":last_access,
            "rctoponly":True,
            "rcprop":"title"
             }
    data2 = {
            "action":"query",
            "format":"json", 
            "generator":"recentchanges",
            "grctype":"edit",
            "grcend":now,
            "grcdir":"newer",
            "grclimit":"max",
            "grctag":"mw-rollback",
            "grcstart":last_access,
            "grctoponly":True,
            "grcprop":"title"
             }
    c = True
    while(c):
        data = data1.copy()
        data.update(data2)
        batch = r(site=bn,parameters=data).submit()
        c = "query-continue" in batch
        if(c):
            if("rccontinue" in batch["query-continue"]["recentchanges"]):
                data1["rccontinue"] = batch["query-continue"]["recentchanges"]["rccontinue"]
            else:
                data1 = {}
            if("grccontinue" in batch["query-continue"]["recentchanges"]):
                data2["grccontinue"] = batch["query-continue"]["recentchanges"]["grccontinue"]
            else:
                data2 = {} 
        changes = batch["query"]["recentchanges"]
        if("pages" in batch["query"]):
            changes += list(batch["query"]["pages"].values()) # merge both the list of undo and rollback
        print("Total scanning : %d" %(len(changes)))
        for i in changes:
            attacks = 0
            warriors = set()
            title = i["title"]
            revs = fetch(title,config["editWar"]["scanRevision"])
            last_id = revs[0]['revid']
            bid = 0
            if(title in backlog):
                bid = backlog[title]
            st = u"\n'''শিরোনাম:''' [["+title+u"]] ([{{subst:fullurl:"+ title +"|action=watch}} নজর রাখুন] &bull; [{{subst:fullurl:"+ title +'|action=protect}} সুরক্ষা])\n{|class="wikitable mw-collapsible mw-collapsed"\n|-\n!সংস্করণ !!সম্পাদক !!সম্পাদনার ধরন\n|-\n'
            for j in revs:
                if(bid == j['revid'] and attacks < 6):
                    print("Already mentioned")
                    warriors = set()
                    break
                if('userhidden' in j):
                    #Skip as the user has been hidden
                    continue
                user = j["user"]
                st+="|[[বিশেষ:পার্থক্য/"+str(j["revid"])+"|"+str(j["revid"])+"]]||[[ব্যবহারকারী:"+user+"|]]||"
                if(user not in trusted and ("mw-undo" in j["tags"] or "mw-rollback" in j["tags"])):
                    attacks += 1
                    warriors.add(user)
                    if("mw-undo" in j["tags"]):
                        st+="'''পুনর্বহাল'''"
                    else:
                        st+="'''রোলব্যাক'''"
                elif(user in warriors):
                    st += "সাধারণ"
                else:
                    st+="সাধারণ\n|-\n"
                    break
                st+="\n|-\n"
            st+="|}"
            if(len(warriors) > config["editWar"]["minWarrior"]):
                print("Title suspected : "+title)
                print("Warriors are "+str(warriors))
                if(attacks > config["editWar"]["suspectWar"]):
                    backlog[title] = last_id
                    if(attacks > config["editWar"]["confirmWar"]):
                        print("Result : Confirmed")
                        R[0][title] = st
                        LOG.text+= "\n== "+ en2bn(settings["editWar"]["count"]) +"==\n"+st
                        settings["editWar"]["count"]+=1
                        if(settings["editWar"]["count"] % 10 == 0):
                            LOG.save(u"নতুন সম্পাদনা যুদ্ধ এবং সংগ্রহশালা সমাপ্তি")
                            LOG = pb.Page(bn,u"user:নকীব বট/সম্পাদনা যুদ্ধ/"+en2bn(int(settings["editWar"]["editWar"]["count"]/10 + 1)))
                            LOG.text += "{{user:নকীব বট/বিজ্ঞপ্তি}}"
                        
                        if(config['editWar']['notifyWarriors']==False):
                            continue
                        #notify the users
                        for user in warriors:
                            user = pb.Page(bn,"User talk:"+user)
                            user.text+="\n== "+i["title"]+"-এ সম্পাদনা যুদ্ধ == \n{{subst:Uw-3rr|"+i["title"]+"}}\n--~~~~"
                            try:
                                user.save("[["+title+u"]] নিবন্ধে সম্পাদনা যুদ্ধ সম্পর্কে সতর্ক করা হয়েছে")
                            except:
                                pass
                            #request protection"""
                    else:
                        R[1][title] = st
        summary = ""
        st=""
        if(len(R[0])):
            st+="\n'''যুদ্ধ চলমান'''\n"+"\n".join(R[0].values())
            summary+= "[["+"]], [[". join(R[0].keys())+"]]-নিবন্ধ(সমূহ) এ চলমান সম্পাদনা যুদ্ধের বিজ্ঞপ্তি"
        if(len(R[1])):
            st+="\n'''যুদ্ধের ডঙ্কা'''\n"+"\n".join(R[1].values())
            if(summary!=""):
                summary+=" এবং "
            summary+= "[["+"]], [[". join(R[1].keys())+"]]-নিবন্ধ(সমূহ) এ সম্পাদনা যুদ্ধের আভাস"
        if(st==""):
            return
        summary = "বট কর্তৃক "+ summary +" প্রদান করা হয়েছে"
        st = "\n== সম্পাদনা যুদ্ধ সম্পর্কে বিজ্ঞপ্তি ==\n{{subst:User:নকীব বট/সম্পাদনা যুদ্ধ}}\n"+st+"\n~~~~"
        try:
            admin = pb.Page(bn,"উইকিপিডিয়া:প্রশাসকদের আলোচনাসভা")
            admin.text+=st
            admin.save(summary)
            LOG.save(u"নতুন সম্পাদনা যুদ্ধ")
            settings['editWar']['backlog'] = backlog
        except:
            pass
#----DetectUser -----#
def appendTable(table, data):
    data += "\n|}"
    s = re.subn("\n\|\}" ,data, table, 1)
    if s[1] is 0:
        table += u'\n{|class="wikitable sortable" style="width:100%"\n|-\n!ব্যবহারকারী নাম !!নীতিমালাবহির্ভূত অংশ !!তারিখ\n|-' + data
    else:
        table = s[0]
    return table
def patrolRecentChange():
    global settings, cases,non_free, last_access, tags
    backlog = settings['detectUser']['backlog']
    cases = '' # entries for username
    #-- edit the sandbox ---#
    pg = pb.Page(bn,u'User:নকীব বট/খেলাঘর')
    pg.text = re.sub('\n\* *([^\n]+)',check, pg.text)
    if(cases != ''):
        pg.text = appendTable(pg.text, cases)
        pg.save(u'পরীক্ষার ফলাফল ঘোষণা')
    cases = '' #blank it for new
    #--check for backlogs ---#
    data = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "utf8": 1,
            "rvdir":"newer",
            "rvprop": "user",
            "rvlimit": "max",
            "titles": u"উইকিপিডিয়া:ব্যবহারকারী নাম পরিবর্তনের আবেদন",
            "rvslots": "main",
            "rvstart":last_access
        }
    revs = list(r(bn,parameters=data).submit()['query']['pages'].values())[0]
    if 'revisions' in revs:
        revs = revs['revisions']
    else:
        revs = []
    for i in revs:
        if 'userhidden' in i:
            #username has been hidden
            continue
        user = i['user']
        if user not in backlog:
            #Skip the username
            continue
        del backlog[user]
    for i in backlog.copy():
        t = int(backlog[i]) #Number Days after 01-01-1970
        if((now_st - t) < 7):
            #did not cross the limit
            continue
        cases = u'%s\n|[[ব্যবহারকারী:%s]]||%s||~~~~~\n|-' % (cases, i, ', '.join(patt.findall(i)))
        del backlog[i]
    ##--- check if anyone who did not apply for renaming
    if(cases != ''):
        title = u"উইকিপিডিয়া:নীতিমালাবহির্ভূত ব্যবহারকারী নাম/%s %s" % (en2bn(now.year), month[now.month -1])
        pg = pb.Page(bn,title)
        pg.text = appendTable(pg.text, cases)
        pg.save(u'বট কর্তৃক নীতিমালাবহির্ভূত ব্যবহারকারীর নামের তালিকা হালনাগাদ করা হচ্ছে')
    ### Patrol recentchanges
    #--- data1 for userdetect while data2 for image tagging
    data1 = [
        ("action","query"),
        ("format", "json"),
        ("utf8",True)
    ]
    data2 = [
         ("list", "recentchanges"),
         ("rcdir","newer"),
         ("rcnamespace", 2),
         ("rcprop", "title|loginfo"),
         ("rcshow", "!bot"),
         ("rctype", "log"),
         ('rcstart',last_access),
         ('rclimit','max')
        ]
    data3 = [
        ("prop", "imageinfo|revisions"),
        ("rvprop", "content"),
        ("rvslots","main"),
        ("generator", "recentchanges"),
        ("iiprop", "mime|dimensions|user"),
        ("iilocalonly", 1),
        ("grcdir", "newer"),
        ("grcnamespace", 6),
        ("grcprop", "title|timestamp|ids"),
        ('grcstart',last_access),
        ("grclimit",250),
        ('grcdir','newer')
    ]
    ###
    c=True
    while(c):
        data = dict(data1 + data2 + data3)
        batch = r(bn,parameters=data).submit()
        c = 'query-continue' in batch and 'recentchanges' in batch['query-continue']
        if(c):
            if('rccontinue' in batch['query-continue']['recentchanges']):
                data2.insert(8,('rccontinue', batch['query-continue']['recentchanges']['rccontinue']))
            else:
                data2 = []
            if('grccontinue' in batch['query-continue']['recentchanges']):
                if len(data3) < 13:
                    data3.insert(12,('grccontinue', batch['query-continue']['recentchanges']['grccontinue']))
                else:
                    data3[12] = ('grccontinue', batch['query-continue']['recentchanges']['grccontinue'])
            elif('query-noncontinue' in batch): # accessing recentchanges first
                if len(data3) < 13:
                    data3.insert(12,('grccontinue', batch['query-noncontinue']['recentchanges']['grccontinue']))
                else:
                    data3[12] = ('grccontinue', batch['query-noncontinue']['recentchanges']['grccontinue'])
                del batch['query']['pages']
            else:
                data3 = []
    ###
        batch = batch['query']
        files = []
        users = []
        if(config['reduceImage']["tag"]["status"] and 'pages' in batch):
            files = batch['pages'].values()
        if(config['detectUser']['status'] and 'recentchanges' in batch):
            users = batch['recentchanges']
        print("Scanning files:",len(files))
        print("Scanning Users:",len(users))
        for i in files:
            if('missing' in i):
                #--Deleted Already
                continue
            info = i['imageinfo'][0]
            p1 = MIME.match(info['mime'])
            if(p1 == None):
                #skip as it is not an image
                continue
            p1 = p1.group(1)
            if(p1 != 'svg'):
                p1 = 'image'
            height = info['height']
            width = info['width']
            info['content'] = i['revisions'][0]['slots']['main']['*']
            resolution = height * width
            target_res = 100000
            if(1 - target_res/resolution < 0.05):
                #skip as it is small enough
                continue
            if(non_free.search(info['content']) == None or tagged.search(info['content'])):
                #Freely licensed or already tagged
                continue
            #--- Overly pixeled non-free image
            fp = pb.Page(bn,i['title'])
            fp.text = u'{{মুক্ত নয় হ্রাস করুন|type=%s|bot=নকীব বট}}\n' % (p1) + fp.text
            fp.save(u'অধিক রেজ্যুলেশনের অ-মুক্ত চিত্র হ্রাসকরণের জন্য ট্যাগ করা হয়েছে')
            #----Notify the user ----#
            """
            user = pb.Page(bn,'User talk:' +info['user'])
            user.text+= u'\n== অ-মুক্ত চিত্রের আকার সংক্রান্ত বিজ্ঞপ্তি ==\n{{subst:uw-nonfree|%s}}\n-~~~~' % (i['title'])
            user.save(u'অ-মুক্ত চিত্রের অধিক আকার সংক্রান্ত বিজ্ঞপ্তি দেয়া হয়েছে')"""
        for i in users:
            if(i['logtype'] !='newusers'):
                #-- Skip as not a user login
                continue
            i = i['title'][12:]
            k = patt.findall(i)
            if(len(k) == 0):
                #---Username has no problem
                continue
            #---Notify the user ---#
            user = pb.Page(bn, 'User talk:'+i)
            user.text+= "\n==ব্যবহারকারী নাম সম্পর্কে==\n{{subst:uw-username|এতে '''%s''' পদ(সমূহ) বিদ্যমান।}}\n~~~~" % (', '.join(k))
            user.save(u'ব্যবহারকারী নাম নীতিমালা পরিপন্থী হওয়ায় বিজ্ঞপ্তি প্রদান',minor=False)
            backlog[i] = now_st
    settings['detectUser']['backlog'] = backlog
def check(match):
    global cases
    cases += "\n|" + match.group(1) +"||" + ", ". join(patt.findall(match.group(1))) + "||~~~~~\n|-"
    return ""
if(config['editWar']["status"]):
    detect_edit_war()
if(config['detectUser']['status'] or config['reduceImage']["tag"]["status"]):
    patrolRecentChange()
    settings["editWar"]["last_access"] = now.strftime(ISO)
s = json.dumps(settings, indent = 4,ensure_ascii=False)
fp = open("setting.json","w")
fp.write(s)
fp.close()
print(now)