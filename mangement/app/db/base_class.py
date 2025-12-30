from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, func


# The common fields that needs to be used in all the model
class BaseColumn(object):
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(
        DateTime, server_default=func.now(), onupdate=func.current_timestamp()
    )



