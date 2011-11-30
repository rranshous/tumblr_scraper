
from decorator import decorator
import urllib2

@decorator
def worker(f, *args, **kwargs)
    f.worker = True
    return f(*args,**kwargs)

def get_html(url):
    try:
        return urllib2.urlopen(url).read()
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

    for i in count(2):
        url = root_url + 'page/' + i

        # check and see if the page has any posts
        html = get_html(url)

        if not html:
            continue

        if 'post' in html: # TODO: better / does this work ?
            yield url

        # no post = last page
        else:
            break

@worker
def generate_pic_urls(page_url):
    """
    inspect the page and pull out all the post pictures
    urls
    """
    import BeautifulSoup as BS
    html = get_html(page_url)
    if html:
        soup = BS(html)
        patterns = ['media.tublr.com','tumblr.com/photo']
        for url in soup.findAll('img'):
            for p in patterns:
                if p in img.get('src'):
                    yield img.src

@worker
def generate_pic_path(pic_url):
    """
    download the pic and save it somewhere put out the
    save path
    """
    data = get_file(pic_url)
    # TODO: move / do something else
    save_root = './output'
    pic_name = pic_url.rsplit('/',1)[-1]
    save_path = os.path.join(save_root,pic_name)
    with open(save_path,'wb') as fh:
        fh.write(data)

    yield save_path
