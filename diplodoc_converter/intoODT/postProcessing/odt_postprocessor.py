import os
import zipfile
from pathlib import Path

# ------------------------------------------------------------
# Постобработка ODT
# ------------------------------------------------------------


class OdtPostProcessor:
    def __init__(self, odt_path: Path):
        self.odt_path = odt_path

    def run(self, strategies):
        print("[ODT постобработка]: Начат")
        temp_odt = self.odt_path.with_suffix(".tmp.odt")
        modified = False

        with (
            zipfile.ZipFile(self.odt_path, "r") as yin,
            zipfile.ZipFile(temp_odt, "w", zipfile.ZIP_DEFLATED) as yout,
        ):
            for item in yin.infolist():
                content = yin.read(item.filename)
                if item.filename == "content.xml":
                    content_str = content.decode("utf-8")
                    original = content_str

                    # ВАЖНО: Передаем управление стратегиям.
                    # Чтобы они могли общаться, мы можем выполнять их последовательно.
                    for strat in strategies:
                        content_str = strat.process(content_str)

                    if content_str != original:
                        modified = True
                    content = content_str.encode("utf-8")
                yout.writestr(item, content)

        if modified:
            os.remove(self.odt_path)
            os.rename(temp_odt, self.odt_path)
            print(
                f"[ODT постобработка]: Закончен. Применено стратегий: {len(strategies)}"
            )
        else:
            os.remove(temp_odt)
            print("[ODT постобработка]: Изменений не потребовалось")
