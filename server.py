import argparse
import asyncio
import socket
from contextlib import closing

import httptools
import uvloop
from aiohttp import web

KB = b'0' * 1024
RESP = {size: KB * size for size in [1, 10, 100]}


def aiohttp_server(loop, addr):
    async def handler(request):
        size = int(request.match_info.get('size', '1'))
        return web.Response(body=RESP.get(size, KB))

    app = web.Application()
    app.router.add_route('GET', '/{size}', handler)
    app.router.add_route('GET', '/', handler)

    handler = app.make_handler()
    server = loop.create_server(handler, *addr)

    return server


class HttpRequest:
    __slots__ = ('_protocol', '_url', '_headers', '_version')

    def __init__(self, protocol, url, headers, version):
        self._protocol = protocol
        self._url = url
        self._headers = headers
        self._version = version


class HttpResponse:
    __slots__ = ('_protocol', '_request', '_headers_sent')

    def __init__(self, protocol, request):
        self._protocol = protocol
        self._request = request
        self._headers_sent = False

    def write(self, data):
        self._protocol._transport.write(b''.join([
            f'HTTP/{self._request._version} 200 OK\r\n'.encode('latin-1'),
            b'Content-Type: octet/plain\r\n',
            f'Content-Length: {len(data)}\r\n'.encode('latin-1'),
            b'\r\n',
            data
        ]))


class HttptoolsProtocol(asyncio.Protocol):
    __slots__ = ('_loop', '_transport', '_headers', '_parser',
                 '_request', '_url', )

    def __init__(self, *, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()

        self._loop = loop
        self._transport = None
        self._headers = None
        self._parser = None
        self._request = None
        self._url = None

    def on_header(self, name, value):
        self._headers.append((name, value))

    def on_headers_complete(self):
        self._request = HttpRequest(
            self, self._url, self._headers,
            self._parser.get_http_version())

        self._loop.call_soon(
            self.handle, self._request,
            HttpResponse(self, self._request))

    def on_url(self, url):
        self._url = url

    def connection_made(self, transport):
        self._transport = transport
        sock = transport.get_extra_info('socket')
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except (OSError, NameError):
            pass

    def connection_lost(self, exc):
        self._request = None
        self._parser = None

    def data_received(self, data):
        if self._parser is None:
            self._headers = []
            self._parser = httptools.HttpRequestParser(self)

        self._parser.feed_data(data)

    def handle(self, request, response):
        url = httptools.parse_url(self._url)
        size = int(url.path.decode('ascii')[1:] or '1')
        resp = RESP.get(size, KB)
        response.write(resp)
        if not self._parser.should_keep_alive():
            self._transport.close()
        self._parser = None
        self._request = None


def httptools_server(loop, addr):
    return loop.create_server(lambda: HttptoolsProtocol(loop=loop), *addr)


def _main():
    def _parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--server', choices=['aiohttp', 'httptools'], default='aiohttp')
        parser.add_argument('-l', '--loop', choices=['asyncio', 'uvloop'], default='asyncio')
        parser.add_argument('-d', '--debug', action='store_true')
        return parser.parse_args()

    args = _parse_args()

    if args.server == 'aiohttp':
        server_factory = aiohttp_server
    elif args.server == 'httptools':
        server_factory = httptools_server

    if args.loop == 'uvloop':
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    loop = asyncio.get_event_loop()
    loop.set_debug(args.debug)

    addr = ('127.0.0.1', '8080')
    server = loop.run_until_complete(server_factory(loop, addr))

    with closing(loop) as loop, closing(server) as server:
        print(f'Serving at http://{":".join(addr)}'
              f' ({args.server} + {args.loop})'
              )
        loop.run_forever()


if __name__ == '__main__':
    _main()
