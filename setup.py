import re
import json
import datetime as dt
import time
import pywikibot as pb
bn = pb.Site("bn","wikipedia")
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
now = dt.datetime.now()
yesterday = now - dt.timedelta(days=1)
config = json.loads(pb.Page(bn,"user:নকীব বট/config.json").text)
r = pb.data.api.Request
ISO = "%Y-%m-%dT%H:%M:%SZ"
months = "((জান|ফেব্র)ুয়ার[িী]|ম(ে|ার্চ)|এপ্রিল|জু(ন|লা[ইঈ])|[অআ]গা?[সষ]্ট|((সেপ্ট|ন[বভ]|ডিস)েম্|অক্টো)[ভব]র)"
no ="০১২৩৪৫৬৭৮৯"
