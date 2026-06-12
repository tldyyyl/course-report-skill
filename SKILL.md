---
name: course-report
description: Create, compile, maintain, or refactor Chinese LaTeX course report templates. Use when a user wants a course report PDF in any project without manually copying template files, or when working with `course-report.cls`, `main.tex`, XeLaTeX course reports, cover fields, course-report cleanup, continuous chapter headings, or tasks that mention course report, 课程报告, or assignment report.
---

# Course Report

## Workflow

When invoked, this skill should interactively gather information from the user before creating the report.

### Step 1: Gather Information

Ask the user the following questions using the `AskUserQuestion` tool:

1. **学校名称** - "请输入你的学校/大学名称"
2. **课程名称** - "请输入课程名称"
3. **报告标题** - "请输入课程报告的标题"
4. **学生姓名** - "请输入你的姓名"
5. **学号** - "请输入你的学号"
6. **指导老师** - "请输入指导老师姓名"
7. **学院/专业** - "请输入学院和专业名称"
8. **学校Logo** - "是否需要在封面显示学校Logo？如果需要，请提供Logo图片路径"

### Step 2: Create and Compile

After gathering information, run the script with the provided values:

```bash
python <skill-root>/scripts/create_report.py \
  --school "学校名称" \
  --course "课程名称" \
  --title "报告标题" \
  --author "学生姓名" \
  --student-id "学号" \
  --advisor "指导老师" \
  --department "学院" \
  --major "专业" \
  --logo "logo路径"  # 如果用户提供了logo
```

### Step 3: Verify Output

1. Check if `main.pdf` was created successfully
2. If logo was provided, verify it appears on the cover
3. Report the output file location to the user

## Creating a Report in Any Project

Use the bundled script instead of manually copying template files:

```bash
python <skill-root>/scripts/create_report.py
```

- Default target is the current working directory.
- The script copies `main.tex`, `course-report.cls`, `course-report.bst`, `latexmkrc`, `reference.bib`, and `pic/` directory.
- It refuses to overwrite existing files by default. If the user explicitly wants replacement, run with `--force`.
- It compiles automatically with `latexmk -xelatex main.tex` and creates `main.pdf`.
- Use `--output <dir>` for a different target directory.
- Use `--no-compile` when only the source template should be created.
- If compilation fails, keep the generated files and summarize the LaTeX/log error. Do not delete user files.

## Customization Options

The template supports the following customizations via command-line arguments or editing `main.tex`:

### Command-line Arguments (create_report.py)

- `--school <name>`: Set school name (default: "学校名称")
- `--logo <path>`: Path to school logo image (default: none, placeholder used)
- `--course <name>`: Set course name (default: "课程名称")
- `--title <title>`: Set report title (default: "课程报告题目")
- `--author <name>`: Set student name (default: "学生姓名")
- `--student-id <id>`: Set student ID (default: "202600000000")
- `--advisor <name>`: Set advisor/supervisor name (default: "指导老师姓名")
- `--department <name>`: Set department/school (default: "学院名称")
- `--major <name>`: Set major (default: "专业名称")

### Editing main.tex

After creating the template, you can customize cover fields directly in `main.tex`:

```latex
\school{你的学校名称}
\course{课程名称}
\title{报告题目}{Report Title}
\author{你的姓名}{Your Name}
\studentnumber{你的学号}
\advisor{指导老师姓名}{Advisor Name}
\department{学院名称}{Department Name}
\major{专业名称}{Major Name}
```

### Adding School Logo

Place your school logo in `pic/logo.pdf` and uncomment the logo line in `main.tex`:

```latex
\showlogo  % Uncomment this line to display logo
```

## Course Report Structure

- Use `\documentclass[course]{course-report}` for course reports.
- Keep the cover fields to: school name, course name, report title, student name, student ID, advisor, department/major, and completion date.
- Make the cover title exactly `课程报告` and `COURSE REPORT`.
- Remove thesis-only front matter: originality declaration, Chinese abstract, English abstract, list of figures, list of tables, and nomenclature/glossary.
- Remove thesis-only back matter: acknowledgements, degree-period publications/achievements, and translation appendices.
- Keep references through `\coursebibliography{...}` unless the user asks for another bibliography workflow.

## Chapter Behavior

- Keep `\chapter` available for users who want report-scale top-level divisions.
- In course-report mode, chapters must not force a page break between each other.
- Keep chapter title spacing consistent before and after every chapter heading; do not rely on manual `\vspace` in `main.tex`.
- Prefer `\section` and `\subsection` for most daily course-report content, but do not break existing cross-reference numbering without a clear reason.

## Editing Guidance

- Do not delete source assets such as `pic/`, `.bib` files, or example chapter files just because `main.tex` no longer references them.
- Avoid broad rewrites of the course report class. Add guarded course-mode logic so other modes continue to work.
- Keep placeholders realistic and short in `main.tex`; the file should be usable immediately as a report skeleton.

## Template Files

The template includes:

- `main.tex` - Main LaTeX document with example content
- `course-report.cls` - LaTeX class file defining formatting
- `course-report.bst` - Bibliography style file (GB/T 7714 compatible)
- `latexmkrc` - Build configuration for latexmk
- `reference.bib` - Example bibliography file
- `pic/` - Directory for images (logo, figures)

## Compilation Requirements

- XeLaTeX (for Chinese typesetting)
- latexmk (for automated compilation)
- Required packages: xeCJK, zhnumber, amsmath, graphicx, booktabs, hyperref, geometry, fancyhdr, titlesec

## Common Tasks

### Adding a New Chapter
```latex
\chapter{章节标题}
\section{小节标题}
正文内容...
```

### Adding Figures
```latex
\begin{figure}[h]
  \includegraphics[width=0.8\textwidth]{pic/your-image.png}
  \caption{图片说明}
  \label{fig:your-label}
\end{figure}
```

### Adding Tables
```latex
\begin{table}[h]
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

### Adding Equations
```latex
\begin{equation}
  \label{eq:your-label}
  E = mc^2
\end{equation}
```

### Citing References
```latex
正文引用\cite{key1}，上标引用\citing{key2}。
```
