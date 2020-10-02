from environment import *
# previously from setup import *
summary = u'[[উইকিপিডিয়া:বট/অনুমোদনের অনুরোধ/নকীব বট/কাজ ৩|আলোচনাসাপেক্ষে]] বট কর্তৃক [[%s]] হতে [[%s]] - নামে স্থানান্তর'
to_move = re.compile(
	'# *\[\[ *([^\]]+)\]\] *- *\[\[([^\]]+)\]\]'
	)
def move(m):
    source = pb.Page(bn,m.group(1).strip())
    target = m.group(2).strip()
    source.move(
    	target,
    	reason = summary % (m.group(1), target),
    	movetalk = True
    	)
def main():
    page = pb.Page(bn,'ব্যবহারকারী:Nokib Sarkar/খেলাঘর২')
    page.text = to_move.sub('', move)
    page.save('সফল!!!!!')