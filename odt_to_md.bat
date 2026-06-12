@echo off
cd /d D:\projects\private\odt2diplodoc
python -m diplodoc_converter.fromODT.cli import ^
    D:\projects\private\gs10_odt\calibr.odt ^
    D:\projects\private\gs10_odt\docs\ru ^
    --enable-crossref ^
    --max-heading-level 6