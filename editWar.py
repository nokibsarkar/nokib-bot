import pywikibot as pb
import json
from datetime import datetime as dt
bn = pb.Site("bn","wikipedia")
r = pb.data.api.Request
ISO = "%Y-%m-%dT%H:%M:%SZ"
config =json.loads(pb.Page(bn,"user:নকীব বট/config.json").text)["editWar"]
settings = json.loads(open("setting.json","r").read())
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
        "rvprop":"tags|user|ids",
        }
    data = r(site=bn,parameters=data).submit()
    return data["query"]["pages"][0]["revisions"]
def detect_edit_war():
    trusted = config["trustedUsers"]
    LOG = pb.Page(bn,u"user:নকীব বট/সম্পাদনা যুদ্ধ/"+en2bn(int(settings["editWar"]["count"]/10 + 1)))
    admin = pb.Page(bn,"উইকিপিডিয়া:প্রশাসকদের আলোচনাসভা")
    now = dt.now().strftime(ISO)
    last = settings["editWar"]["last_access"]
    data1 = {
        "action":"query",
     "format":"json", 
     "list":"recentchanges",
     "rctype":"edit",
     "rcend":now,
     "rcdir":"newer",
            "rclimit":"max",
            "rctag":"mw-undo",
            "rcstart":last,
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
            "grcstart":last,
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
        print("Total scanning : "+str(len(changes)))
        for i in changes:
            attacks = 0
            warriors = set()
            title=i["title"]
            revs = fetch(title,config["scanRevision"])
            st = u"'''শিরোনাম:'''"+title+u"\n{|class='wikitable collapible' collapsed\n|-\n!সংস্করণ !!সম্পাদক !!সম্পাদনার ধরন\n|-\n"
            for j in revs:
                user = j["user"]
                st+="|[[বিশেষ:পার্থক্য/"+str(j["revid"])+"|"+str(j["revid"])+"]]||[[ব্যবহারকারী:"+user+"|]]||"
                if(user not in trusted and ("mw-undo" in j["tags"] or "mw-rollback" in j["tags"])):
                    attacks+=1
                    warriors.add(user)
                    if("mw-undo" in j["tags"]):
                        st+="'''পুনর্বহাল'''"
                    else:
                        st+="'''রোলব্যাক'''"
                elif(user in warriors):
                    st+="সাধারণ"
                else:
                    st+="সাধারণ\n|-\n"
                    break
                st+="\n|-\n"
            st+="|}"
            if(len(warriors) > config["minWarrior"]):
                print("Title suspected : "+title)
                print("Warriors are "+str(warriors))
                if(attacks > config["suspectWar"]):
                    admin.text+=u"\n{{subst:user:নকীব বট/সম্পাদনা যুদ্ধ|"+title+"|"+LOG.title()+"|"+en2bn(settings["editWar"]["count"])+"|"+str(attacks)+"}}\n"+st +"\n-~~~~"
                    if(attacks > config["confirmWar"]):
                        print("Result : Confirmed")
                        LOG.text+= "\n== "+ en2bn(settings["editWar"]["count"]) +"==\n"+st
                        settings["editWar"]["count"]+=1
                        if(settings["editWar"]["count"]%10 == 0):
                            LOG.save(u"নতুন সম্পাদনা যুদ্ধ এবং সংগ্রহশালা সমাপ্তি")
                            LOG = pb.Page(bn,u"user:নকীব বট/সম্পাদনা যুদ্ধ/"+en2bn(int(settings["editWar"]["editWar"]["count"]/10 + 1)))
                            LOG.text = "{{user:নকীব বট/বিজ্ঞপ্তি}}"
                        
                        #notify the users
                        for user in warriors:
                            user = pb.Page(bn,"User talk:"+user)
                            user.text+="\n== "+i["title"]+"-এ সম্পাদনা যুদ্ধ == \n{{subst:Uw-3rr|"+i["title"]+"}}\n-~~~~"
                            try:
                                user.save("[["+title+u"]] নিবন্ধে সম্পাদনা যুদ্ধ সম্পর্কে সতর্ক করা হয়েছে")
                            except:
                                pass
                            #request protection"""
        try:
            admin.save(u"সম্পাদনা যুদ্ধ সম্পর্কে নজরদারির অনুরোধ")
            LOG.save(u"নতুন সম্পাদনা যুদ্ধ")
        except:
            pass
    fp = open("setting.json","w")
    settings["editWar"]["last_access"]=now
    fp.write(json.dumps(settings))
    fp.close()
if(config["status"]):
    detect_edit_war()
print(dt.now())