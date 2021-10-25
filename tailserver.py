# -*- coding: utf-8 -*-
import os
import sys
import asyncio
import websockets
from concurrent.futures import ProcessPoolExecutor
from wsgiref.simple_server import make_server
from urllib.parse import parse_qs, unquote


html_template = b"""<!DOCTYPE html>
<html lang="zh">
  <head>
    <meta charset="utf-8">
    <title>TailServer</title>
    <style>
      body {background: black; color: white}
      p{ margin: 0;}
      ul{padding: 0;}
      li{list-style:none; padding: 0; margin: 0;}
    </style>
  </head>
  <body>
    <ul id="logger"></ul>
    <script>
      const socket = new WebSocket('ws://localhost:8081/?log=%s');
      let log = document.getElementById('logger');
      socket.addEventListener('message', function (event) {
        let text = document.createTextNode(event.data);
        let li = document.createElement("li");
        li.appendChild(text);
        log.prepend(li);
      });		
    </script>
  </body>
</html>"""


async def tail(ws, path):
    log = parse_qs(path[2:]).get("log", [""])[0]
    if not log:
        return
    try:
        with open(log, "rt") as fp:
            seek = os.path.getsize(log)
            await ws.send(f"#tail -f {log}")
            while True:
                fp.seek(seek)
                line = fp.readline()
                where = fp.tell()
                if line and seek != where:
                    try:
                        await ws.send(line.strip())
                    except websockets.exceptions.ConnectionClosedOK:
                        pass
                else:
                    await asyncio.sleep(0.01)
                    continue
                seek = where
                
    except (FileNotFoundError, PermissionError) as error:
        await ws.send(f"{error}")
        

async def ws_server():
    ip, port = "0.0.0.0", 8081
    print(f"ws server running {ip}:{port}")
    async with websockets.serve(tail, ip, port):
        await asyncio.Future()


def wsgi_app(environ, start_response):
    d = parse_qs(environ["QUERY_STRING"])
    start_response("200 OK", [("Content-Type", "text/html")])
    if d:
        log = d.get("log", [""])[0].encode("utf-8")
        return [html_template % log]
    else:
        return []


def run_wsgi_server():
    ip, port = "0.0.0.0", 8082
    with make_server(ip, port, wsgi_app) as httpd:
        print(f"http server running on {ip}:{port}")
        httpd.serve_forever()
        
        
def run_ws_server():
    asyncio.run(ws_server())
    
    
async def serve():
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=2) as pool:
        loop.run_until_complete(asyncio.gather(
            loop.run_in_executor(pool, run_ws_server),
            loop.run_in_executor(pool, run_wsgi_server)))


if __name__ == "__main__":
    asyncio.run(serve())
