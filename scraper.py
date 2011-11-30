

# there are alot of different types of themes for tumblr
# need to try and find a generic pattern

# start by iter'n the page urls
# than explode that into the pic urls per page
# than download each and add d/l path?


from flow import tublr_scrape


if __name__ == '__main__':
    # server which will host a flow
    from flowserver import FlowServer

    # get'r goin'
    server = FlowServer(flow)
    server() # starts the server
