

def iter_site_urls():
    # hack for now, cmd line?
    urls = ['http://thehottestamateurs.tumblr.com/',
            'http://mrmt.tumblr.com/',
            'http://reblogmygirlfriend.tumblr.com/']
    for url in urls:
        yield url

def explode_pages(root_urls):
    # go through the site getting the page urls
    # from root until we run out

    for root_url in root_urls:

        # this url counts
        yield root_url

        # make sure our root url ends in a slash
        if not root_urls.endswith('/'):
            root_url += '/'

        # now we need to try and go through all the pages
        # off the root, we'll keep going through pages
        # until we find one w/o any "post"s
        for i in count(2):
            url = root_url + 'page/' + i



def run():

    # iter all the site urls
    sites_urls = iter_site_urls()

    # add in the page urls
    pages_pipe = explode_pages(site_urls)

    # turn the html to soup
    soup_pipe = soup_pages(pages_pipe)

    #

    # now we want to explode w/ pics
    pics_pipe = explode_pics(pages_pipe)

    # and now download the pics
    downloaded_pipe = download_pics(pics_pipe)
