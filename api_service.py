from api.ReconstructDocument import reconstructDocument
import base64


def convert_to_markdown(file_path: str) -> str | None:
    file_base64 = file_to_base64(file_path)
    markdown_base64 = reconstructDocument(
        fileBase64=file_base64
    )["markdownBase64"]
    return base64_to_string(markdown_base64) if markdown_base64 else None


def file_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def base64_to_string(base64_str: str) -> str:
    return base64.b64decode(base64_str).decode("utf-8")
