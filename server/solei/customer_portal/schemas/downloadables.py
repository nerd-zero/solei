from datetime import datetime

from pydantic import UUID4

from solei.benefit.schemas import BenefitID
from solei.file.schemas import FileDownload
from solei.kit.schemas import Schema
from solei.models.downloadable import DownloadableStatus


class DownloadableURL(Schema):
    url: str
    expires_at: datetime


class DownloadableRead(Schema):
    id: UUID4
    benefit_id: UUID4

    file: FileDownload


class DownloadableCreate(Schema):
    file_id: UUID4
    customer_id: UUID4
    benefit_id: BenefitID
    status: DownloadableStatus


class DownloadableUpdate(Schema):
    file_id: UUID4
    customer_id: UUID4
    benefit_id: BenefitID
    status: DownloadableStatus
