from environment import *
# previously from setup import *
import pymysql
conn = pymysql.connect(
	host = 'bnwiki.web.db.svc.eqiad.wmflabs',
	database='bnwiki_p',
	read_default_file = '~/replica.my.cnf',
	charset='utf8mb4'
	)
res=[]
with conn.cursor() as cur:
    limit = cur.execute(
    	"SELECT user_name, user_editcount FROM user WHERE user_name NOT REGEXP '.+([bB][oO][tT]|বট)' ORDER BY user_editcount DESC LIMIT 1000"
    	)
    st = """===১-১০০০===
'''সর্বশেষ হালনাগাদ করা হয়েছে {{সময় আগে|%s|purge=y}}''' 

{| class="wikitable"
|- style="white-space:nowrap;"
! নং
! ব্যবহারকারী নাম
! সম্পাদনার সংখ্যা
|-"""% dt.datetime.utcnow().isoformat()[:19]
    res = cur.fetchall()
    for i in range(limit):
        st= '%s\n|%s||[[ব্যবহারকারী:%s|]]||%s\n|-' % (st, en2bn(i+1), str(res[i][0],'utf8'), en2bn('{:,}'.format(res[i][1])))
    st = '%s\n|}' % st
    pg = pb.Page(bn,u'উইকিপিডিয়া:সম্পাদনার সংখ্যা অনুযায়ী উইকিপিডিয়ানদের তালিকা/১-১০০০')
    pg.text = st
    pg.save(u"পরিসংখ্যান হালনাগাদ করা হয়েছে")
    conn.close()