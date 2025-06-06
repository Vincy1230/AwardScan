from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
import os
from api_service import convert_to_markdown
from llm_service import extract_award_info
import tempfile

app = FastAPI(title="获奖信息提取服务", docs_url=None)

# 挂载本地 swagger ui 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
MAX_FILE_SIZE = 6 * 1024 * 1024  # 6MB in bytes


class FilePath(BaseModel):
    file_path: str


@app.post("/extract-award-info")
async def extract_info(file: UploadFile = File(...)):
    # 检查文件名
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    # 检查文件扩展名
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。支持的格式：{', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        # 读取上传的文件内容
        content = await file.read()

        # 检查文件大小
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制。最大允许大小：6MB"
            )

        # 写入临时文件
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        # 转换为 Markdown
        markdown_text = convert_to_markdown(temp_file_path)
        if not markdown_text:
            raise HTTPException(status_code=500, detail="文件转换为 Markdown 失败")

        # 提取获奖信息
        award_info = extract_award_info(markdown_text)
        if not award_info:
            raise HTTPException(status_code=500, detail="提取获奖信息失败")

        return award_info

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理过程中发生错误：{str(e)}")
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="My API Docs",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    return get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )


if os.path.exists("./favicon.ico"):

    @app.get("/favicon.ico")
    async def get_favicon():
        return FileResponse("./favicon.ico")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8114)
