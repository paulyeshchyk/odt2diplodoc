from diplodoc_converter.fromODT.model.CacheSettings import CacheSettings
from diplodoc_converter.fromODT.model.ConversionConfig import ConversionConfig
from diplodoc_converter.fromODT.model.ConverterMessages import ConverterMessages
from diplodoc_converter.fromODT.pandoc_utils.LuaOptions import LuaOptions
from diplodoc_converter.fromODT.model.OdtCrossReferences import OdtCrossReferences
from diplodoc_converter.fromODT.model.ParserSettings import ParserSettings
from diplodoc_converter.fromODT.pandoc_utils.PandocOptions import (
    PandocOptions,
)
from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext


class ConfigBuilder:
    def build_conversion_context(self, args, messages: ConverterMessages):
        config = self.build_conversion_config(args)
        return ConversionContext(config, messages)

    def build_conversion_config(self, args):
        lua_filters = []
        if args.lua_filter:
            for item in args.lua_filter:
                parsed = _parse_lua_filters(item)
                if parsed:
                    lua_filters.extend(parsed)

        parser_settings = ParserSettings(
            max_heading_level_for_single_page=args.max_heading_level
        )
        lua_options = LuaOptions(lua_filter_path=lua_filters, lua_dir=args.lua_dir)

        if args.pandoc_format:
            pandoc_options = PandocOptions(raw_format=args.pandoc_format)
        else:
            pandoc_options = PandocOptions(
                format="markdown",
                raw_html=True,
                pipe_tables=True,
                backtick_code_blocks=True,
                lua_options=lua_options,
            )

        odtCross = OdtCrossReferences(
            enable_crossref=args.enable_crossref,
            crossref_metadata_file=args.crossref_metadata_file,
        )

        cache_settings = CacheSettings(
            temp_dir=args.temp_dir,
            keep_cache=args.keep_cache,
            reuse_cache=args.reuse_cache,
        )

        config = ConversionConfig(
            odt_path=args.odt_path,
            output_dir=args.output_dir,
            cache_settings=cache_settings,
            parser_settings=parser_settings,
            pandoc_options=pandoc_options,
            odt_crossreferences_options=odtCross,
        )

        return config


def _parse_lua_filters(value: str | None) -> list[str] | None:
    if not value:
        return None
    filters = [f.strip() for f in value.split(",") if f.strip()]
    return filters if filters else None
