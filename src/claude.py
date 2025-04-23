import anthropic, os, json, textwrap
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])

with open("output/output.txt", "r") as f:
    raw = f.read()

system_msg = (
    "You are a professional meeting secretary. "
    "Return only JSON. Keys: agenda (list of {title, line_start, line_end})."
)
user_msg = (
    "次の議事録テキストから議題とその行番号範囲を抽出してください。\n\n"
    "```\n" + raw + "\n```"
)

resp1 = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=4000,
    temperature=0.3,
    system=system_msg,
    messages=[{"role": "user", "content": user_msg}],
)
agenda_items = json.loads(resp1.content[0].text)["agenda"]

minutes = {"会議概要": {}, "参加者": [], "議題": []}

for ag in agenda_items:
    segment = "\n".join(raw.splitlines()[ag["line_start"]-1 : ag["line_end"]])
    prompt = textwrap.dedent(f"""
        ## 役割
        あなたは会議の議事録を作成するプロの秘書です。
        ## 出力形式
        JSON で出力してください。 keys: title, points, decisions, speaker_list
        ## 入力
        ```
        {segment}
        ```
    """).strip()

    r = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4000,
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}],
    )
    minutes["議題"].append(json.loads(r.content[0].text))

def to_md(m):
    md = ["## 会議概要", "- 日時: 不明", "- 会議名: 不明", "", "## 参加者"]
    md += [f"- {p}" for p in set(sum([g['speaker_list'] for g in m['議題']], [])) or ["不明"]]

    for idx, g in enumerate(m["議題"], 1):
        md += [f"\n## 議題{idx}: {g['title']}"]
        md += ["### 要点"] + [f"- {pt}" for pt in g["points"]]
        md += ["### 決定事項"] + [f"- {d}" for d in g["decisions"] or ["（決定事項なし）"]]
    return "\n".join(md)

with open("output/summary_output.md", "w") as f:
    f.write(to_md(minutes))
print("✅ 生成完了 : output/summary_output.md")
