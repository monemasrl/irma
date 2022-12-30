from pydantic import BaseModel


class SensorSettings(BaseModel):
    hv: int | None = None
    w1_low: int | None = None
    w1_high: int | None = None
    w2_low: int | None = None
    w2_high: int | None = None
    w3_low: int | None = None
    w3_high: int | None = None


class DetectorSettings(BaseModel):
    s1: SensorSettings | None
    s2: SensorSettings | None
