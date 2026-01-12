import aioboto3
from jinja2 import Template
from cachetools import TTLCache
from app.settings import get_settings
from botocore.exceptions import ClientError, BotoCoreError
from fastapi import HTTPException, status, UploadFile, File
import os
import uuid
from datetime import datetime
from typing import List, Optional
import asyncio


settings = get_settings()

TEMPLATE_CACHE: TTLCache[str, Template] = TTLCache(maxsize=100, ttl=2 * 24 * 60 * 60)

async def load_template_from_s3(template_name: str) -> Template:
    if template_name in TEMPLATE_CACHE:
        return TEMPLATE_CACHE[template_name]
    s3_key  = f"templates/{template_name}"
    session = aioboto3.Session()
    try:
        async with session.client('s3', region_name=settings.aws.aws_region_name) as s3:
            response = await s3.get_object(Bucket=settings.aws.aws_storage_bucket_name,Key=s3_key)
            body     = await response["Body"].read()
            content  = body.decode("utf-8")
            template = Template(content)
            TEMPLATE_CACHE[template_name] = template
            return template
    except (ClientError, BotoCoreError) as e:
        error_msg = (f"Error fetching template from S3 bucket '{settings.aws.aws_storage_bucket_name}' "f"with key '{s3_key}': {e}")
        raise FileNotFoundError(error_msg) from e

