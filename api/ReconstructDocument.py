# -*- coding: utf-8 -*-
from tencentcloud.lke.v20231130 import lke_client, models
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common import credential
import json
from dotenv import load_dotenv
from typing import TypedDict, NotRequired
import os

REGION = "ap-guangzhou"

load_dotenv()

assert (
    TENCENT_SECRET_ID := os.getenv("TENCENT_SECRET_ID")
), "TENCENT_SECRET_ID is not set"
assert (
    TENCENT_SECRET_KEY := os.getenv("TENCENT_SECRET_KEY")
), "TENCENT_SECRET_KEY is not set"


class ReconstructDocumentConfig(TypedDict):
    enableInsetImage: NotRequired[bool]


class ReconstructDocumentResponse(TypedDict):
    markdownBase64: str | None
    insetImagePackage: str | None
    documentRecognizeInfo: str | None
    requestId: str


def reconstructDocument(
    region: str = REGION,
    *,
    fileBase64: str | None = None,
    fileUrl: str | None = None,
    fileStartPageNumber: int | None = None,
    fileEndPageNumber: int | None = None,
    config: ReconstructDocumentConfig | None = None,
) -> ReconstructDocumentResponse:
    assert fileBase64 or fileUrl, "FileBase64和FileUrl至少传入一个"
    # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
    # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性
    # 以下代码示例仅供参考，建议采用更安全的方式来使用密钥
    # 请参见：https://cloud.tencent.com/document/product/1278/85305
    # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
    cred = credential.Credential(TENCENT_SECRET_ID, TENCENT_SECRET_KEY)
    # 实例化一个http选项，可选的，没有特殊需求可以跳过
    httpProfile = HttpProfile()
    httpProfile.endpoint = "lke.tencentcloudapi.com"

    # 实例化一个client选项，可选的，没有特殊需求可以跳过
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    # 实例化要请求产品的client对象,clientProfile是可选的
    client = lke_client.LkeClient(cred, region, clientProfile)

    # 实例化一个请求对象,每个接口都会对应一个request对象
    req = models.ReconstructDocumentRequest()
    params = {}
    if fileBase64:
        params["FileBase64"] = fileBase64
    if fileUrl:
        params["FileUrl"] = fileUrl
    if fileStartPageNumber:
        params["FileStartPageNumber"] = fileStartPageNumber
    if fileEndPageNumber:
        params["FileEndPageNumber"] = fileEndPageNumber
    if config:
        params["Config"] = config
    req.from_json_string(json.dumps(params))

    # 返回的resp是一个ReconstructDocumentResponse的实例，与请求对象对应
    resp = client.ReconstructDocument(req)

    return {
        "markdownBase64": str(resp.MarkdownBase64) if resp.MarkdownBase64 else None,
        "insetImagePackage": str(resp.InsetImagePackage) if resp.InsetImagePackage else None,
        "documentRecognizeInfo": str(resp.DocumentRecognizeInfo) if resp.DocumentRecognizeInfo else None,
        "requestId": str(resp.RequestId),
    }
