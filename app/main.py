import json
import math


async def read_body(receive):
    """
    Read and return the entire body from an incoming ASGI message.
    """
    body = b''
    more_body = True

    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)

    return body


async def send_response(send, status_code: int = 200, body=None):
    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': [
            [b'content-type', b'text/plain'],
        ],
    })
    if not body:
        body = dict()
    body = json.dumps(body).encode()
    await send({
        'type': 'http.response.body',
        'body': body,
    })


async def app(scope, receive, send):
    if scope['method'] != 'GET':
        await send_response(send, 404)
        return

    path: str = scope['path']

    if path.startswith('/factorial'):
        query_string = scope['query_string'].decode()
        items = query_string.split('=')
        if len(items) != 2:
            await send_response(send, 422)
        elif items[0] == 'n' and items[1]:
            try:
                num = int(items[1])
                if num < 0:
                    await send_response(send, 400)
                else:
                    result = math.factorial(num)
                    body = {"result": result}
                    await send_response(send, body=body)
            except ValueError:
                await send_response(send, 422)
        else:
            await send_response(send, 422)

    elif path.startswith('/fibonacci'):
        items = path.split('/')
        if len(items) != 3:
            await send_response(send, 422)
        else:
            param = items[-1]
            try:
                num = int(param)
                if num < 0:
                    await send_response(send, 400)
                else:
                    a, b = 0, 1
                    for _ in range(num):
                        a, b = b, a + b
                    body = {"result": b}
                    await send_response(send, body=body)
            except ValueError:
                await send_response(send, 422)

    elif path.startswith('/mean'):
        body = await read_body(receive)
        if not body:
            await send_response(send, 422)
            return
        # nums = eval(body.decode('utf-8'))
        nums = json.loads(body)
        if not nums:
            await send_response(send, 400)
        else:
            try:
                avg = sum(nums) / len(nums)
                body = {"result": avg}
                await send_response(send, body=body)
            except TypeError:
                await send_response(send, 422)
    else:
        await send_response(send, 404)
