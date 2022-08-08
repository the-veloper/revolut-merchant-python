from __future__ import unicode_literals

from decimal import Decimal
import json
import logging
import requests

from .exceptions import InvalidAmountError, InvalidOrderStateError

try:  # pragma: nocover
    from urllib.parse import urljoin, urlencode  # 3.x
except ImportError:  # pragma: nocover
    from urlparse import urljoin  # 2.x
    from urllib import urlencode
from . import exceptions, utils

__version__ = "0.0.3"

_log = logging.getLogger(__name__)


class Client(utils._SetEnv):
    live = False
    timeout = 10
    _requester = None  # requests.Session()
    _customers = None
    _orders = None

    def __init__(self, access_token, environment, timeout=None):
        self._orders = {}
        self._set_env(environment)
        self.timeout = timeout
        self._requester = requests.Session()
        self._requester.headers.update(
            {"Authorization": "Bearer {}".format(access_token)}
        )
        self._customers = {}

    def _request(self, func, path, data=None):
        url = urljoin(self.base_url, path)
        _log.debug("{}".format(path))
        if data is not None:
            _log.debug(
                "data: {}".format(
                    json.dumps(
                        data, cls=utils.JSONWithDecimalEncoder, indent=2, sort_keys=True
                    )
                )
            )
        rsp = func(url, data=json.dumps(data) if data else None, timeout=self.timeout)
        if rsp.status_code == 204:
            result = None
        else:
            result = rsp.json(parse_float=Decimal)
        if rsp.status_code < 200 or rsp.status_code >= 300:
            error_id = result.get("errorId")
            raise exceptions.raise_error(rsp.status_code, error_id)
        if result:
            _ppresult = json.dumps(
                result, cls=utils.JSONWithDecimalEncoder, indent=2, sort_keys=True
            )
            _log.debug("Result:\n{result}".format(result=_ppresult))
        return result

    def _get(self, path, data=None):
        path = "{}?{}".format(path, urlencode(data)) if data is not None else path
        return self._request(self._requester.get, path)

    def _post(self, path, data=None):
        return self._request(self._requester.post, path, data or {})

    def _patch(self, path, data=None):
        return self._request(self._requester.patch, path, data or {})

    def _delete(self, path, data=None):
        return self._request(self._requester.delete, path, data or {})

    @property
    def customers(self):
        if self._customers:
            return self._customers
        _customers = {}
        data = self._get("customers")
        for customer_data in data:
            customer = Customer(client=self, **customer_data)
            _customers[customer.id] = customer
        self._customers = _customers
        return self._customers

    def get_customer(self, cid):
        if self._customers and cid in self._customers:
            return self._customers[cid]

        return Customer(client=self, **self._get(path="customers/{}".format(cid)))

    def get_orders(
        self,
        created_before=None,
        from_created_date=None,
        to_created_date=None,
        email=None,
        merchant_order_ext_ref=None,
        limit=100,
    ):
        if self._orders:
            return self._orders
        _orders = {}
        data = self._get("orders")
        for order_data in data:
            order = Order(client=self, **order_data)
            _orders[order.id] = order
        self._orders = _orders
        return self._orders

    def get_order(self, oid):
        if self._orders and oid in self._orders:
            return self._orders[oid]

        return Order(client=self, **self._get(path="orders/{}".format(oid)))


class _UpdateFromKwargsMixin(object):
    def _update(self, **kwargs):
        for k, v in kwargs.items():
            if not hasattr(self, k):
                raise ValueError(
                    "Excess keyword for {}: {} = {}".format(type(self), k, v)
                )
            setattr(self, k, v)


class Customer(_UpdateFromKwargsMixin):
    client = None
    id = None
    full_name = None
    created_at = None
    updated_at = None
    business_name = None
    email = None
    phone = None
    payment_methods = None

    def __init__(self, **kwargs):
        self.client = kwargs.pop("client")
        self._update(**kwargs)

    @property
    def is_business(self):
        return self.business_name is not None

    def __repr__(self):
        return "<Customer {} {}>".format(self.id, self.full_name)

    def refresh(self):
        data = self.client._get("customers/{}".format(self.id))
        self._update(**data)
        return self

    def save(self):
        keyset = ["full_name", "business_name", "email", "phone"]
        data = {k: getattr(self, k) for k in keyset if getattr(self, k) is not None}

        if self.id:
            self.client._patch("customers/{}".format(self.id), data)
            return self.refresh()

        data = self.client._post("customers", data)
        self.id = data["id"]
        self.client._customers[self.id] = self
        customer = Customer(client=self.client, id=self.id)
        return customer.refresh()

    def delete(self):
        if not self.id:
            raise ValueError("Customer not loaded from API.")

        self.client._delete("customers/{}".format(self.id))


class Order(_UpdateFromKwargsMixin):
    client = None
    id = None
    type = None
    state = None
    created_at = None
    updated_at = None
    order_amount = None
    order_outstanding_amount = None
    completed_at = None
    settlement_currency = None
    currency = None
    amount = None
    email = None
    phone = None
    description = None
    capture_mode = None
    merchant_order_ext_ref = None
    customer_id = None
    refunded_amount = None
    shipping_address = None
    payments = None
    related = None
    public_id = None
    metadata = None

    def __init__(self, **kwargs):
        self.client = kwargs.pop("client")
        self._update(**kwargs)

    def __repr__(self):
        return "<Order {} State: {} >".format(self.id, self.state)

    def refresh(self):
        data = self.client._get("orders/{}".format(self.id))
        self._update(**data)
        return self

    def save(self):
        if self.id:
            # @TODO update order
            raise Exception("Update of order using .save() not supported yet.")
        data = self.client._post(
            "orders",
            {"amount": self.amount, "currency": self.currency, "email": self.email},
        )
        self._update(**data)
        return self

    def capture(self, amount):
        if amount >= self.order_amount.get("value"):
            raise InvalidAmountError(
                "Amount should be less than or equal to the originally captured amount"
            )
        data = self.client._post(
            "orders/{}/capture".format(self.id), data={"amount": amount}
        )
        self._update(**data)
        return self

    def cancel(self):
        data = self.client._post("orders/{}/cancel".format(self.id))
        self._update(**data)
        return self

    def refund(self, amount, description):
        if self.state != "COMPLETED":
            raise InvalidOrderStateError("Only a completed order can be refunded")
        refunded_amount = self.refunded_amount.get("value", 0)
        if amount + refunded_amount > self.order_amount:
            raise InvalidAmountError(
                "Total refunded amount for order {} can be up to {}".format(
                    self.id, self.order_amount
                )
            )
        data = self.client._post(
            "orders/{}/refund".format(self.id),
            data={"amount": amount, "description": description},
        )
        self._update(**data)
        return self

    def confirm(self, payment_method_id=None):
        if self.state != "PENDING":
            raise InvalidOrderStateError("Only a pending order can be confirmed")
        confirm_data = {}
        if payment_method_id:
            confirm_data["payment_method_id"] = payment_method_id
        data = self.client._post("orders/{}/confirm".format(self.id), data=confirm_data)
        self._update(**data)
        return self
