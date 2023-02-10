#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, and Tommy Sandanasamy
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
    def __str__(self):
        return "{}\n{}\n".format(self.code, self.body)

class HTTPClient(object):
    #def get_host_port(self,url):

    def parse_url_and_connect(self, url):
        if not url.startswith("http://"):
            url = "http://" + url
        self.parsed_url = urllib.parse.urlparse(url, scheme='http')

        port = 80
        if ( self.parsed_url.port != None ):
            port = self.parsed_url.port
        try:
            self.connect(self.parsed_url.hostname, port)
        except:
            try:
                port = 8080
                self.connect(self.parsed_url.hostname, port)
            except:
                return HTTPResponse(-1, "Cannot connect to {}".format(url))
        return None

    def connect(self, host, port):
        address = socket.gethostbyname(host)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, port))
        return None

    def get_code(self, data):
        #get status code
        line = data.split("\n")[0]
        status_line = line.split(" ")
        if(len(status_line) >= 3 and status_line[1].isnumeric()):
            return int(status_line[1])
        else:
            return -1

    def get_headers(self,data):
        #get headers
        headers = dict()
        for line in data.split("\n")[1:]:
            if(line == "\r"):
                break
            try:
                header, value = line.split(":", 1)
                headers[header] = value
            except:
                headers["CLIENT-ERROR-OCCURED"] = "True"
                break
        return headers

    def get_body(self, data):
        lines = data.split("\n")[1:]
        body = ""
        for i in range(len(lines)):
            if(lines[i] == "\r"):
                body = "\n".join(lines[i:]).strip()
                break
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if not part:
                break
            buffer.extend(part)
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        conn_response = self.parse_url_and_connect(url)
        if(conn_response == -1):
            return conn_response

        path = self.parsed_url.path
        if not path:
            path = "/"

        query_string = ""
        if args:
            urllib.parse.urlencode(args)
            
        request = "GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(path + query_string, self.parsed_url.netloc)

        self.sendall(request)
        data = self.recvall(self.socket).strip()
        self.close()
        
        #Parse response data
        code = self.get_code(data)
        headers = self.get_headers(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        conn_response = self.parse_url_and_connect(url)
        if(conn_response == -1):
            return conn_response

        query_string = ""
        if args:
            query_string = urllib.parse.urlencode(args)

        path = self.parsed_url.path
        if not path:
            path = "/"

        request = "POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\n{}".format(path, self.parsed_url.netloc, len(query_string), query_string)
        
        self.sendall(request)
        data = self.recvall(self.socket).strip()
        self.close()

        #Parse response data
        code = self.get_code(data)
        headers = self.get_headers(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):

        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
