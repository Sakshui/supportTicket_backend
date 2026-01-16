import re
import sys
import aioboto3
import orjson
import logging
import traceback
import uuid
import httpx
from typing import Dict, Optional, Union
from fastapi import Body, Request
from botocore.config import Config
from jinja2 import Template
from fastapi import Request,UploadFile
from urllib.parse import urlparse
from pydantic import  HttpUrl
from fastapi.responses import Response
from datetime import datetime, timezone
from botocore.exceptions import ClientError, BotoCoreError
from typing import Optional, Any, Union ,Generic ,TypeVar, Dict

from app.settings import get_settings
from app.template_loader import load_template_from_s3

settings = get_settings()

#------------------------------------------------------------ GLOBLE PROJECT TIME ----------------------------------------------------
def utcnow() -> datetime:
    return datetime.now(timezone.utc)

#------------------------------------------------------------ API RESPONSE CLASS ------------------------------------------------------
T = TypeVar("T")

class ApiResponse(Response, Generic[T]):
    media_type = "application/json"
    def render(self, content: any) -> bytes:
        return orjson.dumps(content)

#------------------------------------------------------------ REQUEST DATA PARSER ------------------------------------------------------ 


async def get_request_data(content_type, request):
    content_type = (content_type or "").lower().strip()

   
    if request.method in ["GET"]:
        data = dict(request.query_params)
        data.pop("time", None)

        if "id" in data:
            try:
                data["id"] = int(data["id"])
            except ValueError:
                raise ValueError("Query param 'id' must be an integer")

        return data

 

   
    if "application/json" in content_type or "application/x-www-form-urlencoded" in content_type:
        body = await request.body()
        return orjson.loads(body) if body else {}
    

    if "multipart/form-data" in content_type:
        form = await request.form()
        data = {}

        for k in form.keys():
            values = form.getlist(k)
            processed = []

            for v in values:
                if isinstance(v, UploadFile):
                    processed.append(v)
                elif isinstance(v, str):
                    v = v.strip()
                    try:
                        if v.startswith(("{", "[")):
                            processed.append(orjson.loads(v))
                        else:
                            processed.append(v)
                    except orjson.JSONDecodeError:
                        processed.append(v)
                else:
                    processed.append(v)

           
            if all(isinstance(x, UploadFile) for x in processed):
                data[k] = processed
            else:
                data[k] = processed if len(processed) > 1 else processed[0]

        return data
    
    raise ValueError(f"Unsupported Content-Type: {content_type}")


  
#------------------------------------------------------------- EXEPTION HANDLER ---------------------------------------------------------
async def exception_handler(e: Exception, request: Optional[Request] = None, data: Optional[Union[dict, str]] = None) -> str:
    tb_str     = traceback.format_exception(type(e), e, e.__traceback__)
    tb_message = ''.join(tb_str)
    if request:
        try:
            if request.method == "POST":
                request_data = await request.json()
            else:
                request_data = dict(request.query_params)
        except Exception as ex:
            request_data = f"<failed to extract request data: {ex}>"
    else:
        request_data = data or "<no request object>"
    print("========================================================================================")
    if request:
        print("🚨 Source:\n", f"[{request.method}] {str(request.url)}")
    else:
        print("🚨 Source:\n No request object (manual/async call)")
    print("📦 Request data:\n", request_data)
    print("💥 An error occurred:\n", tb_message, file=sys.stderr)
    print("================================== SUPPORT_TICKET_SYSTEM ERROR =======================================")
    return tb_message

# ====================================================================================================================================


def _get_s3(aws_key, aws_secret, aws_region):
    return aioboto3.Session().client(
        "s3",
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret,
        config=Config(
            region_name=aws_region,
            retries={"max_attempts": 3, "mode": "adaptive"},
            connect_timeout=5,
            read_timeout=20,
        ),
    )


async def media_to_aws_s3(*, key: str | None = None, file: UploadFile | None = None, file_data: bytes | None = None, file_type: str | None = None, media_link: HttpUrl | None = None, delete: bool = False,) -> str | dict[str, Any]:
    settings = get_settings()
    if not key:
        key = f"media_gallery/{uuid.uuid4().hex}.{file_type}"
    bucket_name = settings.aws.aws_storage_bucket_name
    aws_region = settings.aws.aws_region_name
    aws_key = settings.aws.aws_access_key_id
    aws_secret = settings.aws.aws_secret_access_key
    async with _get_s3(aws_key, aws_secret, aws_region) as s3:
        if delete:
            await s3.delete_object(Bucket=bucket_name, Key=key)
            return {"status": "deleted", "key": key, "detail": "Object removed"}

        if file is not None:
            content_type = file.content_type or "application/octet-stream"
            await s3.upload_fileobj(file.file, bucket_name, key, ExtraArgs={"ContentType": content_type},)
            url = f"https://s3.{aws_region}.amazonaws.com/{bucket_name}/{key}"
            return url
        if file_data is not None:
            content_type = file_type or "application/octet-stream"
            await s3.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=file_data,
                ContentType=content_type,
            )
            url = f"https://s3.{aws_region}.amazonaws.com/{bucket_name}/{key}"
            return url

        if media_link is not None:
            async with httpx.AsyncClient(timeout=30) as client:
                head = await client.head(str(media_link))
                head.raise_for_status()
                content_type = head.headers.get("content-type", "binary/octet-stream")

                async with client.stream("GET", str(media_link)) as resp:
                    resp.raise_for_status()
                    await s3.upload_fileobj(
                        resp.aiter_bytes(),
                        bucket_name,
                        key,
                        ExtraArgs={"ContentType": content_type},
                    )
            url = f"https://s3.{aws_region}.amazonaws.com/{bucket_name}/{key}"
            return url
        raise ValueError("No file, file_data, or media_link provided, and delete=False")

