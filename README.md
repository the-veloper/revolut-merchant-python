# Python Revolut Merchant API Client

DISCLAIMER:
**This client is a WIP and still in a very beta stage. Please use at your own risk!**

## Installation

```
pip install revolut-merchant-python
```

## Initialize the Client

To initialize the client install and import the library.

```
import revolut_merchant

client = revolut_merchant.Client(access_token="<YOUR_TOKEN>", environment="<production/sandbox>")
```

## Fetch Order by ID

```
order_id = "e5aa96ca-7ba1-4b5a-gj5a-03273877f3dc"
client.get_order(order_id) # This will return an Order object
```

## Create an order
```
order = revolut_merchant.Order(client=client, amount=1, currency="EUR", email="email@domain.com").save()
print(order.public_id) # prints the public order id
```