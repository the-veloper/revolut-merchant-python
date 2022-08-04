import datetime
import dateutil.parser
from decimal import Decimal
import json
import sys

if sys.version_info < (3,):  # pragma: nocover
    _integer_types = (
        int,
        long,
    )
    _str_types = (str, bytes, unicode)
else:  # pragma: nocover
    _integer_types = (int,)
    _str_types = (str, bytes)


def _obj2id(obj):
    return obj.id if hasattr(obj, "id") else obj


def _date(v):
    if not isinstance(v, (datetime.date, datetime.datetime)):
        return dateutil.parser.parse(v).date()
    elif isinstance(v, datetime.datetime):
        return v.date()
    return v


class _SetEnv(object):
    def _set_env(self, env):
        if env == "production":
            self.base_url = "https://merchant.revolut.com/api/1.0/"
            self.live = True
        elif env == "sandbox":
            self.base_url = "https://sandbox-merchant.revolut.com/api/1.0/"
            self.live = False
        else:
            raise ValueError(
                "Environment '{:s}' matches neither production nor sandbox environment.".format(
                    env
                )
            )


class JSONWithDecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(JSONWithDecimalEncoder, self).default(o)
