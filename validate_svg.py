from environment import *
# previously from setup import *
requests = pb.comms.http.requests
sess = requests.Session()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMPLEMENTOFDEFAULT"
validator = 'https://validator.w3.org/nu/?out=json&level=error'
tag = re.compile(
	u"\n*(\{\{ *([iI]n|অ)?(?:বৈধ এসভিজি|[vV]alid SVG) *\}\}|$)"
)
valid = True
def set_status(m):
    global change, valid
    if m.group(1) is '' or (m.group(2) is None) ^ valid:
        return '\n{{%sবৈধ এসভিজি}}' % ("" if valid else 'অ')
    change = False  
    return m.group(1)
def mass_validate(start='!'):
	images = bn.allimages(start=start)
	for i in images:
		validate(i)
   break
def validate(i):
	global valid, change
    print("Checking:",i.title())
    if i.title()[-4:].lower() is not '.svg':
        continue
    #check with api
    valid = len(sess.get(
    	validator,
    	params={'doc':i.get_file_url()}
   	).json()['messages'])
    valid = valid is 0
    change = True
    i.text = tag.sub(set_status, i.text, 1)
    if change:
        i.save("এসভিজির উৎসের বৈধতা যাচাই করা হয়েছে")
