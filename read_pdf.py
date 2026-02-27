from PyPDF2 import PdfReader

# 打开PDF文件
reader = PdfReader("实际情况分析.pdf")

# 获取PDF的页数
print(f"PDF页数: {len(reader.pages)}")

# 读取每一页的内容
for i, page in enumerate(reader.pages):
    print(f"\n=== 第 {i+1} 页 ===")
    text = page.extract_text()
    print(text)
