# Python Revolut Merchant API Client

DISCLAIMER:
**This client is a WIP and still in a very beta stage. Please use at your own risk!**

## Installation

```
pip install revolut-merchant-python
```

## Initialize the Client

To initialize the client install and import the library.

```python
import revolut_merchant

client = revolut_merchant.Client(access_token="<YOUR_TOKEN>", environment="<production/sandbox>")
```

## Fetch Order by ID

```python
order_id = "e5aa96ca-7ba1-4b5a-gj5a-03273877f3dc"
client.get_order(order_id) # This will return an Order object
```