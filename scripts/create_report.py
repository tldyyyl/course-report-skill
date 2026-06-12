#!/usr/bin/env python
"""Create a course report template from bundled skill assets."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def template_root() -> Path:
    return skill_root() / "assets" / "template"


def iter_template_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def relative_template_files(root: Path) -> list[Path]:
    return [path.relative_to(root) for path in iter_template_files(root)]


def find_conflicts(src_root: Path, dst_root: Path) -> list[Path]:
    conflicts: list[Path] = []
    for rel_path in relative_template_files(src_root):
        dst_path = dst_root / rel_path
        if dst_path.exists():
            conflicts.append(rel_path)
            continue
        parent = dst_path.parent
        while parent != dst_root.parent:
            if parent.exists() and not parent.is_dir():
                conflicts.append(rel_path)
                break
            if parent == dst_root:
                break
            parent = parent.parent
    return conflicts


def copy_template(src_root: Path, dst_root: Path, force: bool) -> None:
    if not src_root.is_dir():
        raise FileNotFoundError(f"Template assets not found: {src_root}")

    dst_root.mkdir(parents=True, exist_ok=True)

    conflicts = find_conflicts(src_root, dst_root)
    if conflicts and not force:
        print("Refusing to overwrite existing files:", file=sys.stderr)
        for rel_path in conflicts:
            print(f"  {rel_path}", file=sys.stderr)
        print("Use --force to overwrite these files.", file=sys.stderr)
        raise SystemExit(2)

    for src_path in iter_template_files(src_root):
        rel_path = src_path.relative_to(src_root)
        dst_path = dst_root / rel_path
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)


def customize_template(dst_root: Path, args: argparse.Namespace) -> None:
    """Customize the template with user-provided values."""
    main_tex = dst_root / "main.tex"
    if not main_tex.exists():
        return

    content = main_tex.read_text(encoding="utf-8")

    # Replace school name
    if args.school:
        content = content.replace("\\school{学校名称}", f"\\school{{{args.school}}}")

    # Replace course name
    if args.course:
        content = content.replace("\\course{课程名称}", f"\\course{{{args.course}}}")

    # Replace title
    if args.title:
        content = content.replace("\\title{课程报告题目}{Course Report Title}",
                                  f"\\title{{{args.title}}}{{Course Report Title}}")

    # Replace author
    if args.author:
        content = content.replace("\\author{学生姓名}{Student Name}",
                                  f"\\author{{{args.author}}}{{Student Name}}")

    # Replace student ID
    if args.student_id:
        content = content.replace("\\studentnumber{202600000000}",
                                  f"\\studentnumber{{{args.student_id}}}")

    # Replace department
    if args.department:
        content = content.replace("\\department{学院名称}{School Name}",
                                  f"\\department{{{args.department}}}{{School Name}}")

    # Replace major
    if args.major:
        content = content.replace("\\major{专业名称}{Major Name}",
                                  f"\\major{{{args.major}}}{{Major Name}}")

    # Replace advisor
    if args.advisor:
        content = content.replace("\\advisor{指导老师姓名}{Advisor Name}",
                                  f"\\advisor{{{args.advisor}}}{{Advisor Name}}")

    main_tex.write_text(content, encoding="utf-8")


def compile_report(dst_root: Path) -> int:
    if shutil.which("latexmk") is None:
        print("latexmk was not found on PATH. Install TeX Live/MiKTeX or run with --no-compile.", file=sys.stderr)
        return 127

    command = ["latexmk", "-xelatex", "main.tex"]
    print(f"Running: {' '.join(command)}")
    completed = subprocess.run(command, cwd=dst_root)
    if completed.returncode != 0:
        print("Compilation failed. Check main.log in the output directory.", file=sys.stderr)
    elif not (dst_root / "main.pdf").is_file():
        print("Compilation finished but main.pdf was not created.", file=sys.stderr)
        return 1
    else:
        print(f"Created PDF: {dst_root / 'main.pdf'}")
    return completed.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create and optionally compile a course report template.")
    parser.add_argument(
        "--output",
        default=".",
        help="Target directory. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing template files in the target directory.",
    )
    parser.add_argument(
        "--no-compile",
        action="store_true",
        help="Copy the template but do not run latexmk.",
    )
    parser.add_argument(
        "--school",
        help="School/university name.",
    )
    parser.add_argument(
        "--course",
        help="Course name.",
    )
    parser.add_argument(
        "--title",
        help="Report title.",
    )
    parser.add_argument(
        "--author",
        help="Student name.",
    )
    parser.add_argument(
        "--student-id",
        help="Student ID number.",
    )
    parser.add_argument(
        "--department",
        help="Department/school name.",
    )
    parser.add_argument(
        "--major",
        help="Major name.",
    )
    parser.add_argument(
        "--advisor",
        help="Advisor/supervisor name.",
    )
    parser.add_argument(
        "--logo",
        help="Path to school logo image (will be copied to pic/logo.pdf).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    src_root = template_root()
    dst_root = Path(args.output).expanduser().resolve()

    copy_template(src_root, dst_root, args.force)
    print(f"Template copied to: {dst_root}")

    # Copy logo if provided
    if args.logo:
        logo_path = Path(args.logo).expanduser().resolve()
        if logo_path.exists():
            pic_dir = dst_root / "pic"
            pic_dir.mkdir(exist_ok=True)
            shutil.copy2(logo_path, pic_dir / "logo.pdf")
            print(f"Logo copied to: {pic_dir / 'logo.pdf'}")
        else:
            print(f"Warning: Logo file not found: {logo_path}", file=sys.stderr)

    customize_template(dst_root, args)

    if args.no_compile:
        return 0
    return compile_report(dst_root)


if __name__ == "__main__":
    raise SystemExit(main())
