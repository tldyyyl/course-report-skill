# Course Report Skill

[![License: LPPL 1.3c](https://img.shields.io/badge/License-LPPL%201.3c-blue.svg)](https://www.latex-project.org/lppl/)
[![Platform: Codex & Claude Code](https://img.shields.io/badge/Platform-Codex%20%26%20Claude%20Code-orange)](https://github.com/tldyyyl/course-report-skill)

适用于 Codex 和 Claude Code 的技能插件，在任意项目中快速创建可编辑的中文 XeLaTeX 课程报告并编译为 PDF。

## 功能特性

- 🚀 **一行命令生成**：无需手动复制文件，脚本自动完成模板创建和编译
- 📄 **中文支持完善**：基于 XeLaTeX + xeCJK，支持 Windows / macOS / Linux
- 🎓 **专业封面**：自动生成包含学校、课程、姓名、学号、导师等信息的封面
- 📚 **GB/T 7714 参考文献**：内置国标兼容的 BibTeX 样式
- 🔧 **高度可定制**：命令行参数一键替换封面字段，支持学校 Logo
- 📐 **标准化排版**：A4 纸张、3cm 页边距、章节自动编号、图表浮动体

## 安装

把本仓库地址复制给 Agent 智能体，并对它说：

> 请将这个 GitHub 仓库作为 Skill 安装到你当前环境的用户级 Skill 目录。请自行识别正确的安装目录，确保 `SKILL.md` 位于该 Skill 的根目录，安装完成后检查依赖并验证 `scripts/create_report.py --help` 可以正常运行。不要修改仓库内容，也不要把仓库重复嵌套一层。仓库地址：https://github.com/tldyyyl/course-report-skill

## 快速使用

在 Codex 或 Claude Code 对话中直接说：

> 帮我创建一个课程报告

Agent 会询问尚未提供的报告信息，确定学校官方英文名，优先选择矢量校徽，然后生成、编译并逐页检查 PDF。

或者手动运行脚本：

```bash
python scripts/create_report.py \
  --school "XX大学" \
  --school-en "University of Electronic Science and Technology of China" \
  --course "机器学习" \
  --title "基于CNN的图像分类研究" \
  --author "张三" \
  --student-id "202600000001" \
  --advisor "李四" \
  --department "计算机科学与工程学院" \
  --major "计算机科学与技术" \
  --date "2026年6月12日" \
  --logo /path/to/school-logo.png \
  --compiler auto
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--school` | 学校/大学名称 | 学校名称 |
| `--school-en` | 学校官方英文名称 | 已知学校自动匹配，否则 University Name |
| `--course` | 课程名称 | 课程名称 |
| `--title` | 报告标题 | 课程报告题目 |
| `--author` | 学生姓名 | 学生姓名 |
| `--student-id` | 学号 | 202600000000 |
| `--advisor` | 指导老师姓名 | 指导老师姓名 |
| `--department` | 学院名称 | 学院名称 |
| `--major` | 专业名称 | 专业名称 |
| `--date` | 报告完成日期 | LaTeX 当前日期 |
| `--logo` | 学校 Logo 图片路径 | 无 |
| `--compiler` | `auto`、`latexmk` 或 `xelatex` | auto |
| `--output` | 输出目录 | 当前目录 |
| `--force` | 覆盖已有文件 | 否 |
| `--no-compile` | 仅生成模板，不编译 | 否 |

命令行封面字段按普通文本处理，脚本会自动转义 `&`、`_`、`%` 等 LaTeX 特殊字符。需要使用 LaTeX 命令时，可在生成后直接编辑 `main.tex`。

使用技能时，Agent 应根据学校中文名称填写官方英文校名并传入 `--school-en`，不使用机器直译。脚本仅为少量已知学校提供确定性回退，例如“示例大学”对应 `Example University`。

## 模板结构

生成的报告模板包含以下文件：

```
your-report/
├── main.tex              # LaTeX 主文档（含示例章节）
├── course-report.cls      # 文档类文件
├── course-report.bst      # GB/T 7714 参考文献样式
├── latexmkrc              # latexmk 编译配置
├── reference.bib          # 示例参考文献
└── pic/                   # 图片资源目录
    └── logo.<ext>         # （可选）学校 Logo
```

## 编译要求

- **XeLaTeX**（TeX Live 2023+ 或 MiKTeX）
- **latexmk**（推荐）或 **BibTeX**
- 必需宏包：`xeCJK`、`zhnumber`、`amsmath`、`graphicx`、`booktabs`、`hyperref`、`geometry`、`fancyhdr`、`titlesec`

默认 `--compiler auto` 优先使用 `latexmk`。如果 `latexmk` 缺失或执行失败，脚本会回退到 `xelatex → bibtex → xelatex → xelatex`。显式指定 `latexmk` 或 `xelatex` 时不会自动切换。

## 封面自定义

在生成的 `main.tex` 中直接修改封面字段：

```latex
\school{你的学校}{Your School}
\course{课程名称}
\title{报告题目}{Report Title}
\author{你的姓名}{Your Name}
\studentnumber{你的学号}
\advisor{指导老师}{Advisor}
\department{学院名称}{Department}
\major{专业名称}{Major}
\completiondate{\today}
```

添加学校 Logo：

```latex
\reportlogo{pic/logo.png}
\showlogo
```

支持 PDF、PNG、JPG 和 JPEG。通过 `--logo` 提供图片时，脚本会保留真实扩展名并自动启用封面 Logo。
用于打印时优先选择 PDF 矢量校徽；PNG、JPG 和 JPEG 用于兼容已有素材。

## 交叉引用

目录、章节、图、表、公式、代码和参考文献引用均为单向可点击链接。使用 `\label` 定义目标，使用 `\autoref` 引用文档对象，使用 `\citing` 引用文献：

```latex
\chapter{方法}\label{chap:method}
如\autoref{chap:method}和\autoref{eq:objective}所示。
相关研究见\citing{example2024}。
```

链接保持黑色且无边框，适合屏幕阅读与打印；参考文献条目不提供返回正文的反向链接。

## 常用 LaTeX 代码片段

### 添加章节

```latex
\chapter{章节标题}
\section{小节标题}
正文内容...
```

### 插入图片

```latex
\begin{figure}[h]
  \centering
  \includegraphics[width=0.8\textwidth]{pic/your-image.png}
  \caption{图片说明}
  \label{fig:your-label}
\end{figure}
```

### 插入表格

```latex
\begin{table}[h]
  \centering
  \caption{表格说明}
  \label{tab:your-label}
  \begin{tabular}{ccc}
    \toprule
    列1 & 列2 & 列3 \\
    \midrule
    数据1 & 数据2 & 数据3 \\
    \bottomrule
  \end{tabular}
\end{table}
```

### 插入公式

```latex
\begin{equation}
  \label{eq:your-label}
  E = mc^2
\end{equation}
```

### 引用文献

```latex
正文引用\cite{key1}，上标引用\citing{key2}。
```

## 项目文件说明

```
course-report-skill/
├── SKILL.md                     # 技能定义（入口）
├── scripts/
│   └── create_report.py         # 模板创建与编译脚本
├── assets/
│   └── template/
│       ├── main.tex             # LaTeX 模板主文档
│       ├── course-report.cls    # 文档类（泛化自 thesis-uestc）
│       ├── course-report.bst    # 参考文献样式
│       ├── latexmkrc            # 编译配置
│       ├── reference.bib        # 示例参考文献
│       └── pic/                 # 图片目录
└── references/                  # 参考材料
```

## 测试

```bash
python -m unittest discover -v
```

测试覆盖模板生成、字段转义、Logo、编译器回退和 XeLaTeX 冒烟编译；缺少 TeX 工具时编译测试会明确跳过。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=tldyyyl/course-report-skill&type=Date)](https://star-history.com/#tldyyyl/course-report-skill&Date)
