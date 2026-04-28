# classical-corpus

中国古典文献结构化语料集 — 把殆知阁、wikisource 等公开文本转为统一 JSON schema，可直接喂给任何 LLM 训练或评测。

**当前版本：v0.5** — 完整十三经 + 说文解字 + 资治通鉴 + 二十四史前 4 部，~950 万字，11,132 条记录。

## 覆盖

### 字书
| 文献 | 条数 | 字数 | 来源 | 状态 |
|------|------|------|------|------|
| 说文解字 | 9,831 | 140K | 殆知阁 | 21% 字头为 □（CJK 扩展生僻字，v0.6 计划修复） |

### 十三经（完整）
| 文献 | 条数 | 字数 | 来源 | 状态 |
|------|------|------|------|------|
| 大学 | 1 | 2K | chinese-poetry | ✓ |
| 中庸 | 1 | 4K | chinese-poetry | ✓ |
| 论语 | 20 | 22K | chinese-poetry | ✓ |
| 孟子 | 14 | 46K | chinese-poetry | ✓ |
| 诗经 | 305 | 38K | chinese-poetry | ✓ |
| 尚书 | 55 | 34K | 殆知阁 | 缺 3 篇（殆知阁源文无正文） |
| 礼记 | 47 | 131K | 殆知阁 | 殆知阁合并了曲礼/檀弓/杂记上下 |
| 周易 | 67 | 34K | 殆知阁 | 64 卦 + 4 传序（缺卦三、系辞上） |
| 春秋左传 | 12 | 264K | 殆知阁 | 按 12 公组织 |
| 春秋公羊传 | 12 | 75K | 殆知阁 | ✓ |
| 春秋穀梁传 | 12 | 42K | wikisource | 繁→简自动转换 |
| 孝经 | 18 | 2K | 殆知阁 | ✓ |
| 尔雅 | 19 | 20K | 殆知阁 | ✓ |

### 史
| 文献 | 条数 | 字数 | 来源 |
|------|------|------|------|
| 史记 | 130 | 1.11M | 殆知阁（四库版） |
| 汉书 | 101 | 895K | 殆知阁 |
| 后汉书 | 130 | 1.21M | 殆知阁（四库版） |
| 三国志 | 65 | 734K | 殆知阁 |
| 资治通鉴 | 292 | 4.67M | 殆知阁 |

## 用法

```python
from datasets import load_dataset
ds = load_dataset('json', data_files='output/corpus.jsonl', split='train')
print(ds[0])
# {'id': 'shuowen#1', 'source': '说文解字', ...}
```

或单独 JSON：

```python
import json
shijing = json.load(open('output/wujing/shijing.json'))
```

## Schema

通用字段（所有记录）：`id` `source` `author` `era` `category` `content`

类型特定字段：
- 字书：`char` `radical` `pinyin` `fanqie`
- 经类：`chapter` `subchapter` `section` `title`
- 史类：`volume` `chapter`

详见 [docs/schema.md](docs/schema.md)。

## 数据来源

- **[殆知阁古代文献](https://github.com/garychowcmu/daizhigev20)** — 主要语料源（17 亿字 plaintext）
- **[chinese-poetry](https://github.com/chinese-poetry/chinese-poetry)** — 诗经 + 四书 已是 JSON
- **[zh.wikisource.org](https://zh.wikisource.org/wiki/春秋穀梁傳)** — 穀梁传（殆知阁仅有注疏版）

源数据未托管在本仓库，需自行 clone（殆知阁约 2.1GB git size / 6.9GB 解压）。

## 重新生成

```bash
# 依赖
pip install opencc-python-reimplemented   # 仅 scrape_guliang.py 需要

# 抽取（每个脚本独立可跑）
python scripts/extract_shuowen.py
python scripts/extract_sishu.py
python scripts/extract_shijing.py
python scripts/extract_wujing_others.py
python scripts/extract_remaining_classics.py
python scripts/scrape_guliang.py            # 网络爬取，~15 秒
python scripts/extract_zizhi_tongjian.py
python scripts/extract_histories.py

# 合并 → corpus.jsonl + stats.md
python scripts/build_corpus.py
```

## 已知数据问题

源自殆知阁/wikisource 原文的瑕疵，已记录但未修改：

- **说文 □ 字头**：2102 字头是 `□` 占位符（CJK Extension B-G 区生僻字源文未渲染），v0.6 计划用 ctext.org / CDBert 数据交叉补全
- **资治通鉴卷 158、171**：源文中只有标题占位符，无正文
- **资治通鉴卷 258**：作者属字误为 `寀`，实为 `宋`
- **周易缺卦三、系辞上**：源文格式异常未匹配
- **尚书缺 3 篇**（益稷、禹贡、泰誓上）：源文 TOC 列出但无正文
- **穀梁传字数偏多**：wikisource 版本可能含部分注释，与殆知阁注疏版混杂

## 路线图

- **v0.6** — 用 ctext.org / CDBert 修复说文 □ 字头；补全资治通鉴/尚书/周易缺漏卷
- **v0.7** — 加二十四史下 5 部（晋书、宋书、南齐书、梁书、陈书）
- **v1.0** — 加古译今对齐数据（指令微调集）

## License

数据集 (`output/`) 用 **CC0**，代码 (`scripts/`) 用 **MIT**。详见 [LICENSE](LICENSE)。
