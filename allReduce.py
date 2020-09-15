# -*- coding: utf-8 -*-
import re
import datetime as dt
import json
import pywikibot as pb
bn = pb.Site("bn","wikipedia")
r = pb.data.api.Request
MIME = re.compile('image\/(.+)')
non_free = re.compile('\{\{\s*(?:মুক্ত নয়|non-free) *(?!হ্রাস(?:কৃত| কর(?:ুন|বেন না))|(?:no )?reduced?)',re.I)
tagged = re.compile('\{\{\s*(?:মুক্ত নয়|non-free) (?:হ্রাস(?:কৃত| কর(?:ুন|বেন না))|(?:no )?reduced?)', re.I)
config =json.loads(pb.Page(bn,"user:নকীব বট/config.json").text)
def __main__():
    files = pb.Category(bn,"category:সকল মুক্ত নয় মিডিয়া").members(namespaces=['File'])
    if(1):
        for i in files:
            i = pb.FilePage(i)
            info = i.latest_file_info
            p1 = MIME.match(info['mime'])
            if(p1 == None):
                #skip as it is not an image
                continue
            p1 = p1.group(1)
            if(p1 != 'svg'):
                p1 = 'image'
            height = info['height']
            width = info['width']
            
            resolution = height * width
            target_res = 100000
            if(1 - target_res/resolution < 0.05):
                #skip as it is small enough
                continue
            if(non_free.search(i.text) == None or tagged.search(i.text)):
                #Freely licensed or already tagged
                continue
            #--- Overly pixeled non-free image
            fp = i
            fp.text = u'{{মুক্ত নয় হ্রাস করুন|type=%s|bot=নকীব বট}}\n' % (p1) + fp.text
            fp.save(u'অধিক রেজ্যুলেশনের অ-মুক্ত চিত্র হ্রাসকরণের জন্য ট্যাগ করা হয়েছে')
__main__()