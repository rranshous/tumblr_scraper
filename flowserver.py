

# the flow server is going to be a asyn core
# based server.

# we want to put a blocking request to the tuple server
# for our pipe's input, when we get something run
# the worker against it. whatever the worker yields
# up we push to the tuple server


class FlowServer(flow,host='localhost',port=9119):

    # async tuple client
    tc = tuple_client(host,port)

    def run_flow():

        for pipe in flow:

            # create a request of it's in conn
            in_req = pipe.in_conn()

            # create a callback which runs the worker
            # against incoming msgs and than puts in
            # another request for messages
            def run_worker(*work):
                for r in pipe.worker(*work):
                    out_msg = pipe.out_conn(*r)
                    ac.put(out_msg)
                ac.get_wait(in_req,run_worker)

            # put in our request for msgs
            ac.get_wait(in_req,run_worker)

    return run_flow
