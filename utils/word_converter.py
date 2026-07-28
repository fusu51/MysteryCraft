"""Markdown → PDF 转换（WeasyPrint，跨平台）"""
import logging
from pathlib import Path

try:
    import markdown
except ImportError:
    markdown = None

try:
    from weasyprint import HTML
except ImportError:
    HTML = None


def convert_md_to_pdf(md_path: Path, pdf_path: Path) -> str:
    """
    将 Markdown 文件转为 PDF。
    依赖：markdown + weasyprint（已在 requirements.txt）
    """

    # 依赖检查
    if markdown is None:
        return "缺少依赖库，请安装: pip install markdown"
    if HTML is None:
        return "缺少依赖库，请安装: pip install weasyprint"

    # 源文件检查
    if not md_path.exists():
        return f"错误：源文件不存在 {md_path}"

    try:
        # 读取 Markdown
        md_text = md_path.read_text(encoding="utf-8")

        # Markdown → HTML
        html_body = markdown.markdown(
            md_text,
            extensions=["tables", "fenced_code", "codehilite"],
        )

        # 包装完整 HTML
        html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<style>
  body {{
    font-family: 'WenQuanYi Micro Hei', 'Microsoft YaHei', sans-serif;
    padding: 40px;
    font-size: 12pt;
    line-height: 1.8;
  }}
  h1 {{ font-size: 18pt; }}
  h2 {{ font-size: 15pt; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
  th, td {{ border: 1px solid #333; padding: 6px 10px; text-align: left; }}
  th {{ background-color: #f0f0f0; }}
  pre {{ background: #f4f4f4; padding: 12px; border-radius: 6px; overflow-x: auto; }}
  code {{ font-family: "Consolas", "Courier New", monospace; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

        # HTML → PDF
        HTML(string=html_doc).write_pdf(str(pdf_path))
        return f"PDF 已生成: {pdf_path.name}"

    except Exception as e:
        logging.error(f"PDF 转换失败: {e}", exc_info=True)
        return f"PDF 转换失败: {e}"
