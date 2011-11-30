
# the Pipe connects up worker and connector series
from piping import Pipe

# the workers receive a message and than put off another message
from workers import generate_root_urls, generate_page_urls \
                    generate_pic_urls, generate_pic_path

# the connectors specify the message pattern between pipes
from connectors import RootURL, PageURL, PicURL, PicPath


# for now a flow is just a list
class Flow(list):
    """
    a set of pipes which all relate to eachother
    """
    pass


## setup our piping
tumblr_scrape = Flow(

    # root url =>> page urls
    Pipe(RootURL,generate_page_urls,PageURL),

    # page url =>> pic urls
    Pipe(PageURL, generate_pic_urls, PicURL),

    # pic url =>> pic save path
    Pipe(PicURL, generate_pic_path, PicPath)

    # not sure what we'll do next, reporting, storing of reports?
    # idk
)
