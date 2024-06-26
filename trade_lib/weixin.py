#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import aiofiles
import aiohttp
import base64
import hashlib
import os
import yaml
import sys
import getopt

help_doc = """Usage: wwx-robot -k <robot_key> -t <msg_type> -d <msg_data> -f <msg_file_path>
Option:
    -k      Robot key
    -t      Message type
              text, markdown, image, news
    -d      Message data
    -f      Message file
              +--------------+--------------+
              | Message Type |  File Type   |
              +--------------+--------------+
              |     text     |     text     |
              +--------------+--------------+
              |   markdown   |   markdown   |
              +--------------+--------------+
              |     image    |    jpg,png   |
              +--------------+--------------+
              |     news     |     yaml     |
              +--------------+--------------+
Example:
    wwx-robot -k xxxx -t text -d "Hello world"
    wwx-robot -k xxxx -t markdown -f demo/help.md
    wwx-robot -k xxxx -t image -f demo/picture.jpg
    wwx-robot -k xxxx -t news -f demo/articles.yaml
"""


class WXRobot(object):
    def __init__(self, key: str, proxy=None):
        self.url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + key
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.proxy = proxy

    async def _send(self, body: dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=self.url, headers=self.headers, json=body, proxy=self.proxy) as resp:
                r = await resp.json()
                assert resp.status == 200
                assert r.get('errmsg') == 'ok'
                return True

    async def send_text(self, content: str):
        """
        文本类型
        :param content:
        :return:
        """
        body = {
            'msgtype': 'text',
            'text': {
                'content': content,
                # 'mentioned_list': ['@all'],  # Optional
                # 'mentioned_mobile_list': ['@all']  # Optional
            }
        }
        await self._send(body)

    async def send_markdown(self, content: str):
        """
        Markdown 类型
        :param content:
        :return:
        """
        body = {
            'msgtype': 'markdown',
            'markdown': {
                'content': content,
            }
        }
        await self._send(body)

    async def send_image(self, local_file=None, remote_url=None):
        """
        图片类型
        :param local_file: local file path
        :param remote_url: image url
        :return:
        """
        if local_file:
            async with aiofiles.open(local_file, mode='rb') as f:
                image_content = await f.read()
        elif remote_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(remote_url) as response:
                    image_content = await response.read()
        else:
            raise Exception('Need provide local_file: str or remote_url: str')
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        md5 = hashlib.md5()
        md5.update(image_content)
        image_md5 = md5.hexdigest()
        body = {
            'msgtype': 'image',
            'image': {
                'base64': image_base64,
                'md5': image_md5
            }
        }
        await self._send(body)

    async def send_news(self, articles: list):
        """
        图文类型
        :param articles: [
            {
                'title': '',
                'description': '',  # Optional
                'url': '',
                'picurl': '',  # Optional
            }
        ]
        :return:
        """
        assert len(articles) <= 8, 'Only support 1-8 articles'
        for article in articles:
            assert article.get('title'), 'Need provide article title'
            assert article.get('url'), 'Need provide article url'
        body = {
            'msgtype': 'news',
            'news': {
                'articles': articles
            }
        }
        await self._send(body)

    @staticmethod
    async def read_file(file_path):
        if os.path.exists(file_path):
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                return await f.read()
        else:
            return ""

    async def sender(self, msg_type: str = "text", msg_data=None, msg_file_path=None):
        if msg_type == "text":
            await self.send_text(msg_data or self.read_file(msg_file_path))
        elif msg_type == "markdown":
            await self.send_markdown(msg_data or self.read_file(msg_file_path))
        elif msg_type == "image":
            if os.path.exists(msg_file_path):
                await self.send_image(local_file=msg_file_path)
            else:
                await self.send_image(remote_url=msg_file_path)
        elif msg_type == "news":
            await self.send_news(yaml.full_load(self.read_file(msg_file_path)))


async def main():
    if len(sys.argv[1:]) == 0:
        print(help_doc)
        exit(1)
    try:
        _args = dict()
        for opt, arg in getopt.getopt(sys.argv[1:], "k:t:d:f:")[0]:
            if opt == '-k':
                _args['key'] = arg
            elif opt == '-t':
                _args['type'] = arg
            elif opt == '-d':
                _args['data'] = arg
            elif opt == '-f':
                _args['file'] = arg
        if not _args.get('key') or not _args.get('type'):
            print('Robot key and message type is required')
            print(help_doc)
            exit(1)
        if not _args.get('data') and not _args.get('file'):
            print('Message data or message file is required')
            print(help_doc)
            exit(1)
        print('Welcome to use Work WeiXin Robot tool')
        rbt = WXRobot(key=_args.get('key'))
        print('Try to send == %s == type message' % _args.get('type').upper())
        if _args.get('data'):
            print('Message Content:\n%s' % _args.get('data'))
        else:
            if _args.get('type') == 'image':
                print('Message Content: \n%s' % _args.get('file'))
            else:
                with open(_args.get('file'), 'r', encoding='utf-8') as f:
                    print('Message Content:\n%s' % f.read())
        await rbt.sender(msg_type=_args.get('type'), msg_data=_args.get('data'), msg_file_path=_args.get('file'))
    except getopt.GetoptError:
        print(help_doc)
        exit(1)
    print('Complete to send message')


if __name__ == '__main__':
    print('This is the scripts of Work Weixin Robot sender')
    asyncio.run(main())
