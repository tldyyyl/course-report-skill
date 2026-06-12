from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "create_report.py"

SPEC = importlib.util.spec_from_file_location("create_report", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load create_report module from {SCRIPT_PATH}")

create_report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(create_report)


class CreateReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.output_dir = Path(self.temp_dir.name) / "output"

    def copy_template(self) -> None:
        create_report.copy_template(
            create_report.template_root(),
            self.output_dir,
            force=False,
        )

    @staticmethod
    def customization_args(**overrides: str | None) -> Namespace:
        values = {
            "school": None,
            "school_en": None,
            "course": None,
            "title": None,
            "author": None,
            "student_id": None,
            "department": None,
            "major": None,
            "advisor": None,
            "date": None,
        }
        values.update(overrides)
        return Namespace(**values)

    def test_copy_template_copies_all_bundled_files(self) -> None:
        source = create_report.template_root()

        create_report.copy_template(source, self.output_dir, force=False)

        expected = create_report.relative_template_files(source)
        actual = sorted(
            path.relative_to(self.output_dir)
            for path in self.output_dir.rglob("*")
            if path.is_file()
        )
        self.assertEqual(expected, actual)

    def test_copy_template_refuses_existing_files_without_force(self) -> None:
        self.output_dir.mkdir(parents=True)
        existing = self.output_dir / "main.tex"
        existing.write_text("user content", encoding="utf-8")

        with self.assertRaises(SystemExit) as context:
            create_report.copy_template(
                create_report.template_root(),
                self.output_dir,
                force=False,
            )

        self.assertEqual(2, context.exception.code)
        self.assertEqual("user content", existing.read_text(encoding="utf-8"))

    def test_copy_template_overwrites_existing_files_with_force(self) -> None:
        self.output_dir.mkdir(parents=True)
        existing = self.output_dir / "main.tex"
        existing.write_text("user content", encoding="utf-8")

        create_report.copy_template(
            create_report.template_root(),
            self.output_dir,
            force=True,
        )

        self.assertEqual(
            (create_report.template_root() / "main.tex").read_text(encoding="utf-8"),
            existing.read_text(encoding="utf-8"),
        )

    def test_customize_template_replaces_every_cover_field(self) -> None:
        self.copy_template()
        args = self.customization_args(
            school="测试大学",
            school_en="Test University",
            course="软件工程",
            title="课程设计",
            author="张三",
            student_id="20260001",
            advisor="李老师",
            department="计算机学院",
            major="软件工程",
        )

        create_report.customize_template(self.output_dir, args)

        content = (self.output_dir / "main.tex").read_text(encoding="utf-8")
        expected_lines = (
            r"\school{测试大学}{Test University}",
            r"\course{软件工程}",
            r"\title{课程设计}{Course Report Title}",
            r"\author{张三}{Student Name}",
            r"\studentnumber{20260001}",
            r"\advisor{李老师}{Advisor Name}",
            r"\department{计算机学院}{Department Name}",
            r"\major{软件工程}{Major Name}",
        )
        for line in expected_lines:
            with self.subTest(line=line):
                self.assertIn(line, content)

    def test_customize_template_infers_known_english_school_name(self) -> None:
        self.copy_template()

        create_report.customize_template(
            self.output_dir,
            self.customization_args(school="示例大学"),
        )

        content = (self.output_dir / "main.tex").read_text(encoding="utf-8")
        self.assertIn(
            r"\school{示例大学}{Example University}",
            content,
        )

    def test_parse_args_accepts_english_school_name(self) -> None:
        with mock.patch(
            "sys.argv",
            ["create_report.py", "--school-en", "Test University"],
        ):
            args = create_report.parse_args()

        self.assertEqual("Test University", args.school_en)

    def test_customize_template_escapes_latex_special_characters(self) -> None:
        self.copy_template()
        args = self.customization_args(
            title=r"C:\课程_{A&B} #1 50% $x^2$ ~",
        )

        create_report.customize_template(self.output_dir, args)

        content = (self.output_dir / "main.tex").read_text(encoding="utf-8")
        self.assertIn(
            r"\title{C:\textbackslash{}课程\_\{A\&B\} \#1 50\% "
            r"\$x\textasciicircum{}2\$ \textasciitilde{}}{Course Report Title}",
            content,
        )

    def test_customize_template_fails_when_expected_placeholder_is_missing(self) -> None:
        self.copy_template()
        main_tex = self.output_dir / "main.tex"
        content = main_tex.read_text(encoding="utf-8")
        main_tex.write_text(
            content.replace(r"\school{学校名称}{University Name}", ""),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "Template placeholder not found"):
            create_report.customize_template(
                self.output_dir,
                self.customization_args(school="测试大学"),
            )

    def test_install_logo_preserves_supported_extension_and_enables_logo(self) -> None:
        for suffix in (".pdf", ".png", ".jpg", ".jpeg"):
            with self.subTest(suffix=suffix):
                case_root = Path(self.temp_dir.name) / suffix[1:]
                create_report.copy_template(
                    create_report.template_root(),
                    case_root,
                    force=False,
                )
                source_logo = Path(self.temp_dir.name) / f"source{suffix}"
                source_logo.write_bytes(b"test logo")

                destination = create_report.install_logo(case_root, str(source_logo))

                self.assertEqual(case_root / "pic" / f"logo{suffix}", destination)
                self.assertEqual(b"test logo", destination.read_bytes())
                content = (case_root / "main.tex").read_text(encoding="utf-8")
                self.assertIn(fr"\reportlogo{{pic/logo{suffix}}}", content)
                self.assertIn("\n\\showlogo\n", content)

    def test_install_logo_rejects_missing_file(self) -> None:
        self.copy_template()

        with self.assertRaisesRegex(ValueError, "Logo file not found"):
            create_report.install_logo(
                self.output_dir,
                str(Path(self.temp_dir.name) / "missing.png"),
            )

    def test_install_logo_rejects_directory(self) -> None:
        self.copy_template()
        logo_directory = Path(self.temp_dir.name) / "logo.png"
        logo_directory.mkdir()

        with self.assertRaisesRegex(ValueError, "Logo file not found"):
            create_report.install_logo(self.output_dir, str(logo_directory))

    def test_install_logo_rejects_unsupported_extension(self) -> None:
        self.copy_template()
        source_logo = Path(self.temp_dir.name) / "logo.svg"
        source_logo.write_text("<svg/>", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "Unsupported logo format"):
            create_report.install_logo(self.output_dir, str(source_logo))

    def test_customize_template_leaves_default_completion_date_without_argument(self) -> None:
        self.copy_template()

        create_report.customize_template(
            self.output_dir,
            self.customization_args(),
        )

        content = (self.output_dir / "main.tex").read_text(encoding="utf-8")
        self.assertIn(r"\completiondate{\today}", content)

    def test_customize_template_replaces_and_escapes_custom_completion_date(self) -> None:
        self.copy_template()

        create_report.customize_template(
            self.output_dir,
            self.customization_args(date="2026_06_12"),
        )

        content = (self.output_dir / "main.tex").read_text(encoding="utf-8")
        self.assertIn(r"\completiondate{2026\_06\_12}", content)

    def test_parse_args_accepts_date_option(self) -> None:
        with mock.patch(
            "sys.argv",
            ["create_report.py", "--date", "2026 年 6 月 12 日"],
        ):
            args = create_report.parse_args()

        self.assertEqual("2026 年 6 月 12 日", args.date)

    def compiler_fixture(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "main.tex").write_text("test", encoding="utf-8")
        commands = []

        def runner(command, cwd):
            commands.append(command)
            return SimpleNamespace(returncode=0)

        return commands, runner

    def test_compile_auto_uses_latexmk_when_successful(self) -> None:
        commands, base_runner = self.compiler_fixture()

        def runner(command, cwd):
            result = base_runner(command, cwd)
            (Path(cwd) / "main.pdf").write_bytes(b"pdf")
            return result

        result = create_report.compile_report(
            self.output_dir,
            compiler="auto",
            which=lambda command: f"/tools/{command}",
            runner=runner,
        )

        self.assertEqual(0, result)
        self.assertEqual([["latexmk", "-xelatex", "main.tex"]], commands)

    def test_compile_auto_falls_back_when_latexmk_is_missing(self) -> None:
        commands, base_runner = self.compiler_fixture()

        def which(command):
            return None if command == "latexmk" else f"/tools/{command}"

        def runner(command, cwd):
            result = base_runner(command, cwd)
            if len(commands) == 4:
                (Path(cwd) / "main.pdf").write_bytes(b"pdf")
            return result

        result = create_report.compile_report(
            self.output_dir,
            compiler="auto",
            which=which,
            runner=runner,
        )

        self.assertEqual(0, result)
        self.assertEqual("xelatex", commands[0][0])
        self.assertEqual("bibtex", commands[1][0])
        self.assertEqual(4, len(commands))

    def test_compile_auto_falls_back_when_latexmk_fails(self) -> None:
        commands, _ = self.compiler_fixture()

        def runner(command, cwd):
            commands.append(command)
            if command[0] == "latexmk":
                return SimpleNamespace(returncode=1)
            if len(commands) == 5:
                (Path(cwd) / "main.pdf").write_bytes(b"pdf")
            return SimpleNamespace(returncode=0)

        result = create_report.compile_report(
            self.output_dir,
            compiler="auto",
            which=lambda command: f"/tools/{command}",
            runner=runner,
        )

        self.assertEqual(0, result)
        self.assertEqual("latexmk", commands[0][0])
        self.assertEqual("xelatex", commands[1][0])
        self.assertEqual(5, len(commands))

    def test_compile_auto_falls_back_when_latexmk_creates_no_pdf(self) -> None:
        commands, _ = self.compiler_fixture()

        def runner(command, cwd):
            commands.append(command)
            if len(commands) == 5:
                (Path(cwd) / "main.pdf").write_bytes(b"pdf")
            return SimpleNamespace(returncode=0)

        result = create_report.compile_report(
            self.output_dir,
            compiler="auto",
            which=lambda command: f"/tools/{command}",
            runner=runner,
        )

        self.assertEqual(0, result)
        self.assertEqual("latexmk", commands[0][0])
        self.assertEqual("xelatex", commands[1][0])
        self.assertEqual(5, len(commands))

    def test_compile_latexmk_mode_does_not_fallback(self) -> None:
        commands, _ = self.compiler_fixture()

        def runner(command, cwd):
            commands.append(command)
            return SimpleNamespace(returncode=7)

        result = create_report.compile_report(
            self.output_dir,
            compiler="latexmk",
            which=lambda command: f"/tools/{command}",
            runner=runner,
        )

        self.assertEqual(7, result)
        self.assertEqual([["latexmk", "-xelatex", "main.tex"]], commands)

    def test_compile_xelatex_runs_expected_command_sequence(self) -> None:
        commands, base_runner = self.compiler_fixture()

        def runner(command, cwd):
            result = base_runner(command, cwd)
            if len(commands) == 4:
                (Path(cwd) / "main.pdf").write_bytes(b"pdf")
            return result

        result = create_report.compile_report(
            self.output_dir,
            compiler="xelatex",
            which=lambda command: f"/tools/{command}",
            runner=runner,
        )

        self.assertEqual(0, result)
        self.assertEqual(
            [
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                ["bibtex", "main"],
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
            ],
            commands,
        )

    def test_compile_fails_when_pdf_is_not_created(self) -> None:
        _, runner = self.compiler_fixture()

        result = create_report.compile_report(
            self.output_dir,
            compiler="latexmk",
            which=lambda command: f"/tools/{command}",
            runner=runner,
        )

        self.assertEqual(1, result)

    def test_parse_args_accepts_compiler_option(self) -> None:
        with mock.patch(
            "sys.argv",
            ["create_report.py", "--compiler", "xelatex"],
        ):
            args = create_report.parse_args()

        self.assertEqual("xelatex", args.compiler)

    def test_course_mode_body_transition_does_not_use_cleardoublepage(self) -> None:
        class_content = (
            create_report.template_root() / "course-report.cls"
        ).read_text(encoding="utf-8")
        start = class_content.index(r"\newcommand{\thesiscontent}")
        end = class_content.index(r"\pretocmd{\@chapter}", start)
        transition = class_content[start:end]

        self.assertIn(r"\clearpage", transition)
        self.assertNotIn(r"\cleardoublepage", transition)
        self.assertNotIn(r"\newpage", transition)

    def test_fandol_fallback_uses_tex_live_font_files(self) -> None:
        class_content = (
            create_report.template_root() / "course-report.cls"
        ).read_text(encoding="utf-8")

        expected_fragments = (
            r"\setCJKmainfont[AutoFakeBold=true]{FandolSong-Regular.otf}",
            r"\newCJKfontfamily{\heiti}{FandolHei-Regular.otf}",
            r"\setcoursefonts{FandolSong-Regular.otf}{FandolHei-Regular.otf}",
            r"\setCJKmonofont{FandolFang-Regular.otf}",
        )
        for fragment in expected_fragments:
            self.assertIn(fragment, class_content)

    def test_template_contains_clickable_cross_reference_examples(self) -> None:
        content = (create_report.template_root() / "main.tex").read_text(
            encoding="utf-8"
        )

        expected_fragments = (
            r"\label{chap:introduction}",
            r"\label{eq:objective}",
            r"\label{fig:example}",
            r"\label{tab:example}",
            r"\label{lst:example}",
            r"\autoref{chap:introduction}",
            r"\autoref{eq:objective}",
            r"\autoref{fig:example}",
            r"\autoref{tab:example}",
            r"\autoref{lst:example}",
            r"\citing{example2024}",
        )
        for fragment in expected_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, content)


class CreateReportIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.output_dir = Path(self.temp_dir.name) / "report"

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *arguments],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_cli_generates_customized_template(self) -> None:
        completed = self.run_cli(
            "--output",
            str(self.output_dir),
            "--no-compile",
            "--school",
            "测试大学",
            "--course",
            "C++ 程序设计",
            "--title",
            "A&B_课程报告",
            "--author",
            "张三",
            "--student-id",
            "2026_001",
            "--advisor",
            "李老师",
            "--department",
            "计算机学院",
            "--major",
            "软件工程",
            "--date",
            "2026_06_12",
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue((self.output_dir / "main.tex").is_file())
        self.assertTrue((self.output_dir / "course-report.cls").is_file())
        content = (self.output_dir / "main.tex").read_text(encoding="utf-8")
        self.assertIn(r"\course{C++ 程序设计}", content)
        self.assertIn(r"\title{A\&B\_课程报告}{Course Report Title}", content)
        self.assertIn(r"\studentnumber{2026\_001}", content)
        self.assertIn(r"\department{计算机学院}{Department Name}", content)
        self.assertIn(r"\completiondate{2026\_06\_12}", content)
        self.assertFalse((REPO_ROOT / "main.aux").exists())
        self.assertFalse((REPO_ROOT / "main.pdf").exists())

    @unittest.skipUnless(
        shutil.which("xelatex") and shutil.which("bibtex"),
        "XeLaTeX and BibTeX are required for the compilation smoke test.",
    )
    def test_cli_compiles_report_with_escaped_fields(self) -> None:
        completed = self.run_cli(
            "--output",
            str(self.output_dir),
            "--compiler",
            "xelatex",
            "--title",
            "A&B_课程报告",
            "--student-id",
            "2026_001",
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        pdf_path = self.output_dir / "main.pdf"
        self.assertTrue(pdf_path.is_file())
        self.assertGreater(pdf_path.stat().st_size, 0)

    def test_cli_rejects_invalid_logo_with_exit_code_two(self) -> None:
        missing_logo = Path(self.temp_dir.name) / "missing.png"

        completed = self.run_cli(
            "--output",
            str(self.output_dir),
            "--no-compile",
            "--logo",
            str(missing_logo),
        )

        self.assertEqual(2, completed.returncode)
        self.assertIn("Logo file not found", completed.stderr)
        self.assertTrue((self.output_dir / "main.tex").is_file())


if __name__ == "__main__":
    unittest.main()
