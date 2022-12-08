from pydantic import BaseModel


class SensorSettings(BaseModel):
    hv: int
    w1_low: int
    w1_high: int
    w2_low: int
    w2_high: int
    w3_low: int
    w3_high: int


class DeltaSensorSettings(BaseModel):
    hv: int | None = None
    w1_low: int | None = None
    w1_high: int | None = None
    w2_low: int | None = None
    w2_high: int | None = None
    w3_low: int | None = None
    w3_high: int | None = None


class DetectorSettings(BaseModel):
    s1: SensorSettings
    s2: SensorSettings


class DeltaDetectorSettings(BaseModel):
    hv: int | None = None
    s1: DeltaSensorSettings | None = None
    s2: DeltaSensorSettings | None = None


class DeltaNodeSettings(BaseModel):
    d1: DeltaDetectorSettings | None = None
    d2: DeltaDetectorSettings | None = None
    d3: DeltaDetectorSettings | None = None
    d4: DeltaDetectorSettings | None = None
