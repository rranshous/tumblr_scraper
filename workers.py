import os.path
from itertools import count
from decorator import decorator
import urllib2
from hashlib import md5

@decorator
def worker(f, *args, **kwargs):
    f.worker = True
    return f(*args,**kwargs)

def get_html(url):
    print 'getting: %s' % url
    # check the disk
    cache_path = '/tmp/_c'+md5(url).hexdigest()
    if os.path.exists(cache_path):
        with open(cache_path,'r') as fh:
            print 'reading: %s' % cache_path
            return fh.read()
    try:
        d = urllib2.urlopen(url).read()
        with open(cache_path,'w') as fh:
            print 'writing: %s' % cache_path
            fh.write(d)
        return d
    except:
        return None

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
    if not os.path.exists(save_path):
        data = get_file(pic_url)
        # TODO: move / do something else
        with open(save_path,'wb') as fh:
            fh.write(data)
        yield save_path
