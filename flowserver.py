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

# create a callbtck which runs the worker
# against incoming msgs and than puts in
# another request for messages

class WorkHandler(object):
    def __init__(self,server,pipe):
        self.pipe = pipe
        self.server = server

    def run_work(self, work):
        # create our worker
        worker = self.pipe.worker(self)

        # strip the connector name
        work = work[1:]

        # run the worker
        worker(*work)

    def __call__(self, work):
        # we have some work to preform
        self.run_work(work)

    def work_finished(self):
        # our work is done, let the server know
        self.server.work_finished(self.pipe)

    def send_result(self,r):
        # our worker has a result, pass it on
        self.server.send_work_result(self.pipe,r)

class FlowServer(object):
    def __init__(self, flow, host='localhost', port=9119):
        self.flow = flow
        self.host = host
        self.port = port
        self.tc = TupleClient(host,port)

    def run_flow(self):
        for pipe in self.flow:
            for i in xrange(pipe.worker.max_workers):
                # we want tc connection for each worker instance
                self.tc.max_handlers += 1
                self.make_work_request(pipe)

        # start asyncore loop
        asyncore.loop()

    def make_work_request(self, pipe):
        in_req = pipe.in_conn()
        self.tc.get_wait(tuple(in_req),
                         WorkHandler(self,pipe))

    def send_work_result(self, pipe, r):
        if r is not None and not isinstance(r,tuple):
            r = (r,)
        if r:
            out_msg = pipe.out_conn(*r)
            self.tc.put(tuple(out_msg))

    def work_finished(self, pipe):
        # if we are doing requests serially (only one worker at a time)
        # time to make another request for work
        self.make_work_request(pipe)
