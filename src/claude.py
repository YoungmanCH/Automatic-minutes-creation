import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

with open("output/output.txt", "r") as f:
    transcription = f.read()

prompt = f"""
あなたは、会議の議事録を作成するプロの秘書です。
以下の文字起こしテキストを読み取り、重要な内容を抽出し、分かりやすく整理された議事録を作成してください。

**ルール：**
- 原文をただ短縮するのではなく、議論の流れ・背景・意見の対立などの文脈を反映してください。
- 「誰が何を言ったのか」を整理し、参加者が会議の全体像を把握できるようにしてください。
- 複数の話題がある場合は、【議題1】【議題2】のように分けて記述してください。
- 発言の文体を整え、読みやすくしてください。
- 発言者が不明な場合は「発言者不明」として記述してください。

**出力フォーマット：**

【会議概要】
- 日時（不明な場合は「不明」と記述）
- 会議名・テーマ（推測できる範囲で）

【参加者】
- 名前があれば列挙、なければ「不明」

【議題1】
- 議題タイトル（抽出）
- 要点
  - 発言者A: ○○○○
  - 発言者B: ○○○○
- 決定事項：
  - △△△△

【議題2】
...

---

以下が会議の文字起こし全文です：

{transcription}
"""


response = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=4000,
    temperature=0.5,
    messages=[{"role": "user", "content": prompt}]
)

output_text = response.content[0].text

output_path = "output/summary_output.txt"
with open(output_path, "w") as f:
    f.write(output_text)

print(f"\n✅ 議事録を {output_path} に保存しました。\n")
