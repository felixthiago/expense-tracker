"""Load Poppins font if available."""
import os
from pathlib import Path

from PyQt6.QtGui import QFontDatabase

from app.config import FONTS_DIR

def load_fonts() -> str:
    fonts_path = Path(FONTS_DIR)
    if fonts_path.exists():
        for f in fonts_path.glob("*.ttf"):
            try:
                fid = QFontDatabase.addApplicationFont(str(f))
                if fid != -1:
                    print(f'loaded font: {f.name}')
                    families = QFontDatabase.applicationFontFamilies(fid)
                    if families and "Poppins" in families[0]:
                        font_family = "Poppins"
                        break
                else:
                    print(f'failed to load font {f.name}')
            except Exception:
                pass

    return font_family
