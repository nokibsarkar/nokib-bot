# -*- coding: utf-8 -*- 
from environment import *
# previously from setup import *
import os
from PIL import Image as im
from xml.etree import ElementTree as etree
#--Image resize
temp = re.compile(u"\{\{ *(?:[Nn]on-free reduce|মুক্ত নয় হ্রাস করুন)[^\}]*\}\}",re.I)
#attribute to zervick
def parse_length(value, def_units='px'):
    """Parses value as SVG length and returns it in pixels, or a negative scale (-1 = 100%)."""
    if not value:
        return 0.0
    parts = re.match(r'^\s*(-?\d+(?:\.\d+)?)\s*(in|[cm]m|p[tcx]|%)?', value)
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
def resize_svg(tree, target_width, target_height):
    svg = tree.getroot()
    width = parse_length(svg.get('width'))
    height = parse_length(svg.get('height'))
    viewbox = re.split('[ ,\t]+', svg.get('viewBox', '').strip())
    if len(viewbox) == 4:
        for i in range(4):
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
    # read and convert size
    twidth = parse_length(str(target_width), 'px')
    theight = parse_length(str(target_height), 'px')
    # twidth and theight are image dimensions without margins
    # set svg width and height, update viewport for margin
    svg.set('width', '{}px'.format(twidth))
    svg.set('height', '{}px'.format(theight))
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
    svg.set(
            'viewBox', 
            '{} {} {} {}'.format(
                viewbox[0] - offsetx,
                viewbox[1] - offsety,
                page_width,
                page_height
            )
        )
def get_dimension(dim, threshold = 0.05, target = 100000):
    width = dim[0]
    height = dim[1]
    ratio = width/height
    width = (target*ratio)**0.5
    height = width/ratio
    dr = 1 - width * height/dim[0]/dim[1] #percentage of change
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
        k.save(path,exif = exif)
    except:
        #---Save without metadata
        k.save(path)
    return True
def fetch_csrf(k):
    return k
def reduceFUR():
    #---Login
    bn.login()
    #----
    parser = etree.XMLParser(encoding='utf-16')
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
                tree = etree.parse(fp,parser)
            dim = i.latest_file_info
            dim = get_dimension((dim.width,dim.height), config['reduceImage']['tag']['minDeltaRate'], config['reduceImage']['tag']['resolution'])
            try:
                resize_svg(tree, dim[0],dim[1])
                tree.write(title)
                t = True
            except Exception as e:
                 print("%s is Already reduced" % title)
                 pass
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
        except Exception as e:
            print("Couldn't upload: %s" % e)
            pass
        os.remove(title)