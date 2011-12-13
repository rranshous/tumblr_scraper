import os.path
from itertools import count
from decorator import decorator
import urllib2
from hashlib import md5
from memcache import Client as MCClient
from base64 import b64encode, b64decode
from imgcompare.compare_images import get_image_visual_hash

mc = MCClient(['127.0.0.1:11211'])

@decorator
def worker(f, *args, **kwargs):
    f.worker = True
    return f(*args,**kwargs)

def get_html(url):
    print 'getting: %s' % url
    # check the cache
    key = str(url)+':webcache'
    d = mc.get(key)
    if d:
        d = b64decode(d)
    if not d:
        try:
            d = urllib2.urlopen(url).read()
            mc.set(key,b64encode(str(d)))
        except:
            d = None
    return d

def get_file(url):
    return get_html(url)

@worker
def generate_page_urls(root_url):
    """
    starting at the root find all the pages off root
    and pass them on. will try as many pages as we keep
    finding posts on. be careful this could get out of hand
    """
    if not root_url.endswith('/'):
        root_url += '/'

    print 'generating page urls: %s' % root_url

    MAX_PAGES = 1000
    for i in xrange(1,MAX_PAGES):
        yield root_url + 'page/' + str(i)

@worker
def validate_page_urls(page_url):
    """
    takes a page url and checks to make sure there is a post
    on the page, if there is a post it's considered valid
    and is passed on
    """
    # check and see if the page has any posts
    html = get_html(page_url)

    print 'validating: %s' % page_url

    if html and 'post' in html: # TODO: better / does this work ?
        print 'found: %s' % page_url
        yield page_url

@worker
def generate_pic_urls(page_url):
    """
    inspect the page and pull out all the post pictures
    urls
    """
    from BeautifulSoup import BeautifulSoup as BS
    html = get_html(page_url)
    if html:
        print 'making soup'
        soup = BS(html)
        patterns = ['media.tumblr.com','tumblr.com/photo']
        print 'images: %s' % len([x for x in soup.findAll('img')])
        for img in soup.findAll('img'):
            src = img.get('src')
            for p in patterns:
                if p in src:
                    # make sure the img is large
                    size = src[-7:-4]
                    if size.isdigit() and int(size) > 300:
                        print 'found: %s' % src
                        yield src

@worker
def generate_pic_path(pic_url):
    """
    download the pic and save it somewhere put out the
    save path
    """
    # dont over write
    save_root = './output'
    pic_name = pic_url.rsplit('/',1)[-1]
    save_path = os.path.join(save_root,pic_name)
    if os.path.exists(save_path):
        yield save_path

    try:
        data = get_file(pic_url)
        # TODO: move / do something else
        with open(save_path,'wb') as fh:
            fh.write(data)
        yield save_path
    except Exception, ex:
        print 'exception writing file: %s' % ex

@worker
def generate_pic_details(pic_path):
    """
    calculates the pics av_hash and saves it
    """
    av_hash = get_image_visual_hash(pic_path)
    print 'generated av hash: %s' % pic_path
    mc.set(str(pic_path)+':av_hash',str(av_hash))
    yield None

