from collections import namedtuple
import inspect

# create a named tuple which you can pass default values to
# by name and by args
def nnamedtuple(cls,*_tuple,**namedvalues):

    # make our tuple maluable for now
    _tuple = list(_tuple)

    # get the args for cls creation, minus cls
    args = inspect.getargspec(cls.__new__)[0][1:]

    # pad the tuple out
    arg_count = len(args)
    if len(_tuple) != arg_count:
        # we need the tuple to be the min len, pad w/ none's
        diff = arg_count - len(_tuple)
        _tuple = _tuple + [None for x in xrange(diff)]

    # fill in our args
    for index, arg in enumerate(args):
        if arg in namedvalues:
            _tuple[index] = namedvalues.get(arg)

    print '_tuple: '+str(_tuple)

    # now that we've got our tuple sorted out create the namedtuple
    nt = cls(*_tuple)

    return nt

# easy way to provide default non-None values for named tuple values
def dnamedtuple(name,fields,**defaults):
    # we are going to return a callable which
    # creates the named tuple and fills in the defaults
    NT = namedtuple(name,fields)
    print name,fields
    def create_named_tuple(*args,**kwargs):
        # the kwargs are going to set values when from nnamedtuple
        for k,v in defaults.iteritems():
            if not kwargs.get(k):
                kwargs[k] = v

        # this function returns a named tuple w/ initial values
        # set via kwargs
        nt = nnamedtuple(NT,*args,**kwargs)

        return nt
    return create_named_tuple

def Connector(name, fields):
    """
    Connects one worker to another.
    They are globally unique
    """

    # i want to make this in the future so that u
    # can turn on "tracking" and each connector
    # can build on another and the history chain
    # gets passed along

    # in order to make them globally unique we are going
    # to need to add some sort of identifier as initial
    # fields
    fields = ['connector_name'] + fields
    def create_connector(*args,**kwargs):
        t = dnamedtuple(name, fields)
        return t(*((name,)+args),**kwargs)
    return create_connector

# start with the root url for the tumblr site
# (root url,)
RootURL = Connector('RootURL',['url'])

# from there generate page urls for the site
# to search for pictures
# (root url, page_url)
PageURL = Connector('PageURL',['url'])

# take the page url and give off picture urls
# (root url, page_url, pic url)
PicURL = Connector('PicURL',['url'])

# pull in the image and save it, add in the save path
# this may end up being a key or a local path
# (root url, page_url, pic url, image path)
PicPath = Connector('PicPath',['path'])
