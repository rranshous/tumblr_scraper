from lib.discovery import connect
from lib.scraper import Scraper, o as so
from lib.tumblrimages import TumblrImages, o as to
from lib.requester import Requester, o as ro
from lib.thread_utils import thread_out_work

import time

def thread_scraper_work(sites,sync=False):
    print 'threading scraper'
    def work(site):
        try:
            print 'starting work: %s' % site
            r = (site,BlogScraper(site).update_scrape(sync=sync))
            print 'done work: %s' % site
            return r
        except Exception, ex:
            print 'site work exception: %s' % ex
            return (site,'ERR')

    args = [(site,) for site in sites]
    print 'args: %s' % args
    print 'starting threading'
    r = thread_out_work(args,work,1)
    print 'done'
    return r


class BlogScraper(object):
    def __init__(self, blog_root_url):
        self.root_url = blog_root_url
        if not self.root_url.endswith('/'):
            self.root_url += '/'
        self.min_img_size = 300
        self.max_pages = 1000

    def generate_page_urls(self):
        print 'generating page urls'
        for i in xrange(1,self.max_pages):
            yield self.root_url + 'page/' + str(i)

    def validate_page(self, url):
        print 'validating page: %s' % url
        try:
            with connect(Requester) as c:
                r = c.urlopen(ro.Request(url))
        except ro.Exception, ex:
            print 'oException validating, retrying: %s %s' % (url,ex.msg)
            with connect(Requester) as c:
                r = c.urlopen(ro.Request(url))
        except Exception, ex:
            print 'Exception validating, retrying: %s %s' % (url,ex)
            with connect(Requester) as c:
                r = c.urlopen(ro.Request(url))
        html = r.content
        try:
            if html and 'post' in html: # TODO: better / does this work ?
                return True
        except Exception, ex:
            print 'exception validating page: %s' % ex
        return False

    def filter_pic_urls(self, urls):
        print 'filtering pic urls'
        for src in urls:
            # TODO: better
            # finding ones which match the patterns
            patterns = ['media.tumblr.com','tumblr.com/photo']
            found = False
            for p in patterns:
                if p in src:
                    # make sure the img is large enough
                    size = src[-7:-4]
                    if size.isdigit() and int(size) > self.min_img_size:
                        found = True
                        yield src
                        break
                if found:
                    break


    def update_scrape(self,sync=False):
        """
        starts at the newest page and scrapes until it
        finds an image it's already stored

        if sync is true will scrape entire site not stopping
        when it finds repeat
        """

        print 'update scraping start'

        added = 0

        # go through the pages newest to oldest
        for page_url in self.generate_page_urls():

            # make sure it's a valid page
            try:
                if not self.validate_page(page_url):
                    # we've hit an invalid page, done
                    return added
            except ro.Exception, ex:
                print 'oException validating: %s %s' % (page_url,ex.msg)
                return self.validate_page(page_url)
            except Exception, ex:
                print 'Exception validating: %s %s' % (page_url,ex)
                return self.validate_page(page_url)

            # get all the pics on the page
            with connect(Scraper) as c:
                print 'getting page images'
                try:
                    img_urls = c.get_images(page_url)
                except so.Exception, ex:
                    print 'oException getting images: %s %s' % (page_url,ex.msg)
                    if not sync:
                        raise ex
                except Exception, ex:
                    print 'Exception getting images: %s %s' % (page_url,ex)
                    if not sync:
                        raise ex

                print 'images: %s' % len(img_urls)

            # go through the good img urls
            for img_url in self.filter_pic_urls(img_urls):
                print 'img url: %s' % img_url

                # download the image
                print 'downloading'
                try:
                    image_data = self.download_image_data(img_url)
                except ro.Exception, ex:
                    print 'oException downloading data: %s %s' %(img_url,ex.msg)
                    if not sync:
                        raise ex
                except Exception, ex:
                    print 'Exception downloading data: %s %s' % (img_url,ex)
                    if not sync:
                        raise ex

                try:
                    assert image_data, "image found no data"
                except Exception, ex:
                    print 'no image data: %s' % img_url
                    if not sync:
                        raise ex

                # create a tumblr image
                tumblr_image = to.TumblrImage()
                tumblr_image.data = image_data
                tumblr_image.source_blog_url = self.root_url
                tumblr_image.source_url = img_url
                tumblr_image.downloaded_at = time.time()

                # when we add an image to the tumblrimage
                # service it will fill out stat's about the image
                # it will also not add the image if we've already
                # downloaded this image from this blog
                print 'uploading'
                try:
                    with connect(TumblrImages) as c:
                        tumblr_image = c.add_image(tumblr_image)
                except to.Exception, ex:
                    print 'oException adding image: %s %s' % (img_url,ex)
                    if not sync:
                        raise ex
                except Exception, ex:
                    print 'Exception adding image: %s %s' % (img_url,ex)
                    if not sync:
                        raise ex

                try:

                    assert tumblr_image.data, "image has no data"
                    assert tumblr_image.xdim, "image has no x"
                    assert tumblr_image.ydim, "image has no y"
                    assert tumblr_image.size, "image has no size"
                    assert tumblr_image.vhash, "image has no vhash"
                    assert tumblr_image.shahash, "image has no sha"

                except Exception, ex:
                    print 'assert fail: %s %s' % (img_url,ex)
                    if not sync:
                        raise ex

                # if our tumblr image now has an id than it was saved
                if not tumblr_image.id and not sync:
                    print 'image already uploaded'
                    # we've already added this image before
                    # we're done updating this blog
                    return added

                # we did it!
                added += 1

        return added

    def download_image_data(self, url):
        # we want to download the image
        with connect(Requester) as c:
            try:
                img_r = c.urlopen(ro.Request(url))
            except Exception, ex:
                # fail, try again ?
                print 'exception getting img: %s' % ex
                try:
                    img_r = c.urlopen(ro.Request(img_url))
                except Exception:
                    print 'refailed'
                    return None

        if not img_r or img_r.status_code != 200:
            return None

        return img_r.content


if __name__ == '__main__':
    sites = [l.strip() for l in open('./sites.txt','r').readlines()]
    thread_scraper_work(sites,True)
