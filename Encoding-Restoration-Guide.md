# Восстановление комментариев при проблемах с кодировкой (Cp1251 → UTF-8)

## RU

## Цель

В исходниках иногда оказываются **битые или пустые комментарии**: кириллица пропадает, остаются только пробелы и знаки. Обычно это следствие того, что файлы были в кодировке **Windows-1251 (Cp1251)** и позже были открыты или сохранены как **UTF-8** без перекодировки. Байты кириллицы тогда интерпретируются неверно и «рассыпаются».

Данная инструкция описывает, как восстановить такие комментарии из истории Git (где сохранена версия в Cp1251) и сохранить файл уже в **UTF-8**. Скрипты и инструкция расположены в **корне репозитория** и могут использоваться для любой библиотеки (Nmsdk-PulseLib, Rdk-BasicLib и др.).

---

## EN

## Script locations

All scripts are located in the directory **`Scripts/`** at the repository root:

- `Scripts/detect_encoding.py` — detect file encoding (Cp1251 / UTF-8)
- `Scripts/convert_cp1251_to_utf8.py` — convert files from Cp1251 to UTF-8
- `Scripts/restore_cp1251_comments.py` — restore broken comments from a Git reference

**Run:** from the repository root, for example: `python Scripts/detect_encoding.py ...`

---

## Detecting files in Cp1251

To find source files still stored in encoding **Cp1251** (rather than UTF-8), a raw-byte script is used:

- **UTF-8 Cyrillic:** two-byte sequences `0xD0/0xD1` + `0x80–0xBF`.
- **Cp1251 Cyrillic:** single bytes `0xC0–0xFF`, not part of a UTF-8 pair.

**Script:** `Scripts/detect_encoding.py`

**Run from the repository root:**

For one library (for example, Nmsdk-PulseLib):

```bash
python Scripts/detect_encoding.py Libraries/Nmsdk-PulseLib/Core
```

The script prints each file path and label `cp1251` или `utf8`. To write the Cp1251 file list to a separate file:

```bash
python Scripts/detect_encoding.py Libraries/Nmsdk-PulseLib/Core --list cp1251_files.txt
```

File `cp1251_files.txt` is created only if at least one Cp1251 file is found. Paths in the file are relative to the current directory; for conversion use the same library directory as `root_dir` and paths like `Core/File.cpp`.

---

## Cp1251 → UTF-8 conversion

If Cp1251 files are found, **first** convert them to UTF-8, then run comment restoration if needed (see below).

**Script:** `Scripts/convert_cp1251_to_utf8.py`

**Run from the repository root:**

- **root_dir** — library directory (or repository root) paths are relative to.

Read path list from file (paths in the file are relative to `root_dir`, for example `Core/File.cpp`):

```bash
python Scripts/convert_cp1251_to_utf8.py Libraries/Nmsdk-PulseLib --list cp1251_files.txt
```

If `detect_encoding.py` was run from the library directory and wrote paths like `Core/File.cpp`, use `root_dir=Libraries/Nmsdk-PulseLib`. If paths in the file look like `Libraries/Nmsdk-PulseLib/Core/File.cpp`, use `root_dir=.` (repository root).

Specify files manually (paths relative to `root_dir`):

```bash
python Scripts/convert_cp1251_to_utf8.py Libraries/Nmsdk-PulseLib Core/SomeFile.h Core/Other.cpp
```

The script reads each file as **Cp1251**, decodes to Unicode, and writes **UTF-8**.

**Workflow:** first encoding detection → convert Cp1251 files to UTF-8 → then verify and restore broken comments (script `restore_cp1251_comments.py`) across all sources.

---

## 1. How to find a good version in Git

1. Go to the repository (or submodule) containing the problem file.  
   For example, для Nmsdk-PulseLib: `Libraries/Nmsdk-PulseLib`; для another library — её directory.

2. View file history:
   ```bash
   cd Libraries/Nmsdk-PulseLib
   git log --oneline -- Core/NPulseSynapse.h
   ```

3. Pick a commit **before** bulk encoding changes or with a message like «Comment updated». Для Nmsdk-PulseLib was used commit **bcf94ed**.

4. Verify comments in the chosen commit are actually in Cp1251:
   ```bash
   git show <коммит>:Core/NPulseSynapse.h
   ```
   If the UTF-8 console shows **mojibake** of the same length as the expected Russian text, the file in that commit is likely stored in **Cp1251**.

---

## 2. How to get comments in the correct encoding

Get the file content from the commit as **raw bytes**, then decode as **Cp1251** to Unicode (in the script `restore_cp1251_comments.py` this is done automatically).

---

## 3. How to apply comments to the current file

Script `restore_cp1251_comments.py` does this automatically: builds from the reference (Git version decoded from Cp1251) map «next code line» → «comment above it», finds broken comments in the current file (empty or without Cyrillic; does not touch commented-out code) and substitutes reference comments. The result is written in UTF-8.

---

## 4. Comment restoration script

**Path:** `Scripts/restore_cp1251_comments.py`

**Run from the repository root:**

```bash
python Scripts/restore_cp1251_comments.py <каталог_репозитория_библиотеки> <путь_к_файлу_от_корня_этой_библиотеки> [коммит]
```

- **library_repository_directory** — path to the library Git repository root (submodule), for example `Libraries/Nmsdk-PulseLib`.
- **file_path_from_library_root** — file path **from that library root**, for example `Core/NPulseSynapse.h`.
- **commit** — optional argument; default `bcf94ed`.

**Examples (from repository root):**

Restore comments in one file Nmsdk-PulseLib:

```bash
python Scripts/restore_cp1251_comments.py Libraries/Nmsdk-PulseLib Core/NPulseSynapse.h
```

Specify another commit:

```bash
python Scripts/restore_cp1251_comments.py Libraries/Nmsdk-PulseLib Core/NPulseSynapseCommon.h 2b564e8
```

Restore several files in sequence (Nmsdk-PulseLib):

```bash
for f in Core/NPulseSynapse.h Core/NPulseSynapse.cpp Core/NPulseSynapseCommon.h Core/NPulseSynapseCommon.cpp; do
  python Scripts/restore_cp1251_comments.py Libraries/Nmsdk-PulseLib "$f"
done
```

В PowerShell:

```powershell
python Scripts/restore_cp1251_comments.py Libraries/Nmsdk-PulseLib Core/NPulseSynapse.h
python Scripts/restore_cp1251_comments.py Libraries/Nmsdk-PulseLib Core/NPulseSynapse.cpp
python Scripts/restore_cp1251_comments.py Libraries/Nmsdk-PulseLib Core/NPulseSynapseCommon.h
python Scripts/restore_cp1251_comments.py Libraries/Nmsdk-PulseLib Core/NPulseSynapseCommon.cpp
```

**For another library** substitute its directory for `Libraries/Nmsdk-PulseLib` and the file path relative to its root.

---

## 5. Verification after restoration

1. **Visually** open the file in a UTF-8 editor and verify comments display correctly.
2. **Build:** build the project (for example, via CMake), to ensure edits did not break compilation.
3. Commit changes to Git if needed (in the submodule or root repository).

---

## 6. Limitations and tips

- **Different code structure:** if member names, types, or declaration order changed between the chosen commit and the current version, some comments may remain unmatched. Pick another commit or add comments manually.
- **Commented-out code:** the script does not replace lines that look like commented-out code (for example, `// return false;`, `// if (...)`) — only empty or clearly broken comments.
- **Encoding when saving:** when editing manually, save the file in **UTF-8**.

---

## 7. Completed work (example)

Comments were restored with the scripts in files Nmsdk-PulseLib (commit **bcf94ed**): including `Core/NPulseSynapse.h`, `Core/NPulseSynapse.cpp`, `Core/NPulseSynapseCommon.h`, `Core/NPulseSynapseCommon.cpp` and others in `Core/`. For files added after the chosen commit, the script prints «Skip (file not in commit)»; specify another commit or restore comments manually.
