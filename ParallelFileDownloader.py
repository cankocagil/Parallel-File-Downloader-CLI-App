import numpy as np
import threading
import logging
import socket
import json
import time
import sys
import os
import re

class URLParser:
    def __init__(self, url):
        self.url = url
        self.parse()
        
    def parse(self):
        splitted_url = self.url.split('/')

        if splitted_url[0].startswith('http:'):
            splitted_url = splitted_url[2:]

        host_name = splitted_url[0]
        directory_name = "/".join(splitted_url[1:-1])
        file_name = splitted_url[-1]
        
        self.parsed_data = {
            'host': host_name,
            'directory_name' : '/' + directory_name,
            'file_name':file_name
        }

        for k, v in self.parsed_data.items():
            setattr(self, k, v)


class HTTPResponse:

    status_codes = {
        200: 'OK',
        404: 'Not Found',
        501: 'Not Implemented',
    }

    def __init__(self, data):
        self.response_line = None
        self.body = None
        self.blank_line = False
        self.header = None
        self.status = None
        self.parsed_data = {}
        self.status_code = None
        self.data = data

        self.parse(data)

    def parse(self, data):
        response_list = data.decode('utf-8').split('\r\n')

        if response_list[0].startswith('HTTP'):
            self.response_line = response_list[0]

            if '200' in self.response_line.split():
                self.status = 'HTTP/1.1 200 OK'
                self.status_code = 200

            elif '404' in self.response_line.split():
                self.status = 'HTTP/1.1 404 Not Found'
                self.status_code = 404
                
            else:
                self.status = 'HTTP/1.1 501 Not Implemented'
                self.status_code = 501

        header = []

        for data_line in response_list[1:-1]:
            if data_line == " ":
                self.blank_line = True
            else:
                header.append(data_line)

        self.header = "\n".join(header)
            
        self.body = response_list[-1]#.split()

        self.parsed_data['response_line'] = self.response_line
        self.parsed_data['status'] = self.status
        self.parsed_data['status_code'] = self.status_code
        self.parsed_data['header'] = self.header
        self.parsed_data['body'] = self.body

        return self


class HTTPResponseParser:
    def __init__(self, response):
        
        from http.client import HTTPResponse as HTTPParser
        from io import BytesIO


        class FakeSocket():
            def __init__(self, response_bytes):
                self._file = BytesIO(response_bytes)
            def makefile(self, *args, **kwargs):
                return self._file

        self.r = HTTPParser(
            FakeSocket(
                response
            )
        )

        self.r.begin()

        self.data = self.body = self.r.read().decode('utf-8')
        self.status_code = self.r.status

class HTTPClient:
    def __init__(
        self,
        url: URLParser,
        port = 80,
        verbose = 1,
    ):
        
        self.url = url
        self.verbose = verbose

        self.url_parsed = URLParser(url)
        self.port = port

        self.host = self.url_parsed.host
        self.filename = os.path.join(
            self.url_parsed.directory_name,
            self.url_parsed.file_name
        )

        self.data = []

    def head(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))

            get_message = f"HEAD {self.filename} HTTP/1.0\r\nHost: {self.host}\r\n\r\n"
            print(f"HTTP HEAD request is sending \n")

                
            s.sendall(
                get_message.encode('utf-8')
            )

            while 1:
                try:
                    buf = s.recv(2048)

                    self.data.append(buf)
                    
                except socket.error as e:
                    print(f"Error receiving data: {e}" )
                    
                    sys.exit(1)

                if not len(buf):
                    break
        
        response = HTTPResponseParser(
            b"".join([
                data for data in self.data if data != b''
            ])
        )

        return response

    def get(
        self, 
        bytes_to_read = 4096,
        lower_endpoint = 0,
        upper_endpoint = 1e30000,
        is_index_file = False,
    ):

        if is_index_file:
            print(f"URL of the index file: {self.url} \n")

        if lower_endpoint > upper_endpoint:
            print(f"Lower endpoint: {lower_endpoint} cannot be higher than upper endpoint: {upper_endpoint} ! \n")

        is_range_given = any(
            [
                lower_endpoint != 0,
                upper_endpoint != 1e30000,
            ]
        )

        if self.verbose:
            if not is_range_given:

                if is_index_file:
                    print(f"No range is given \n")
            
            else:

                if is_range_given:
                    if is_index_file:
                        print(f"[{lower_endpoint}:{upper_endpoint}]\n")
        
        if any(
            [
                lower_endpoint < 0,
                lower_endpoint < 0,
                lower_endpoint > 1e30000,
                upper_endpoint > 1e30000
            ]
        ):
            print(f"Lower Endpoint or Upper endpoint cannot be lower than 0 or higher than Python infinity! \n")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))

            if not is_range_given:
                get_message = f"GET {self.filename} HTTP/1.0\r\nHost: {self.host}\r\n\r\n"
                print(f"HTTP GET request is sending \n")
            
            else:
                get_message = f"GET {self.filename} HTTP/1.0\r\nHost: {self.host}\r\n\r\nUser-Agent:Mozilla 5.0\rRange: bytes={lower_endpoint}-{upper_endpoint}\n\n"
                print(f"HTTP Partial GET request is sending \n")
                
            s.sendall(
                get_message.encode('utf-8')
            )

            while 1:
                try:
                    buf = s.recv(bytes_to_read)


                    self.data.append(buf)
                    
                except socket.error as e:
                    print(f"Error receiving data: {e}\n" )
                    
                    sys.exit(1)

                if not len(buf):
                    break
        
        response = HTTPResponseParser(
                b"".join([
                    data for data in self.data if data != b''
                ])
        )

        succesfully_downloadad = len(response.body.split()) != 0

        if not is_index_file and succesfully_downloadad:
            
            if is_range_given:
                print(f"{self.url} (range = {lower_endpoint}-{upper_endpoint}) is downloaded\n")

            else:
                print(f"{self.url} (size = {sys.getsizeof(response.body)}) is downloaded\n")
                

        if not is_index_file and not succesfully_downloadad:
            print(f"{self.url} is not found\n")
            
        return response

def write_txt(file_name, body):
    
    current_dir = os.getcwd()
    write_dir = os.path.join(current_dir, file_name)

    with open(f"{write_dir}", 'a') as f:
        f.write(body)

    print(f"The file {file_name} is written under {write_dir}")

def header2dict(header):
    header_dict = {}
    
    for text in header:
        index = text.find(':')
        
        if index != -1:
            key = text[:index]
            value = text[index + 1:]
            header_dict[key] = value.strip()

    return header_dict


def get_size(url):
    client =  HTTPClient(
        url = url
    )
    
    response = client.get()

    """
    header = response.header.split('\n')

    dict_header = header2dict(header)
    content_len = dict_header['Content-Length']
    """

    content_len = response.r.getheader('Content-Length')
    size = int(content_len)
    return size
    
def download_range(url, start, end, is_index_file = False):
    client =  HTTPClient(
        url = url
    )
    response = client.get(
        is_index_file = is_index_file,
        lower_endpoint = start,
        upper_endpoint = end
    )

    parts[start] = response.body
    class_parts[start] = response

def get_chunks(number_of_bytes, number_of_threads) -> np.array:
    """ 
        Given the number of bytes and the number of threads, divides into chunks by satifying the condition
            * The number of bytes downloaded through each connection should differ by at most one byte
    """ 
    n, k = number_of_bytes, number_of_threads
    values = np.arange(n, dtype = int)
    bins, _ = np.histogram(values, bins = k)
    bins = - np.sort(- bins)

    return bins, bins.cumsum()


def download_parellel(url, number_of_threads: int = 5):
    threads = []
    
    global parts, class_parts

    parts, class_parts = {}, {}
    start_chunk = 0 

    number_of_bytes = get_size(url)

    chunk_sizes, chunk_intervals = get_chunks(
        number_of_bytes = number_of_bytes,
        number_of_threads = number_of_threads
    )

    for chunk_size, chunk_interval in zip(chunk_sizes, chunk_intervals):
        end_chunk = chunk_interval

        t = threading.Thread(
            target = download_range, 
            args = (url, start_chunk, end_chunk - 1)
        )
        t.start()
        threads.append(t)
        
        start_chunk = end_chunk

    start_chunk = 0 
    for chunk_size, chunk_interval in zip(chunk_sizes, chunk_intervals):
        end_chunk = chunk_interval
        print(f"File parts: [{start_chunk}/{end_chunk - 1}] ({chunk_size})")
        start_chunk = end_chunk

    for i in threads:
        i.join()

    return (
        ''.join([
                parts[i] for i in sorted(parts.keys())
            ]), 
        dict(
            sorted(class_parts.items())
        )
    )

def main(args):
    """ Main script for ParellelFileDownloader 
    
    test_urls = [
        "http://www.cs.bilkent.edu.tr/~cs421/fall21/project1/index1.txt", 
        "www.cs.bilkent.edu.tr/~cs421/fall21/project1/index2.txt"
    ]

    test_url = test_urls[1]

    """

    index_file = args.index_file

    if args.connection_count:
        number_of_threads = int(args.connection_count)
        print(f"{number_of_threads} number of parellel connections is establishing")
    else:
        number_of_threads = 3 
        print(f"No connection count specified, default {number_of_threads} number of parellel connections is establishing")

    
    assert all([
        isinstance(index_file, str), 
        isinstance(number_of_threads, int)
    ]), f"Index file should be a string and number of threads should be a number"

    client =  HTTPClient(
        url = index_file
    )

    response = client.get(
        is_index_file = True
    )

    print(f"Index file is downloaded\n")
    print(f"The are {len(response.body.split())} files in the index\n")

    responses = []
    
    urls = response.body.split()

    for url in urls:

        response_body, response = download_parellel(
            url, 
            number_of_threads
        )

        responses.append(
            {
                'response_body' : response_body,
                'response' : response, 
                'url' : url
            }

        )

        time.sleep(0.1)

    for response in responses:
        response_body = response['response_body']
        response_class = response['response']
        url = response['url']
        
        async_status_codes = [resp.status_code for resp in response_class.values()]
        
        if all([
            200 in async_status_codes,
            len(response_body) > 1
        ]):
            write_txt(
                url.split('/')[-1],
                response_body
            )


if __name__ == '__main__':
    assert len(sys.argv) != 1, f"Please provide index file, it is required!"

    index_file = sys.argv[1]

    if 1 <= len(sys.argv) <= 2:
        connection_count = None
    else:
        connection_count = sys.argv[2]

    class Args:
        def __init__(
            self, 
            index_file = None, 
            connection_count = 4
        ):
            assert index_file is not None, f"Index file must be provided"
            self.index_file = index_file
            self.connection_count = connection_count
        
    args =  Args(
        index_file = index_file,
        connection_count = connection_count
    )  
        
    main(args)

