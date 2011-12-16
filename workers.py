import os.path
from itertools import count
from decorator import decorator
import urllib2
from hashlib import md5
from functools import partial
from memcache import Client as MCClient
from base64 import b64encode, b64decode
from imgcompare.compare_images import get_image_visual_hash
from asyncore_http_client import async_request
from BeautifulSoup import BeautifulSoup as BS

mc = MCClient(['127.0.0.1:11211'])


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


class Worker(object):

    # how many simultanious instances of this
    # worker should we run ?
    max_workers = 1

    def __init__(self, handler):
        self.handler = handler

    # send up the results of our work
    def result(self,r):
        self.handler.send_result(r)

    # when we are done working, let someone know
    def work_finished(self):
        self.handler.work_finished()

    # this way we don't have to call run dir
    def __call__(self,*args,**kwargs):
        print 'running worker: %s' % type(self).__name__
        self.run(*args,**kwargs)


class GeneratePageURLs(Worker):
    """
    starting at the root find all the pages off root
    and pass them on. will try as many pages as we keep
    finding posts on. be careful this could get out of hand
    """
    def run(self, root_url):
        if not root_url.endswith('/'):
            root_url += '/'

        MAX_PAGES = 1000
        for i in xrange(1,MAX_PAGES):
            self.result(root_url + 'page/' + str(i))


class ValidatePageURL(Worker):
    max_workers = 10

    def __init__(self,*args):
        super(ValidatePageURL,self).__init__(*args)
        self.page_url = None

    def run(self, page_url):
        self.page_url = page_url
        async_request(page_url, self.validate_page)

    def validate_page(self, html):
        if html and 'post' in html: # TODO: better / does this work ?
            self.result(self.page_url)
        self.work_finished()


class GeneratePicURLs(Worker):
    min_img_size = 300
    max_workers = 10

    def __init__(self,*args):
        super(GeneratePicURLs,self).__init__(*args)
        self.page_url = None

    def run(self, page_url):
        self.page_url = page_url
        async_request(page_url, self.find_pic_urls)

    def find_pic_urls(self, html):
        if not html:
            return

        soup = BS(html)
        patterns = ['media.tumblr.com','tumblr.com/photo']

        # go through all the images in the page
        for img in soup.findAll('img'):
            src = img.get('src')
            # finding ones which match the patterns
            for p in patterns:
                if p in src:
                    # make sure the img is large enough
                    size = src[-7:-4]
                    if size.isdigit() and int(size) > self.min_img_size:
                        self.result(src)

        self.work_finished()


class SavePic(Worker):
    save_root = './output'
    max_workers = 10

    def __init__(self,*args):
        super(SavePic,self).__init__(*args)
        self.save_path = None
        self.pic_name = None

    def run(self, pic_url):
        self.pic_name = pic_url.rsplit('/',1)[-1]
        self.save_path = os.path.join(self.save_root,self.pic_name)
        if not os.path.exists(self.save_path):
            # asyncore http request
            # we pass as a callback to the async request a func
            # which will save the data and than call it's own callback
            # in this case the callback after saving the data down will
            # be to put off the next message
            async_request(pic_url, self.save_data)
        else:
            self.work_finished()

    def save_data(self, data):
        try:
            with open(self.save_path,'w') as fh:
                fh.write(data)
            self.result(path)
        except:
            pass
        finally:
            self.work_finished()


class GeneratePicDetails(Worker):
    max_workers = 10
    def run(self, pic_path):
        av_hash = get_image_visual_hash(pic_path)
        mc.set(str(pic_path)+':av_hash',str(av_hash))
        self.work_finished()

