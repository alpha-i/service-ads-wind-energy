import json

import pandas as pd
from datetime import datetime, date, timedelta
from enum import Enum

import enum
import numpy
from flask.json import JSONEncoder
from sqlalchemy.ext.declarative import DeclarativeMeta


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            return obj.to_dict()
        if issubclass(obj.__class__, Enum):
            return obj.name
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S%z')
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        if isinstance(obj, (numpy.float32, numpy.int64, numpy.ndarray)):
            return obj.tolist()
        if isinstance(obj, (timedelta, pd.Timedelta)):
            return str(obj)

        if isinstance(obj, enum.EnumMeta):
            return {member.name: member.value for member in obj}

        return super(CustomJSONEncoder, self).default(obj)
