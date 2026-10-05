import hashlib
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from tools.rag_tools import vector_store

# 扫描目录（项目根目录）与支持的文件类型
DOC_DIR = Path(__file__).resolve().parent.parent
SUPPORTED_SUFFIX = {".txt", ".pdf"}
# 排除的非知识文档（项目配置/依赖文件等）
EXCLUDE_FILES = {"requirements.txt"}


def compute_file_md5(path: Path) -> str:
    """计算文件的 MD5 值，用于去重"""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_text(path: Path) -> str:
    """加载 txt 文本"""
    return path.read_text(encoding="utf-8")


def load_pdf(path: Path) -> str:
    """加载 pdf 文本"""
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def already_ingested(md5: str) -> bool:
    """检查该 md5 是否已在向量库中"""
    result = vector_store._collection.get(where={"md5": md5})
    return len(result["ids"]) > 0


def ingest_file(path: Path) -> int:
    """切分并入库单个文件，返回写入的 chunk 数；已存在则返回 0"""
    md5 = compute_file_md5(path)
    if already_ingested(md5):
        print(f"[跳过] {path.name} 已存在（md5={md5}）")
        return 0

    suffix = path.suffix.lower()
    if suffix == ".txt":
        text = load_text(path)
    elif suffix == ".pdf":
        text = load_pdf(path)
    else:
        return 0

    if not text.strip():
        print(f"[跳过] {path.name} 内容为空")
        return 0

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)

    metadatas = [{"source": path.name, "md5": md5} for _ in chunks]
    vector_store.add_texts(texts=chunks, metadatas=metadatas)
    print(f"[入库] {path.name} → {len(chunks)} 块（md5={md5}）")
    return len(chunks)


def main():
    files = sorted(
        p for p in DOC_DIR.iterdir()
        if p.is_file()
        and p.suffix.lower() in SUPPORTED_SUFFIX
        and p.name not in EXCLUDE_FILES
    )
    if not files:
        print("未找到 txt/pdf 文档")
        return

    total = 0
    for f in files:
        total += ingest_file(f)
    print(f"\n本次共写入 {total} 块")


if __name__ == "__main__":
    main()
