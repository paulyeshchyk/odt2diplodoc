@echo off
cd /d D:\projects\private\odt2diplodoc
python -m diplodoc_converter.intoODT.cli build ^
    -i D:\projects\private\gs10_odt\docs\ru ^
    -o D:\projects\private\gs10_odt\calibr.odt ^
    --width-threshold 700 ^
    --reference D:\projects\private\gs10_odt\reference.odt