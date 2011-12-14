import asyncore
from collections import namedtuple
from functools import partial
from tupilicious.asyncore_client import AsyncClient as TupleClient

# the flow server is going to be a asyn core
# based server.

# we want to put a blocking request to the tuple server
# for our pipe's input, when we get something run
# the worker against it. whatever the worker yields
# up we push to the tuple server

def make_new_request(pipe,tc):
    # subit our wait for more work

    # create a request of it's in conn
    in_req = pipe.in_conn()

    # put in our request for msgs
    print 'putting in request: ' + str(in_req) + ' ' + str(pipe)
    tc.get_wait(tuple(in_req),
                partial(run_worker,pipe,tc))

# create a callbtck which runs the worker
# against incoming msgs and than puts in
# another request for messages
def run_worker(pipe,tc,work):
    print 'running: ' + str(work) + ' ' + str(pipe.worker)
    # strip out the name of the connector
    work = work[1:]
    if pipe.worker.async:
        print 'running async'
        # instead of yielding we are going to use
        # a callback
        pipe.worker(*work,
                    callback=partial(send_work_result,pipe,tc))
    else:
        for r in pipe.worker(*work):
            send_work_result(pipe,tc,r)
    make_new_request(pipe,tc)

def send_work_result(pipe,tc,r):
    if r is not None and not isinstance(r,tuple):
        r = (r,)
    if r:
        out_msg = pipe.out_conn(*r)
        tc.put(tuple(out_msg))

def FlowServer(flow,host='localhost',port=9119):
    # Has limitation that a pipe can only have
    # one output (and input) connector

    # async tuple
    tc = TupleClient(host,port)

    def run_flow():
        for pipe in flow:
            make_new_request(pipe,tc)

        # start asyncore loop
        asyncore.loop()

    return run_flow
