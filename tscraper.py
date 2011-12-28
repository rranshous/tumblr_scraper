from lib.discovery import connect
from lib.scraper import Scraper, o as so
from lib.tumblrimages import TumblrImages, o as to
from lib.requester import Requester, o as ro


class BlogScraper(object):
    def __init__(self, blog_root_url):
        self.root_url = blog_root_url
        self.min_img_size = 300
        self.max_pages = 1000

    def generate_page_urls(self):
        if not root_url.endswith('/'):
            root_url += '/'
        yield root_url
        for i in xrange(1,self.max_pages):
            yield root_url + 'page/' + str(i)

    def validate_page(self, url):
        with connect(Requester) as c:
            r = c.urlopen(url)
        html = r.content
        try:
            if html and 'post' in html: # TODO: better / does this work ?
                return True
        except Exception, ex:
            print 'exception validating page: %s' % ex
        return False

    def filter_pic_urls(self, urls):
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

    def scrape(self):

        added = 0

        # go through the pages newest to oldest
        for page_url in self.generate_page_urls():

            # make sure it's a valid page
            if not self.validate_page(page_url):
                # we've hit an invalid page, done
                return added

            # get all the pics on the page
            with connect(Scraper) as c:
                img_urls = c.get_images(page_url)

            # go through the good img urls
            for img_url in self.filter_pic_urls(img_urls)

                print 'found: %s' % img_url
                # download the image
                image_data = self.download_image_data(img_url)

                # create a tumblr image
                tumblr_image = to.TumblrImage()
                tumblr_image.data = img_r.content
                tumblr_image.source_blog_url = self.root_url
                tumblr_image.source_url = img_r.url

                # when we add an image to the tumblrimage
                # service it will fill out stat's about the image
                # it will also not add the image if we've already
                # downloaded this image from this blog
                with connect(TumblrImages) as c:
                    tumblr_image = c.add_image(ti)

                # if our tumblr image now has an id than it was saved
                if not tumblr_image.id:
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
                img_r = c.urlopen(url)
            except Exception:
                # fail, try again ?
                print 'exception getting img: %s' % ex
                try:
                    img_r = c.urlopen(img_url)
                except Exception:
                    print 'refailed'
                    return None

        if not img_r or img_r.status_code != 200:
            return None

        return img_r.content
