# ODT to Diplodoc Converter

This tool turns a technical document from ODT format (LibreOffice Writer) into a set of files ready for **Diplodoc** — a modern system for technical documentation.

Below is a short list of routine tasks this converter does for you.

---

## 1. Split one ODT file into many MD files with folders

**Without the tool:**  
Open ODT, copy each chapter by hand, create folders, write `index.md`, `index.yaml`, `toc.yaml`. If you change the document, do everything again.

**With the tool:**  
The converter finds headings (`#`, `##`, `###` …) and creates nested folders. Each folder has `index.md`, `index.yaml`, `toc.yaml`. The structure follows the ODT exactly.

---

## 2. Move images and fix their paths

**Without the tool:**  
Extract all images from ODT manually, copy them into subfolders, fix paths in Markdown files (they often have absolute paths like `C:\...`).

**With the tool:**  
The script runs `pandoc` with `--extract-media`, finds all images, copies them into a `media` folder next to each `index.md`, and fixes links to relative paths (`media/name.png`).

---

## 3. Keep figure captions (including numbers)

**Without the tool:**  
Rewrite each caption below the image, check the figure number, keep the same style (“Figure 1. Title”).

**With the tool:**  
The script takes the full caption from the `{alt="..."}` field, adds a missing space after the number if needed, and puts the caption in italics right under the image.

---

## 4. Turn two-column table notes into `{% note info %}` blocks

**Without the tool:**  
Edit HTML tables by hand, remove extra columns, move text into `{% note %}` tags.

**With the tool:**  
The converter finds tables like  
`+-----+-----+ | ![](img) | Note text | +-----+-----+`, deletes the left column with the picture, keeps only the text, and wraps it into `{% note info %}…{% endnote %}`.

---

## 5. Remove Pandoc garbage attributes (`{alt="..."}`)

**Without the tool:**  
Pandoc often leaves lines like `{alt="Figure 49: …"}`, which appear in the final HTML. You must delete them from every file.

**With the tool:**  
The script automatically removes all such attributes, leaving clean Markdown.

---

## 6. Generate the YAML files needed by Diplodoc

**Without the tool:**  
Create `index.yaml` (fields `title`, `href`, `meta`) and `toc.yaml` (with `items`, `include`) by hand.

**With the tool:**  
All YAML files are generated automatically:  
- inside each folder – `index.yaml` and `toc.yaml`;  
- in the root folder – `index.yaml`, `toc.yaml`, `index.md`;  
- links in `toc.yaml` point to `index.md`, and for sub-sections an `include: {path: ..., mode: link}` is added.

---

## 7. Fix internal links (between chapters)

**Without the tool:**  
In ODT the author often puts cross-references like “see chapter 2”. After conversion they become `[see chapter 2](#anchor-209)`, which do not work in Diplodoc. You have to find and replace each link manually.

**With the tool:**  
The script builds a map of all anchors (`anchor-209` -> `path/to/section/index.md`) and automatically replaces the links with relative paths that Diplodoc understands.

---

## 8. Control caching and Pandoc options with config and CLI

**Without the tool:**  
You have to run Pandoc every time, even when only post-processing changes (like note style). You cannot give Pandoc a custom format string (`markdown-raw_html+pipe_tables`).

**With the tool:**  
- You can keep a cache (folder with `full_doc.md`) and skip calling Pandoc on next runs — faster work.  
- Through `cli.py` or the `PandocOptions` dataclass you can set any format extensions (`+`, `-` or not set).  
- You can use Lua filters (e.g. to remove image size attributes).

---

## 9. Integration with Visual Studio Code

**Without the tool:**  
You must run scripts from the command line, remember paths and flags, difficult to debug.

**With the tool:**  
The repository includes a `.vscode/launch.json` file with a ready-to-use Python debug configuration. Just open the project folder in VSCode, press `F5`, and the converter starts with your chosen parameters.

Also the official **Diplodoc** extension for VSCode lets you preview the result, check links and YAML structure right in the editor.

---

## 10. Flexibility for future changes (strategy architecture)

**Without the tool:**  
Any change to the converter’s behaviour requires editing the main code – risky and time-consuming.

**With the tool:**  
All post-processing is moved into **strategies**:
- Global strategies (applied to the whole Markdown before parsing).  
- Section strategies (applied to the body of each article after parsing).  

To add a new transformation (e.g. convert three-column tables into lists), you just write one class and register it in `__init__.py`. The rest of the code stays unchanged.

---

## How to start

1. Install Python 3.11+, Pandoc, PyYAML.  
2. Clone the repository, create a virtual environment.  
3. Put your `manual.odt` in the root folder.  
4. Run `python cli.py manual.odt ./docs/ru --pandoc-format "markdown-raw_html"`.  
5. The result is ready to build with `diplodoc build`.

For more settings, see comments in `cli.py` and `config.py`.

---

## License

This project is licensed under the MIT License — free to use and modify.