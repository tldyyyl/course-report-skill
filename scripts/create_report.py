#!/usr/bin/env python
"""Create a course report template from bundled skill assets."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


LATEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "#": r"\#",
    "$": r"\$",
    "%": r"\%",
    "&": r"\&",
    "_": r"\_",
    "^": r"\textasciicircum{}",
    "~": r"\textasciitilde{}",
}
SUPPORTED_LOGO_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg"}
LOCAL_LOGO_FILENAMES = {
    f"logo{suffix}" for suffix in SUPPORTED_LOGO_SUFFIXES
}


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def template_root() -> Path:
    return skill_root() / "assets" / "template"


def iter_template_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and not (
            path.relative_to(root).parent == Path("pic")
            and path.name.lower() in LOCAL_LOGO_FILENAMES
        )
    )


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


def escape_latex_text(value: str) -> str:
    return "".join(LATEX_ESCAPES.get(char, char) for char in value)


def replace_required(content: str, placeholder: str, replacement: str) -> str:
    if placeholder not in content:
        raise ValueError(f"Template placeholder not found: {placeholder}")
    return content.replace(placeholder, replacement, 1)


def install_logo(dst_root: Path, logo_value: str) -> Path:
    logo_path = Path(logo_value).expanduser().resolve()
    if not logo_path.is_file():
        raise ValueError(f"Logo file not found: {logo_path}")

    suffix = logo_path.suffix.lower()
    if suffix not in SUPPORTED_LOGO_SUFFIXES:
        raise ValueError("Unsupported logo format. Use PDF, PNG, JPG, or JPEG.")

    destination = dst_root / "pic" / f"logo{suffix}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(logo_path, destination)

    main_tex = dst_root / "main.tex"
    if not main_tex.is_file():
        raise ValueError(f"Template file not found: {main_tex}")

    content = main_tex.read_text(encoding="utf-8")
    content = replace_required(
        content,
        r"\reportlogo{pic/logo.pdf}",
        rf"\reportlogo{{pic/logo{suffix}}}",
    )
    content = replace_required(content, "% \\showlogo", r"\showlogo")
    main_tex.write_text(content, encoding="utf-8")
    return destination


def customize_template(dst_root: Path, args: argparse.Namespace) -> None:
    """Customize the template with user-provided values."""
    main_tex = dst_root / "main.tex"
    if not main_tex.exists():
        return

    content = main_tex.read_text(encoding="utf-8")

    school = getattr(args, "school", None)
    school_en = getattr(args, "school_en", None)
    if school or school_en:
        chinese_name = escape_latex_text(school or "学校名称")
        english_name = escape_latex_text(
            school_en or "University Name"
        )
        content = replace_required(
            content,
            r"\school{学校名称}{University Name}",
            rf"\school{{{chinese_name}}}{{{english_name}}}",
        )

    field_specs = (
        ("course", r"\course{课程名称}", r"\course{{{}}}"),
        ("title", r"\title{课程报告题目}{Course Report Title}", r"\title{{{}}}{{Course Report Title}}"),
        ("author", r"\author{学生姓名}{Student Name}", r"\author{{{}}}{{Student Name}}"),
        ("student_id", r"\studentnumber{202600000000}", r"\studentnumber{{{}}}"),
        ("advisor", r"\advisor{指导老师姓名}{Advisor Name}", r"\advisor{{{}}}{{Advisor Name}}"),
        (
            "department",
            r"\department{学院名称}{Department Name}",
            r"\department{{{}}}{{Department Name}}",
        ),
        ("major", r"\major{专业名称}{Major Name}", r"\major{{{}}}{{Major Name}}"),
        ("date", r"\completiondate{\today}", r"\completiondate{{{}}}"),
    )
    for attribute, placeholder, replacement_template in field_specs:
        value = getattr(args, attribute, None)
        if value:
            replacement = replacement_template.format(escape_latex_text(value))
            content = replace_required(content, placeholder, replacement)

    main_tex.write_text(content, encoding="utf-8")


def run_command(
    command: list[str],
    cwd: Path,
    runner=subprocess.run,
) -> int:
    print(f"Running: {' '.join(command)}")
    return runner(command, cwd=cwd).returncode


def compile_with_xelatex(dst_root: Path, runner=subprocess.run) -> int:
    commands = (
        ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        ["bibtex", "main"],
        ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
    )
    for command in commands:
        return_code = run_command(command, dst_root, runner)
        if return_code != 0:
            print(
                f"Compilation command failed with exit code {return_code}: {' '.join(command)}",
                file=sys.stderr,
            )
            return return_code
    return 0


def required_commands_available(commands: tuple[str, ...], which=shutil.which) -> bool:
    missing = [command for command in commands if which(command) is None]
    if not missing:
        return True
    print(
        f"Required command(s) not found on PATH: {', '.join(missing)}",
        file=sys.stderr,
    )
    return False


def finalize_compilation(dst_root: Path, return_code: int) -> int:
    if return_code != 0:
        print("Compilation failed. Check main.log in the output directory.", file=sys.stderr)
        return return_code
    if not (dst_root / "main.pdf").is_file():
        print("Compilation finished but main.pdf was not created.", file=sys.stderr)
        return 1
    print(f"Created PDF: {dst_root / 'main.pdf'}")
    return 0


def compile_report(
    dst_root: Path,
    compiler: str = "auto",
    which=shutil.which,
    runner=subprocess.run,
) -> int:
    if compiler == "latexmk":
        if not required_commands_available(("latexmk",), which):
            return 127
        return finalize_compilation(
            dst_root,
            run_command(["latexmk", "-xelatex", "main.tex"], dst_root, runner),
        )

    if compiler == "xelatex":
        if not required_commands_available(("xelatex", "bibtex"), which):
            return 127
        return finalize_compilation(dst_root, compile_with_xelatex(dst_root, runner))

    if compiler != "auto":
        raise ValueError(f"Unsupported compiler mode: {compiler}")

    if which("latexmk") is not None:
        latexmk_result = run_command(
            ["latexmk", "-xelatex", "main.tex"],
            dst_root,
            runner,
        )
        if latexmk_result == 0 and (dst_root / "main.pdf").is_file():
            return finalize_compilation(dst_root, latexmk_result)
        if latexmk_result == 0:
            print(
                "latexmk created no PDF; falling back to direct XeLaTeX/BibTeX compilation.",
                file=sys.stderr,
            )
        else:
            print(
                "latexmk failed; falling back to direct XeLaTeX/BibTeX compilation.",
                file=sys.stderr,
            )
    else:
        print(
            "latexmk was not found; falling back to direct XeLaTeX/BibTeX compilation.",
            file=sys.stderr,
        )

    if not required_commands_available(("xelatex", "bibtex"), which):
        return 127
    return finalize_compilation(dst_root, compile_with_xelatex(dst_root, runner))


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
        help="Copy the template but do not compile it.",
    )
    parser.add_argument(
        "--compiler",
        choices=("auto", "latexmk", "xelatex"),
        default="auto",
        help="Compilation strategy. Defaults to auto.",
    )
    parser.add_argument(
        "--school",
        help="School/university name.",
    )
    parser.add_argument(
        "--school-en",
        help="Official English school/university name.",
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
        "--date",
        help="Report completion date.",
    )
    parser.add_argument(
        "--logo",
        help="Path to a PDF, PNG, JPG, or JPEG school logo.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    src_root = template_root()
    dst_root = Path(args.output).expanduser().resolve()

    copy_template(src_root, dst_root, args.force)
    print(f"Template copied to: {dst_root}")

    try:
        customize_template(dst_root, args)
        if args.logo:
            logo_destination = install_logo(dst_root, args.logo)
            print(f"Logo copied to: {logo_destination}")
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    if args.no_compile:
        return 0
    return compile_report(dst_root, args.compiler)


if __name__ == "__main__":
    raise SystemExit(main())
