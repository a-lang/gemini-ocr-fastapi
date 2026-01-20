#!/usr/bin/python
# -*- coding: utf-8 -*-
from google import genai
from google.genai import types
import json
import pathlib
from pydantic import BaseModel, Field

# Structured output schema
# Define the schema for the structured output
# https://ai.google.dev/gemini-api/docs/structured-output
class BankTransaction(BaseModel):
    銀行: str = Field(description="銀行名稱")
    帳號: str = Field(description="銀行帳號")
    帳務日期: str = Field(description="帳務日期")
    摘要: str = Field(description="摘要")
    支出: str = Field(description="支出金額")
    存入: str = Field(description="存入/轉入金額")
    餘額: str = Field(description="餘額")
    備註: str = Field(description="備註")

class MatchResult(BaseModel):
    output: list[BankTransaction]

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

# Test the model
"""
response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)
"""

# Define the prompt
prompt = """
    ##角色定義 (Role Definition)
    你是一位/一個：嚴謹的金融數據分析師和 JSON 格式化專家。 你的首要目標是：從提供的銀行交易明細 PDF 內容中，精確提取單筆或多筆交易的關鍵數據，並將其轉換成指定的 JSON 結構陣列。

    ##核心任務與輸入 (Core Task & Input)
    1. 輸入資料：使用者提供的附檔 PDF 檔案內容。
    2. 具體行動：
     - 識別：確定銀行名稱、帳號、查詢期間和所有交易記錄行。
     - 提取：從交易記錄中，按列提取「帳務日期」、「摘要」、「支出金額」、「存入/轉入金額」、「即時餘額」和「附註」。
     - 轉換：將提取的數據映射到目標 JSON 結構。

    ##約束與規則 (Constraints & Rules)
     - 格式要求：輸出必須是一個完整的、有效的 JSON 陣列。
     - 數據映射：必須嚴格遵守以下 JSON 鍵名：銀行、帳號、帳務日期、摘要、支出、存入/轉入、餘額、備註。
     - 未提供/不適用：如果原始數據中某個欄位無值（如「支出金額」），則在 JSON 中對應的值為字串 ""。
     - 數據來源：只使用附檔中實際出現的數據進行填充。
     - 請勿摘要、改寫或推斷缺失文字。
     - 若文字模糊或部分不可見，請盡可能提取內容，切勿憑空揣測。

    ##輸出格式化 (Output Formatting)
     - 強制輸出格式：JSON 陣列。
     - 字串處理：所有字串值必須用雙引號包裹。
     - 日期格式：YYYY-MM-DD。
"""


def ocr_infer(model, file2path: str):
    # Load local PDF file, Retrieve and encode the PDF byte
    filepath = pathlib.Path(file2path)


    # Generate content using the specified model with a JSON schema for the response
    # The response will be in JSON format and validated against the MatchResult schema
    response = client.models.generate_content(
        model=model,
        config={"response_mime_type": "application/json",
                "response_json_schema": MatchResult.model_json_schema(),},
        contents=[
            types.Part.from_bytes(
                data=filepath.read_bytes(),
                mime_type='application/pdf',
            ),
            prompt])
    
    # Validate the response text against the MatchResult schema
    #return MatchResult.model_validate_json(response.text)

    # Return the parsed response as a dictionary
    #return response.parsed    # It's type Dict

    # Convert the parsed dictionary to a JSON string, ensuring Chinese characters are properly encoded
    #return json.dumps(response.parsed, ensure_ascii=False)
    
    # Extract and return the "output" field from the parsed response
    return response.parsed["output"]


if __name__ == "__main__":
    print( [ocr_infer("gemini-2.5-flash", "mma.pdf")] )
