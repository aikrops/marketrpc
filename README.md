# init

```shell
/usr/bin/python3.8 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. market_history.proto
```

# build

```shell
pip install --upgrade setuptools
python setup.py sdist bdist_wheel
pip install ./dist/marketrpc-0.0.1-py3-none-any.whl
```
