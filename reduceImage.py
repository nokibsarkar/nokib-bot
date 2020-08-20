from PIL import Image as im
#--Image resize
temp = re.compile(u"\{\{ *(?:non-free reduce|মুক্ত নয় হ্রাস করুন) *[^\}]+\}\}",re.I)
#attribute to zervick
from xml.etree import ElementTree as etree
# is there a good way to get rid of this function?
def prepare_options(options):
    if 'width' not in options:
        options['width'] = None
    if 'height' not in options:
        options['height'] = None
    if 'longest' not in options:
        options['longest'] = None
    if 'shortest' not in options:
        options['shortest'] = None
    if 'margin' not in options:
        options['margin'] = '0'
    if 'trim' not in options:
        options['trim'] = False
    if 'frame' not in options:
        options['frame'] = False
def parse_length(value, def_units='px'):
    """Parses value as SVG length and returns it in pixels, or a negative scale (-1 = 100%)."""
    if not value:
        return 0.0
    parts = re.match(r'^\s*(-?\d+(?:\.\d+)?)\s*(px|in|cm|mm|pt|pc|%)?', value)
    if not parts:
        raise Exception('Unknown length format: "{}"'.format(value))
    num = float(parts.group(1))
    units = parts.group(2) or def_units
    if units == 'px':
        return num
    elif units == 'pt':
        return num * 1.25
    elif units == 'pc':
        return num * 15.0
    elif units == 'in':
        return num * 90.0
    elif units == 'mm':
        return num * 3.543307
    elif units == 'cm':
        return num * 35.43307
    elif units == '%':
        return -num / 100.0
    else:
        raise Exception('Unknown length units: {}'.format(units))

def resize_svg(tree, options):
    prepare_options(options)
    svg = tree.getroot()
    if 'width' not in svg.keys() or 'height' not in svg.keys():
        raise Exception('SVG header must contain width and height attributes')
    width = parse_length(svg.get('width'))
    height = parse_length(svg.get('height'))
    viewbox = re.split('[ ,\t]+', svg.get('viewBox', '').strip())
    if len(viewbox) == 4:
        for i in [0, 1, 2, 3]:
            viewbox[i] = parse_length(viewbox[i])
        if viewbox[2] * viewbox[3] <= 0.0:
            viewbox = None
    else:
        viewbox = None
    if width <= 0 or height <= 0:
        if viewbox:
            width = viewbox[2]
            height = viewbox[3]
        else:
            raise Exception('SVG width and height should be in absolute units and non-zero')
    if not viewbox:
        viewbox = [0, 0, width, height]

    # read and convert size and margin values
    margin = parse_length(options['margin'], 'mm')
    twidth = None
    theight = None
    if options['width']:
        twidth = parse_length(options['width'], 'mm')
    if options['height']:
        theight = parse_length(options['height'], 'mm')
    if options['longest']:
        value = parse_length(options['longest'], 'mm')
        if width > height:
            twidth = value
        else:
            theight = value
    if options['shortest']:
        value = parse_length(options['shortest'], 'mm')
        if width < height:
            twidth = value
        else:
            theight = value

    # twidth and theight are image dimensions without margins
    if twidth:
        if twidth < 0:
            twidth = -width * twidth
        elif twidth > 0:
            twidth = max(0, twidth - margin * 2)
    if theight:
        if theight < 0:
            theight = -height * theight
        elif theight > 0:
            theight = max(0, theight - margin * 2)

    if not twidth:
        if not theight:
            twidth = width
            theight = height
        else:
            twidth = theight / height * width
    if not theight:
        theight = twidth / width * height

    # set svg width and height, update viewport for margin
    svg.set('width', '{}px'.format(twidth + margin * 2))
    svg.set('height', '{}px'.format(theight + margin * 2))
    offsetx = 0
    offsety = 0
    if twidth / theight > viewbox[2] / viewbox[3]:
        # target page is wider than source image
        page_width = viewbox[3] / theight * twidth
        offsetx = (page_width - viewbox[2]) / 2
        page_height = viewbox[3]
    else:
        page_width = viewbox[2]
        page_height = viewbox[2] / twidth * theight
        offsety = (page_height - viewbox[3]) / 2
    vb_margin = page_width / twidth * margin
    svg.set('viewBox', '{} {} {} {}'.format(
        viewbox[0] - vb_margin - offsetx,
        viewbox[1] - vb_margin - offsety,
        page_width + vb_margin * 2,
        page_height + vb_margin * 2))

    # add frame
    if options['frame']:
        nsm = {
            'inkscape': 'http://www.inkscape.org/namespaces/inkscape',
            'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd'
        }
        layer = etree.SubElement(svg, 'g', nsmap=nsm)
        layer.set('{{{}}}groupmode'.format(nsm['inkscape']), 'layer')
        layer.set('{{{}}}label'.format(nsm['inkscape']), 'Frame')
        layer.set('{{{}}}insensitive'.format(nsm['sodipodi']), 'true')
        frame = etree.SubElement(layer, 'path')
        frame.set('style', 'fill:#ffffff;stroke:none')
        bleed = min(page_width, page_height) / 100
        frame.set('d', 'M {0} {1} v {3} h {2} v -{3} z M {4} {5} h {6} v {7} h -{6} z'.format(
            -viewbox[0] - vb_margin - offsetx - bleed,
            -viewbox[1] - vb_margin - offsety - bleed,
            page_width + (vb_margin + bleed) * 2,
            page_height + (vb_margin + bleed) * 2,
            viewbox[0], viewbox[1],
            viewbox[2], viewbox[3]))


def process_stream(options):
    options = {
    	'height':'100px',
    	'width':'10px'
    	}
    

def get_dimension(dim, threshold = 0.05, target = 100000):
    width = dim[0]
    height = dim[1]
    ratio = width/height
    width = (target*ratio)**0.5
    height = width/ratio
    dr = 1 - width*height/dim[0]/dim[1] #percentage of change
    if dr <= threshold:
        return None
    return int(width), int(height)
def thumb(path):
    k = im.open(path)
    dim = get_dimension(k.size, config['reduceImage']['tag']['minDeltaRate'], config['reduceImage']['tag']['resolution'])
    if dim is None:
        print('Skipping')
        return False
    k.thumbnail(dim,im.ANTIALIAS)
    try:
        #--- Save with metadata
        exif = k.info["exif"]
        k.save(path,exif=exif)
    except:
        #---Save without metadata
        k.save(path)
    return True
def fetch_csrf(k):
    return k
def reduceFUR():
    svg_tag = config['reduceImage']['tag']['tracker'] % ('svg')
    summary = config['reduceImage']['uploadSummary']
    files = pb.Category(bn,u"বিষয়শ্রেণী:" + config['reduceImage']['tracker']).members()
    for i in files:
        i = pb.FilePage(i) #Render as File page
        title = i.title(as_filename=True, with_ns=False).replace('_',' ')
        if(i.download(title) == False):
            continue
        t = False
        if(title[-4:].lower() == '.svg'):
            with open (title,"r") as fp:
                tree = etree.parse(fp)
            dim = i.latest_file_info
            dim = get_dimension(dim.size, config['reduceImage']['tag']['minDeltaRate'], config['reduceImage']['tag']['resolution'])
            if dim is not None:
                t = True
                resize_svg(tree, options)
                tree.write(title)
        else:
            t = thumb(title)
        i.text = temp.sub(u"{{subst:furd}}", i.text,1)
        if(t == False):
            #---Remove the tag
            i.save(u'ইতিমধ্যেই হ্রাসকৃত চিত্র হওয়ায় ট্যাগ পরিবর্তন')
            os.remove(title)
            #---Skip
            continue
        try:
            bn.upload(
                source_filename = title,
                filepage = i,
                 comment = summary,
                 ignore_warnings = fetch_csrf
                 )
            i.save(summary)
        except:
            print("Couldn't upload")
        os.remove(title)