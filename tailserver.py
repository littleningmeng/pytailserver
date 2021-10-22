# -*- coding: utf-8 -*-
import os
import asyncio
import websockets



async def tail(websocket, path):
    with open("access.log", 'rt') as fp:
        seek = os.path.getsize("access.log")
        while 1:
            fp.seek(seek)
            line = fp.readline()
            where = fp.tell()
            if line and seek != where:
                try:
                    await websocket.send(line.strip())
                except websockets.exceptions.ConnectionClosedOK:
                    pass
            else:
                await asyncio.sleep(0.01)
                continue

            seek = where


async def main():
    ip, port = "0.0.0.0", 8081
    print(f"running on {ip}:{port}")
    async with websockets.serve(tail, ip, port):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
