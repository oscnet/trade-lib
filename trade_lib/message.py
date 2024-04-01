import base64
import hashlib
import hmac
import logging
import time
from enum import Enum
from urllib import parse
import json
import traceback
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)


class MessageMethod(Enum):
    """
    发送消息方式，目前只有钉钉，后续可能会有其他形式的消息
    """
    DINGDING = 'DINGDING'


# 钉钉
class Dingding:
    def __init__(self, robot_id, secret):
        """
        :param robot_id:  你的access_token，即webhook地址中那段access_token。
        :param secret: 你的secret，即安全设置加签当中的那个密钥
        """
        self.robot_id = robot_id
        self.secret = secret

    def cal_timestamp_sign(self):
        # 根据钉钉开发文档，修改推送消息的安全设置https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq
        # 也就是根据这个方法，不只是要有robot_id，还要有secret
        # 当前时间戳，单位是毫秒，与请求调用时间误差不能超过1小时
        # python3用int取整
        secret = self.secret
        timestamp = int(round(time.time() * 1000))
        # 密钥，机器人安全设置页面，加签一栏下面显示的SEC开头的字符串
        secret_enc = bytes(secret.encode('utf-8'))
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = bytes(string_to_sign.encode('utf-8'))
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        # 得到最终的签名值
        sign = parse.quote_plus(base64.b64encode(hmac_code))
        return str(timestamp), str(sign)

    # 发送钉钉消息
    async def send_dingding_msg(self, content):
        try:
            robot_id = self.robot_id
            msg = {
                "msgtype": "text",
                "text": {"content": content + '\n' + datetime.now().strftime("%m-%d %H:%M:%S")}}
            headers = {"Content-Type": "application/json;charset=utf-8"}
            # https://oapi.dingtalk.com/robot/send?access_token=XXXXXX&timestamp=XXX&sign=XXX
            timestamp, sign_str = self.cal_timestamp_sign()
            url = 'https://oapi.dingtalk.com/robot/send?access_token=' + robot_id + \
                  '&timestamp=' + timestamp + '&sign=' + sign_str
            body = json.dumps(msg)

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=body, headers=headers, timeout=10) as response:
                    r = await response.text()
            # requests.post(url, data=body, headers=headers, timeout=10)
            logger.debug(f'成功发送钉钉: {content}')
        except Exception as e:
            logger.warning("发送钉钉失败:", e)
            traceback.print_exc()


# 发送消息
class Message:
    def __init__(self, message_method=MessageMethod.DINGDING, init_config={}):
        self.type = message_method
        self.init_config = init_config

    # 发送消息
    async def send(self, content=''):
        if self.type == MessageMethod.DINGDING:
            ding = Dingding(robot_id=self.init_config['robot_id'], secret=self.init_config['secret'])
            return await ding.send_dingding_msg(content)


ding_ding = None
msg_head = None


def set_dingding(config, head=None):
    global ding_ding, msg_head
    ding_ding = Message(MessageMethod.DINGDING, config)
    msg_head = head


async def dinding_send(msg):
    global ding_ding, msg_head
    if ding_ding:
        await ding_ding.send(msg if msg_head is None else f"{msg_head}: {msg}")
    else:
        logger.warning("请先 set_dingding 进行初始化")


# 企业微信通知
# wechat_webhook_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0b0....'
async def send_msg_q_wechat(url, content, proxy=None):
    try:
        data = {
            "msgtype": "text",
            "text": {
                "content": content + '\n' + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(data), timeout=10,
                                    proxy=proxy) as response:
                print(f'调用企业微信接口返回： {await response.text()}')
                print('成功发送企业微信')
    except Exception as e:
        print(f"发送企业微信失败:{e}")
        print(traceback.format_exc())

# async def main():
#     message_instance = Message(MessageMethod.DINGDING, {
#         'robot_id': 'e02d79d08............1ed8dde74e4ee9d9d91a',
#         'secret': 'SEC4efd8.............1eca73afdd1eb8419'
#     })
#     await message_instance.send('哈哈哈')
#
# if __name__ == '__main__':
#     asyncio.run(main())
