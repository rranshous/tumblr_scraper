
# the Pipe connects up worker and connector series
from piping import Pipe

# the workers receive a message and than put off another message
from workers import GeneratePageURLs, ValidatePageURL, GeneratePicURLs, \
                    SavePic, GeneratePicDetails

# the connectors specify the message pattern between pipes
from connectors import RootURL, PageURL, ValidPageURL, PicURL, PicPath


# for now a flow is just a list
class Flow(list):
    """
    a set of pipes which all relate to eachother
    """
    def __init__(self, *items):
        for i in items:
            self.append(i)


## setup our piping
tumblr_scrape = Flow(

    # root url =>> page urls
    Pipe(RootURL, GeneratePageURLs, PageURL),

    # page urls =>> pages with blogs
    Pipe(PageURL, ValidatePageURL, ValidPageURL),

    # page url =>> pic urls
    Pipe(ValidPageURL, GeneratePicURLs, PicURL),

    # pic url =>> pic save path
    Pipe(PicURL, SavePic, PicPath),

    # pic save path =>> nothing
    Pipe(PicPath, GeneratePicDetails, None),

    # not sure what we'll do next, reporting, storing of reports?
    # idk
)
