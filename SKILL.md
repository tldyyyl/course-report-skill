---
name: course-report
description: Create, compile, maintain, or refactor Chinese LaTeX course report templates. Use when a user wants a course report PDF in any project without manually copying template files, or when working with `course-report.cls`, `main.tex`, XeLaTeX course reports, cover fields, course-report cleanup, continuous chapter headings, or tasks that mention course report, 课程报告, or assignment report.
---

# Course Report

## Workflow

When invoked, gather the missing information before creating the report. Reuse values already supplied by the user and do not ask for them again.

### Step 1: Gather Information

Ask for the following information using the user-input mechanism available in the current agent environment. Keep questions concise and batch clearly related cover fields when that reduces unnecessary turns:

1. **学校名称** - "请输入你的学校/大学名称"。Agent 同时确定学校官方英文名称，不使用机器直译
2. **课程名称** - "请输入课程名称"
3. **报告标题** - "请输入课程报告的标题"
4. **学生姓名** - "请输入你的姓名"
5. **学号** - "请输入你的学号"
6. **指导老师** - "请输入指导老师姓名"
7. **学院/专业** - "请输入学院和专业名称"
8. **完成日期** - "请输入报告完成日期；留空则使用当前日期"
9. **学校Logo** - "是否需要在封面显示学校Logo？如果需要，请提供PDF、PNG、JPG或JPEG图片路径"

When the user provides multiple Logo files, prefer a vector PDF. Use PNG, JPG, or JPEG only when no suitable PDF is available. Do not silently reuse a school-specific Logo for another school.

### Step 2: Create and Compile

After gathering information, run the script with the provided values:

```bash
python <skill-root>/scripts/create_report.py \
  --school "学校名称" \
  --school-en "学校官方英文名称" \
  --course "课程名称" \
  --title "报告标题" \
  --author "学生姓名" \
  --student-id "学号" \
  --advisor "指导老师" \
  --department "学院" \
  --major "专业" \
  --date "完成日期" \
  --logo "logo路径" \
  --compiler auto
```

### Step 3: Verify Output

1. Check if `main.pdf` was created successfully
2. Render every PDF page to PNG with `pdftoppm` or an equivalent PDF renderer
3. Visually inspect the cover, table of contents, page transitions, headers/footers, figures, tables, equations, code, references, and long text for clipping, overlap, blank pages, or broken glyphs
4. If logo was provided, verify the correct Logo appears sharply on the cover
5. Verify internal links exist for the table of contents and all demonstrated cross-references
6. Fix defects, recompile, and repeat the full render-and-inspect cycle
7. Report the output file location only after visual verification passes

Do not treat successful XeLaTeX compilation as sufficient visual verification. If no PDF renderer is available, state that limitation explicitly instead of claiming the layout was checked.

## Creating a Report in Any Project

Use the bundled script instead of manually copying template files:

```bash
python <skill-root>/scripts/create_report.py
```

- Default target is the current working directory.
- The script copies `main.tex`, `course-report.cls`, `course-report.bst`, `latexmkrc`, `reference.bib`, and `pic/` directory.
- It refuses to overwrite existing files by default. If the user explicitly wants replacement, run with `--force`.
- It compiles automatically and creates `main.pdf`. The default `auto` mode falls back to direct XeLaTeX/BibTeX compilation when `latexmk` is unavailable or fails.
- Use `--output <dir>` for a different target directory.
- Use `--no-compile` when only the source template should be created.
- If compilation fails, keep the generated files and summarize the LaTeX/log error. Do not delete user files.

## Customization Options

The template supports the following customizations via command-line arguments or editing `main.tex`:

### Command-line Arguments (create_report.py)

- `--school <name>`: Set school name (default: "学校名称")
- `--school-en <name>`: Set the official English school name. The agent must supply it when known
- `--logo <path>`: Path to school logo image (default: none, placeholder used)
- `--course <name>`: Set course name (default: "课程名称")
- `--title <title>`: Set report title (default: "课程报告题目")
- `--author <name>`: Set student name (default: "学生姓名")
- `--student-id <id>`: Set student ID (default: "202600000000")
- `--advisor <name>`: Set advisor/supervisor name (default: "指导老师姓名")
- `--department <name>`: Set department/school (default: "学院名称")
- `--major <name>`: Set major (default: "专业名称")
- `--date <date>`: Set report completion date (default: LaTeX current date)
- `--compiler <auto|latexmk|xelatex>`: Select compilation strategy (default: `auto`)

Command-line cover values are plain text and are escaped before insertion into LaTeX. Users who need custom LaTeX markup should edit the generated `main.tex`.

### Editing main.tex

After creating the template, you can customize cover fields directly in `main.tex`:

```latex
\school{你的学校名称}{Official English School Name}
\course{课程名称}
\title{报告题目}{Report Title}
\author{你的姓名}{Your Name}
\studentnumber{你的学号}
\advisor{指导老师姓名}{Advisor Name}
\department{学院名称}{Department Name}
\major{专业名称}{Major Name}
\completiondate{\today}
```

### Adding School Logo

PDF, PNG, JPG, and JPEG Logos are supported. `--logo` preserves the real extension and enables the Logo automatically. For manual configuration:

```latex
\reportlogo{pic/logo.png}
\showlogo
```

Prefer a PDF vector Logo for print output. Raster formats remain supported for compatibility.

## Course Report Structure

- Use `\documentclass[course]{course-report}` for course reports.
- Keep the cover fields to: school name, course name, report title, student name, student ID, advisor, department/major, and completion date.
- Make the cover title exactly `课程报告` and `COURSE REPORT`.
- Remove thesis-only front matter: originality declaration, Chinese abstract, English abstract, list of figures, list of tables, and nomenclature/glossary.
- Remove thesis-only back matter: acknowledgements, degree-period publications/achievements, and translation appendices.
- Keep references through `\coursebibliography{...}` unless the user asks for another bibliography workflow.
- Use `\label` with `\autoref` for chapters, equations, figures, tables, and code. Use `\citing` for bibliography citations.
- Keep links single-directional, black, and borderless. Do not add bibliography backlinks unless explicitly requested.
- Keep the bundled GB/T 7714-compatible BibTeX workflow lightweight; do not import an external thesis bibliography stack.
- Never make generated reports depend on a local thesis-template directory.
- Do not copy GPL thesis-template source into this skill. Reference layout ideas only and preserve this project's existing license boundaries.

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
- latexmk (recommended) or BibTeX for the direct fallback chain
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
