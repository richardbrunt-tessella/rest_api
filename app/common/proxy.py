import copy
import json
from flask.ext.restful import abort
from flask import request, Response
import requests
import logging
from auth import TokenAuthentication

__author__ = 'andreap'

CHUNK_SIZE = 1024
ALLOWED_HEADERS = ['Content-Type']
class ProxyHandler():

    def __init__(self, allowed_targets = {}):
        self.allowed_targets = allowed_targets

    def proxy(self,
              domain,
              url,
              token_payload,
              post_payload =None,
              ):
        """Fetches the specified URL and streams it out to the client.

        If the request was referred by the proxy itself (e.g. this is an image fetch for
        a previously proxied HTML page), then the original Referer is passed."""

        r = self.get_source_rsp(domain, url, post_payload)
        logging.info("Got %s response from %s",r.status_code, url)
        headers = dict(r.headers)
        def generate():
            for chunk in r.iter_content(CHUNK_SIZE):
                yield chunk
        content = generate()
        return Response(content, headers = headers)


    def get_source_rsp(self,
                       domain,
                       partial_url,
                       post_payload):
        url = self.get_full_url(domain,partial_url)
        logging.info("Fetching %s", url)
        # Pass original Referer for subsequent resource requests
        headers= {"Referer" : url}
        for h in ALLOWED_HEADERS:
            if h in request.headers:
                headers[h]=request.headers.get(h)
        # Fetch the URL, and stream it back
        logging.info("Fetching with headers: %s, %s", url, headers)
        if post_payload is not None:
            return requests.post(url,
                                stream=True ,
                                data = post_payload,
                                headers=headers)
        else:
            return requests.get(url,
                                stream=True ,
                                # params = request.args,
                                headers=headers)

    def get_full_url(self, domain, url):
        if domain in self.allowed_targets:
            return self.allowed_targets[domain]+url
        else:
            logging.warn("domain is not allowed: %s", domain)
            abort(403)
