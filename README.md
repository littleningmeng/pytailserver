# pytailserver
A tail server demo using websockets and implemented by python  

```bash
pip install websockets  
python tailserver.py  
```

If you run tailserver on remote server, do not forget to change then ip in  
```js
const socket = new WebSocket('ws://localhost:8081/?log=%s');
```
