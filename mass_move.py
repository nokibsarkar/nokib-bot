from environment import *
# previously from setup import *
summary = u'[[উইকিপিডিয়া:বট/অনুমোদনের অনুরোধ/নকীব বট/কাজ ৩|আলোচনাসাপেক্ষে]] বট কর্তৃক [[%s]] হতে {{মুক্ত নয় হ্রাসকৃত}} অপসারণ'
cats = pb.Category('বিষয়শ্রেণী:৭ দিন পূর্বের হ্রাসকৃত অ-মুক্ত ফাইল').members()
subst = re.compile('\s*\{\{ *মুক্ত নয় হ্রাসকৃত[^\}]+\}\}\s*')
def main():
    for i in cats:
        i.text = subst.sub('',i.text)
        i.save(summary)