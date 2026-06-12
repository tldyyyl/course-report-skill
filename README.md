# Course Report Skill

[![License: LPPL 1.3c](https://img.shields.io/badge/License-LPPL%201.3c-blue.svg)](https://www.latex-project.org/lppl/)
[![Platform: Claude Code](https://img.shields.io/badge/Platform-Claude%20Code-orange)](https://claude.ai/code)

Claude Code 技能插件 —— 在任意项目中快速创建中文 XeLaTeX 课程报告模板，一键编译为 PDF。

## 功能特性

- 🚀 **一行命令生成**：无需手动复制文件，脚本自动完成模板创建和编译
- 📄 **中文支持完善**：基于 XeLaTeX + xeCJK，支持 Windows / macOS / Linux
- 🎓 **专业封面**：自动生成包含学校、课程、姓名、学号、导师等信息的封面
- 📚 **GB/T 7714 参考文献**：内置国标兼容的 BibTeX 样式
- 🔧 **高度可定制**：命令行参数一键替换封面字段，支持学校 Logo
- 📐 **标准化排版**：A4 纸张、3cm 页边距、章节自动编号、图表浮动体

## 快速开始

### 安装

```bash
# 在 Claude Code 中安装此技能
/install-skill tldyyyl/course-report-skill
```

### 使用

在 Claude Code 对话中直接说：

> 帮我创建一个课程报告

Claude 会依次询问学校、课程、标题、姓名等信息，然后自动生成并编译 PDF。

或者手动运行脚本：

```bash
python scripts/create_report.py \
  --school "电子科技大学" \
  --course "机器学习" \
  --title "基于CNN的图像分类研究" \
  --author "张三" \
  --student-id "202600000001" \
  --advisor "李四" \
  --department "计算机科学与工程学院" \
  --major "计算机科学与技术" \
  --logo /path/to/school-logo.pdf
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--school` | 学校/大学名称 | 学校名称 |
| `--course` | 课程名称 | 课程名称 |
| `--title` | 报告标题 | 课程报告题目 |
| `--author` | 学生姓名 | 学生姓名 |
| `--student-id` | 学号 | 202600000000 |
| `--advisor` | 指导老师姓名 | 指导老师姓名 |
| `--department` | 学院名称 | 学院名称 |
| `--major` | 专业名称 | 专业名称 |
| `--logo` | 学校 Logo 图片路径 | 无 |
| `--output` | 输出目录 | 当前目录 |
| `--force` | 覆盖已有文件 | 否 |
| `--no-compile` | 仅生成模板，不编译 | 否 |

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
    └── logo.pdf           # （可选）学校 Logo
```

## 编译要求

- **XeLaTeX**（TeX Live 2023+ 或 MiKTeX）
- **latexmk**（自动化编译）
- 必需宏包：`xeCJK`、`zhnumber`、`amsmath`、`graphicx`、`booktabs`、`hyperref`、`geometry`、`fancyhdr`、`titlesec`

Windows 用户推荐安装 [TeX Live](https://tug.org/texlive/)，macOS 用户推荐 [MacTeX](https://tug.org/mactex/)。

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
```

添加学校 Logo：

```latex
% 将 logo 图片放入 pic/logo.pdf，然后取消下行注释
\showlogo
```

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

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=tldyyyl/course-report-skill&type=Date)](https://star-history.com/#tldyyyl/course-report-skill&Date)
