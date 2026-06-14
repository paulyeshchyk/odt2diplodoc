from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LuaOptions:
    lua_filter_path: Optional[List[str]] = field(default_factory=list)
    lua_dir: Optional[str] = None
