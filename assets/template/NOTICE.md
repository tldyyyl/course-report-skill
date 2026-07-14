# Third-Party and Derived Work Notice

## Upstream Work

`course-report.cls` is a modified derivative of `thesis-uestc.cls`, and
`course-report.bst` uses the bibliography implementation from
`thesis-uestc.bst`.

- Original author and maintainer: Wen Wang `<wangwen1192@outlook.com>`
- Original project: <https://github.com/bdebye/thesisuestc>
- Original files: `thesis-uestc.cls` and `thesis-uestc.bst`
- License: LaTeX Project Public License, version 1.3 or later

The original author and upstream maintainers do not provide support for this
derived work. Issues concerning this distribution should be reported to
<https://github.com/tldyyyl/course-report-skill>.

## Modifications

The following changes were made for this project in 2026:

- Renamed the distributed class and bibliography style to `course-report`.
- Reworked the default document mode around editable course reports rather
  than degree theses.
- Replaced school-specific cover data with generic school, course, author,
  student, advisor, department, major, date, and optional Logo fields.
- Removed degree-thesis front and back matter from the generated report
  skeleton while retaining selected legacy command names for compatibility.
- Allowed consecutive course-report chapters without forced page breaks and
  adjusted chapter, section, header, footer, figure, table, and code layout.
- Added Windows, macOS, and TeX Live Fandol font fallback behavior.
- Added black, borderless, one-way hyperlinks for the table of contents,
  cross-references, and bibliography citations.
- Added the `course-report` bibliography alias and report-oriented examples.

As of 2026-07-14, no bibliography formatting logic from the upstream
`thesis-uestc.bst` has been changed; only its distributed filename and license
notice differ. The repository Git history records subsequent changes to these
derived files.

## Other Reference Material

The local Example University thesis template was used
only as a manual design reference. Its GPL-licensed source is not copied into
this distribution, and generated reports have no runtime dependency on it.
