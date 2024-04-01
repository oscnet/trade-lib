"""
取得 venus.io 上的借贷利率
"""
import requests

venus_api_url = "https://api.venus.io"
pool_path = '/markets/core-pool'


def get_apy(symbol='BNB'):
    """
    取得 venus 上的存款，借货利率
    :param symbol: 币种
    :return: 存款利率，借货利率
    """

    response = requests.get(venus_api_url + pool_path, params={'underlyingSymbol': symbol})
    if response.status_code == 200:
        data = response.json()
        result = data['result'][0]
        return result['supplyApy'], result['borrowApy']
    else:
        print("请求失败:", response.status_code)
        return None, None


if __name__ == '__main__':
    ret = get_apy('FDUSD')
    print(ret)
