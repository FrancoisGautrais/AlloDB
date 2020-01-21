
from . import log
from .socketwrapper import SocketWrapper, ServerSocket
from .httprequest import HTTPResponse, HTTPRequest, HTTP_OK, STR_HTTP_ERROR, HTTP_NOT_FOUND
from .utils import Callback, start_thread
import os
import time
from .waitqueue import WaitQueue
import threading


class HTTPServer(ServerSocket):
    SINGLE_THREAD="single"
    SPAWN_THREAD="spawn"
    CONST_THREAD="const"
    N_THREAD=4
    def __init__(self, ip="localhost", attrs={ "mode" : SPAWN_THREAD}):
        ServerSocket.__init__(self)
        self._ip=ip
        if isinstance(attrs, str): attrs={ "mode": attrs }
        self.mode=attrs["mode"] if "mode" in attrs else HTTPServer.CONST_THREAD
        if self.mode==HTTPServer.CONST_THREAD:
            self.waitqueue=WaitQueue()
            self.n_thread=attrs["n_threads"] if "n_threads" in attrs else HTTPServer.N_THREAD

    def listen(self, port):
        self._port = port
        self.bind(self._ip, self._port)
        log.info("Listening at http://"+self._ip+":"+str(self._port))
        if self.mode==HTTPServer.CONST_THREAD:
            self.threads=[]
            for i in range(self.n_thread):
                self.threads.append( start_thread(Callback(HTTPServer._handlerequest_loop, self, i)))
        while True:
            x=super().accept()
            if self.mode==HTTPServer.SINGLE_THREAD:
                self._handlerequest_oneshot(HTTPRequest(x))
            elif self.mode==HTTPServer.SPAWN_THREAD:
                req = HTTPRequest(x)
                start_thread( Callback(HTTPServer._handlerequest_oneshot, self, req))
            elif self.mode==HTTPServer.CONST_THREAD:
                self.waitqueue.enqueue( (x, time.time()) )

    def _handlerequest_loop(self, i):
        soc, t=self.waitqueue.dequeue()
        req = HTTPRequest(soc) if soc else None

        while req:
            req.start_time=t
            req.parse()
            res = HTTPResponse(200, )

            self.handlerequest(req, res)
            res.write(req.get_socket())
            req.get_socket().close()

            req.stop_time = time.time()
            req.total_time = req.stop_time - req.start_time

            log.debug(req.method+" "+req.url+" -> %.3f ms" % (req.total_time*1000))
            #attente de la prochaine requete
            soc, t = self.waitqueue.dequeue()
            req = HTTPRequest(soc) if soc else None

    def _handlerequest_oneshot(self, req : HTTPRequest):
        req.parse()
        res=HTTPResponse(200, )
        self.handlerequest(req, res)

        res.write(req.get_socket())
        req.get_socket().close()
        log.debug(req.method + " " + req.url + " -> %.3f ms" % (req.total_time * 1000))

    def handlerequest(self, req, res):
        pass


    def serve_file(self, req: HTTPRequest, res : HTTPResponse):
        res.serve_file(os.path.join(self.www_dir, req.path[1:]))

    def serve_file_gen(self, req: HTTPRequest, res : HTTPResponse, data):
        res.serve_file_gen(os.path.join(self.www_dir, req.path[1:]), data)


