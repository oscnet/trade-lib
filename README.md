# trade-lib
自己的交易常用库

```
pip install trade-lib
```

## 使用

```python

import trade_lib

# load exchange config from ~/.config/exchange.yaml
config = trade_lib.get_exchange_config(exname)

# set_dingding
dingding_config = {'robot_id':'', 'secret':''}
trade_lib.set_dingding(dingding_config)
trade_lib.dinding_send('ding...')
```

## upload to pypi

```
python3 setup.py sdist bdist_wheel

twine upload dist/*
```


## api

1、 取 venus.io 上的借贷利率
```python
from trade_lib.venus import get_apy

supply_apy, borrow_apy = get_apy('BNB')
print(supply_apy, borrow_apy)

```

