rem complex
python -c "from diplodoc_converter.converter import convert_odt_to_diplodoc; from diplodoc_converter.config import ConversionConfig, CacheSettings, ParserSettings; from diplodoc_converter.pandoc_options import PandocOptions; convert_odt_to_diplodoc(ConversionConfig('manual.odt', './gs10/docs/ru', cache_settings=CacheSettings(temp_dir='.temp_convert', keep_cache=False, reuse_cache=False), parser_settings=ParserSettings(max_heading_level_for_single_page=6), pandoc_options=PandocOptions(format='markdown', raw_html=True)))"

rem plain
rem python cli.py manual.odt ./gs10/docs/ru --max-heading-level 2 --keep-cache