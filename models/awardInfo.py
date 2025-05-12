from pydantic import BaseModel, Field


class AwardInfo(BaseModel):
    """获奖证书信息模型"""
    award_name: str = Field(description="获奖名称", default="")
    award_type: str = Field(description="奖项", default="")
    award_level: str = Field(description="获奖等级（国家级/省部级/校院级）", default="")
    winner: str = Field(description="获奖人", default="")
    advisor: str = Field(description="指导教师", default="")
    award_date: str = Field(description="获奖时间", default="")
    issuing_organization: str = Field(description="颁奖单位", default="")
