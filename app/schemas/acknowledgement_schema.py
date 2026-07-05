from pydantic import BaseModel


class AcknowledgementResult(BaseModel):
    ticket_id: int
    sent: bool
    already_sent: bool
