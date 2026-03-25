from pydantic import Field

from solei.customer_meter.schemas import CustomerMeterBase
from solei.kit.schemas import IDSchema, TimestampedSchema
from solei.meter.schemas import NAME_DESCRIPTION as METER_NAME_DESCRIPTION


class CustomerCustomerMeterMeter(IDSchema, TimestampedSchema):
    name: str = Field(description=METER_NAME_DESCRIPTION)


class CustomerCustomerMeter(CustomerMeterBase):
    meter: CustomerCustomerMeterMeter
