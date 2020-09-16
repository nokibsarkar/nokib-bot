from setup import *
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
date_patt = re.compile('(['+no+']{1,2} ('+ month_patt+') ['+ no+']{4}) \(ইউটিসি\)\s*(?:(?:\{\{ *[Aa]bot *\}\}|\|\}|<!--(?:(?!-->)[\s\S])*-->|<\/\S+>)\s*)*$')
DATE = '%d %b %Y' #pattern of the date
setting = re.compile('\{\{\s*স্বয়ংক্রিয় সংগ্রহশালা\s*([^\}]*)\}\}')
setting_fetch = re.compile('\| *([^= ]+) *= *([^\n\|]+)')
section = re.compile('(\s*\n=+ *(?P<section>[^=]+)=+\n(?:(?!\n=+[^=]+=+\n)[\s\S])*)')
ns_mapping ={
    "4":'[wW](?:ikipedia|[Pp])|উইকিপিডিয়া',
    "1":'আলাপ|[Tt]alk',
    "3":'[Uu]ser talk|ব্যবহারকারী আলাপ',
    "11":'[tT]emplate talk|টেমপ্লেট আলোচনা',
    "5":'[wW](?:ikipedia|[Pp]) talk|উইকিপিডিয়া আলোচনা',
    "15":'[cC]ategory talk|বিষয়শ্রেণী আলোচনা',
    "7":'চিত্র আলোচনা',
    "9":'মিডিয়াউইকি আলোচনা',
    "13":'সাহায্য আলোচনা',
    "101":'প্রবেশদ্বার আলোচনা',
    "2":'[uU]ser|ব্যবহারকারী'
}
c_patt = re.compile('\s*\| *current-index *= *\d*\s*|$')
sep = re.compile("\s*,\s*")
#### Constant declared #####
###--- Declaring util function ----#
def fetch_setting(txt):
    k = setting.search(txt)
    if(k and k.group(1)):
        k = k.group(1)
        k = dict(defaults + setting_fetch.findall(k) + [('string',k)])
        k['$'] = k['current-index']
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
    except: # an error occurred so stay safe and skip
        return False
def to_en(txt):
    s = ""
    for i in txt:
        try:
            s += numers[i]
        except:
            s+=i
    return s
def archive_section(match):
    content = match.group(1)
    if(is_old(content)):
        title = match.group(2).strip()
        Archive['sections'].append(title)
        Archive["content"] = '%s%s' % (Archive["content"], content)
        return ""
    return content # skip the section
def fetch_backlink(title,ns):
    ns = ns_mapping[str(ns.id)]
    backlink = "(\[\[ *(?:"
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
    return en2bn(Archive['config'][m.group(1)])
#--- Util functions declared-----
#----- Main archival function------
def archive():
    print("Archival Script Started")
    pages = pb.Category(bn,u'Category:'+config['archiveTalk']['tracker']).members()
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
        summary = u'বট কর্তৃক %sটি অনুচ্ছেদ স্বয়ংক্রিয়ভাবে সংগ্রহশালায় স্থানান্তর' % en2bn(len(Archive['sections']))
        pg.text += Archive['content']
        pg.save(summary) #archive page
        backlink = fetch_backlink(i.title(with_ns=False,underscore=False),i.namespace())
        backlinks = i.backlinks(follow_redirects = False)
        for j in backlinks:
            Archive['fixed-section'] = 0
            j.text = backlink.sub(fix_backlink,j.text)
            if Archive['fixed-section'] is 0:
                #no fix
                continue
            j.save(summary + u'িত হওয়ায় %sটি সংযোগ ঠিক করা হয়েছে' % (en2bn(Archive['fixed-section'])))
            Archive['backlinks'] += 1  
        check_overflow(pg, i.title())
        t = c_patt.sub('\n|current-index = %s\n' % Archive['config']['$'], Archive['config']['string'], 1)
        i.text = setting.sub('{{স্বয়ংক্রিয় সংগ্রহশালা\n' + t + '}}',i.text, 1) # update current index
        if(Archive['backlinks']):
            summary += u' এবং %sটি পশ্চাৎসংযোগ ঠিক করা হয়েছে' % (en2bn(Archive['backlinks']))
        i.save(summary) # main page
    print("Archival Script End")
