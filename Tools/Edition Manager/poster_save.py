import argparse
import configparser
import os
import re
import sys
from pathlib import Path
from io import BytesIO

from plexapi.server import PlexServer
import requests
from PIL import Image

THIS_DIR = Path(__file__).resolve().parent
CONFIG_PATH = THIS_DIR / "config.ini"

DEFAULT_CONFIG = {
    "PLEX": {
        "url": "http://127.0.0.1:32400",
        "token": "",
        "output_format": "jpg",
        "overwrite": "false",
    },
    "MAPPED_FOLDERS": {}
}

def load_config() -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        cfg.read(CONFIG_PATH)

    for section, values in DEFAULT_CONFIG.items():
        if section not in cfg:
            cfg[section] = {}
        for key, value in values.items():
            if key not in cfg[section]:
                cfg[section][key] = value

    return cfg

def save_config(cfg: configparser.ConfigParser) -> None:
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        cfg.write(f)

CONFIG = load_config()

PLEX_URL   = CONFIG["PLEX"]["url"].strip()
PLEX_TOKEN = CONFIG["PLEX"]["token"].strip()

OUTPUT_FORMAT = CONFIG["PLEX"].get("output_format", "jpg").lower()
if OUTPUT_FORMAT not in {"jpg", "png"}:
    OUTPUT_FORMAT = "jpg"

OVERWRITE = CONFIG["PLEX"].get("overwrite", "false").lower() == "true"

MAPPED_FOLDERS = {}
if "MAPPED_FOLDERS" in CONFIG:
    for host, container in CONFIG["MAPPED_FOLDERS"].items():
        MAPPED_FOLDERS[Path(host)] = Path(container)

_MAPPED_FOLDERS = MAPPED_FOLDERS

def map_path(file_path: Path) -> Path:
    for host, container in _MAPPED_FOLDERS.items():
        if container in file_path.parents:
            return host / file_path.relative_to(container)
    return file_path

def _existing_variants(save_dir: Path, base: str) -> dict:
    return {
        "jpg": (save_dir / f"{base}.jpg"),
        "png": (save_dir / f"{base}.png"),
    }

def _ensure_rgb(img: Image.Image) -> Image.Image:
    if img.mode in ("RGBA", "P"):
        return img.convert("RGB")
    if img.mode != "RGB":
        return img.convert("RGB")
    return img

def _download_image_bytes(url: str, token: str) -> bytes:
    headers = {"X-Plex-Token": token}
    params = {"X-Plex-Token": token}
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.content

def _season_number_from_item(season_item) -> int:
    n = getattr(season_item, "index", None) or getattr(season_item, "seasonNumber", None)
    if n:
        try:
            return int(n)
        except Exception:
            pass
    title = getattr(season_item, "title", "") or ""
    m = re.search(r"(\d+)", title)
    return int(m.group(1)) if m else 0  # 0 for Specials if no number found

def _season_poster_basename(season_item) -> str:
    num = _season_number_from_item(season_item)
    return f"season {num:02d}" if num > 0 else "season special"

def _save_image_bytes_as_format(data: bytes, target_path: Path, out_format: str) -> None:
    img = Image.open(BytesIO(data))
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if out_format.lower() == "jpg":
        img = _ensure_rgb(img)
        img.save(target_path, format="JPEG", quality=95)
    elif out_format.lower() == "png":
        img.save(target_path, format="PNG", optimize=True)
    else:
        raise ValueError("OUTPUT_FORMAT must be 'jpg' or 'png'.")

def _handle_overwrite_policy(save_dir: Path, base: str, out_format: str) -> bool:
    variants = _existing_variants(save_dir, base)
    want = variants[out_format]
    other = variants["png" if out_format == "jpg" else "jpg"]

    if OVERWRITE:
        if other.exists():
            try:
                other.unlink()
                print(f"Removed existing {other.name} to enforce {out_format.upper()} for {base}.")
            except Exception as e:
                print(f"Warning: could not remove {other.name}: {e}")
        return True
    else:
        if want.exists() or other.exists():
            print(f"Skipping: {base} already exists in {save_dir} (overwrite disabled).")
            return False
        return True

def _save_asset(item, url: str, save_dir: Path, base: str, out_format: str, display_name: str):
    save_dir.mkdir(parents=True, exist_ok=True)
    proceed = _handle_overwrite_policy(save_dir, base, out_format)
    if not proceed:
        return

    target = save_dir / f"{base}.{out_format}"
    title = getattr(item, "title", "item")
    print(f"Downloading {display_name} for {title} -> {target}")
    try:
        data = _download_image_bytes(url, PLEX_TOKEN)
        _save_image_bytes_as_format(data, target, out_format)
    except Exception as e:
        print(f"Failed to download {display_name} for {title}: {e}")

def _search_by_title(plex, title, library=None, libtype=None):
    results = []
    if library:
        try:
            section = plex.library.section(library)
            results = section.search(title=title, libtype=libtype) if libtype else section.search(title=title)
        except Exception as e:
            print(f"Could not open library '{library}': {e}")
            return []
    else:
        try:
            results = plex.library.search(title=title, libtype=libtype) if libtype else plex.library.search(title=title)
        except Exception as e:
            print(f"Search failed: {e}")
            return []

    seen = set()
    unique = []
    for item in results:
        rk = getattr(item, "ratingKey", None)
        if rk and rk not in seen:
            seen.add(rk)
            unique.append(item)
    return unique

def _describe_item_for_pick(item):
    t = getattr(item, "title", "Unknown")
    y = getattr(item, "year", None)
    try:
        sec = item.section().title
    except Exception:
        sec = "Unknown Library"
    typ = item.type if hasattr(item, "type") else item.__class__.__name__.lower()
    if y:
        return f"{t} ({y}) — [{sec} / {typ}]"
    return f"{t} — [{sec} / {typ}]"

def _pick_one_cli(items):
    if not items:
        print("No matches.")
        return None

    print(f"\nFound {len(items)} match(es):\n")
    for idx, it in enumerate(items, start=1):
        print(f"{idx}. {_describe_item_for_pick(it)}")

    choice_raw = input("\nSelect a number (Enter for 1, or 0 to cancel): ").strip() or "1"
    try:
        n = int(choice_raw)
    except ValueError:
        print("Invalid selection.")
        return None

    if n == 0:
        print("Cancelled.")
        return None
    if 1 <= n <= len(items):
        return items[n - 1]

    print("Invalid selection.")
    return None

def save_library(library, libtype=None, poster=False, art=False):
    for item in library.all(libtype=libtype, includeGuids=False):
        save_item(item, poster=poster, art=art)

VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".m4v", ".wmv", ".mpg", ".mpeg", ".ts", ".m2ts", ".webm"}

def _media_dir_from_item(item) -> Path:
    p = None

    if getattr(item, "locations", None):
        p = Path(item.locations[0])
    else:
        try:
            p = Path(item.media[0].parts[0].file)
        except Exception:
            p = None

    if p is None and getattr(item, "type", None) == "season":
        try:
            eps = item.episodes()
            if eps:
                ep = eps[0]
                if getattr(ep, "locations", None):
                    p = Path(ep.locations[0])
                else:
                    p = Path(ep.media[0].parts[0].file)
        except Exception:
            p = None

    if p is None and getattr(item, "type", None) == "album":
        try:
            trks = item.tracks()
            if trks:
                tr = trks[0]
                if getattr(tr, "locations", None):
                    p = Path(tr.locations[0])
                else:
                    p = Path(tr.media[0].parts[0].file)
        except Exception:
            p = None

    if p is None:
        raise RuntimeError(f"Could not determine filesystem location for: {getattr(item, 'title', 'item')}")

    p = map_path(p)

    if p.suffix.lower() in VIDEO_EXTS:
        return p.parent

    try:
        if p.is_file():
            return p.parent
    except Exception:
        pass

    return p

def save_item(item, poster=False, art=False):
    save_path = _media_dir_from_item(item)

    is_season = getattr(item, "type", None) == "season"

    if poster and getattr(item, "posterUrl", None):
        base = _season_poster_basename(item) if is_season else "poster"
        _save_asset(
            item,
            item.posterUrl,
            save_path,
            base=base,
            out_format=OUTPUT_FORMAT,
            display_name="poster"
        )

    if art:
        if is_season:
            show = getattr(item, "show", None)() if callable(getattr(item, "show", None)) else getattr(item, "show", None)
            show_art = getattr(show, "artUrl", None) if show else None
            art_url = show_art or getattr(item, "artUrl", None)

            if art_url:
                show_dir = save_path.parent
                _save_asset(
                    item,
                    art_url,
                    show_dir,
                    base="background",
                    out_format=OUTPUT_FORMAT,
                    display_name="background"
                )
        else:
            if getattr(item, "artUrl", None):
                _save_asset(
                    item,
                    item.artUrl,
                    save_path,
                    base="background",
                    out_format=OUTPUT_FORMAT,
                    display_name="background"
                )

def run_gui():
    try:
        from PySide6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox,
            QTextEdit, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
            QListWidget, QListWidgetItem
        )
        from PySide6.QtCore import Qt

    except ImportError:
        print("PySide6 is not installed. Install it with 'pip install PySide6' to use the GUI.")
        sys.exit(1)

    class ConfigDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Plex Config")

            self.url_edit = QLineEdit(PLEX_URL)
            self.token_edit = QLineEdit(PLEX_TOKEN)
            self.token_edit.setEchoMode(QLineEdit.Password)

            self.format_combo = QComboBox()
            self.format_combo.addItems(["jpg", "png"])
            self.format_combo.setCurrentText(OUTPUT_FORMAT)

            self.overwrite_cb = QCheckBox("Overwrite existing images")
            self.overwrite_cb.setChecked(OVERWRITE)

            self.map_list = QListWidget()
            if "MAPPED_FOLDERS" in CONFIG:
                for host, container in CONFIG["MAPPED_FOLDERS"].items():
                    item = QListWidgetItem(f"{host}  →  {container}")
                    item.setData(Qt.UserRole, (host, container))
                    self.map_list.addItem(item)

            self.host_edit = QLineEdit()
            self.container_edit = QLineEdit()

            self.add_btn = QPushButton("Add / Update")
            self.remove_btn = QPushButton("Remove selected")

            self.add_btn.clicked.connect(self.on_add_mapping)
            self.remove_btn.clicked.connect(self.on_remove_mapping)
            self.map_list.itemSelectionChanged.connect(self.on_selection_changed)

            form = QFormLayout()
            form.addRow("Server URL:", self.url_edit)
            form.addRow("Token:", self.token_edit)
            form.addRow("Output format:", self.format_combo)
            form.addRow("Overwrite:", self.overwrite_cb)
            form.addRow("Mapped folders:", self.map_list)
            form.addRow("Host path:", self.host_edit)
            form.addRow("Container path:", self.container_edit)

            buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)

            btn_row = QHBoxLayout()
            btn_row.addWidget(self.add_btn)
            btn_row.addWidget(self.remove_btn)

            layout = QVBoxLayout()
            layout.addLayout(form)
            layout.addLayout(btn_row)
            layout.addWidget(buttons)
            self.setLayout(layout)

        def on_selection_changed(self):
            item = self.map_list.currentItem()
            if not item:
                return
            host, container = item.data(Qt.UserRole)
            self.host_edit.setText(host)
            self.container_edit.setText(container)

        def on_add_mapping(self):
            host = self.host_edit.text().strip()
            container = self.container_edit.text().strip()

            if not host or not container:
                QMessageBox.warning(self, "Missing values", "Please enter both host and container paths.")
                return

            existing = None
            for i in range(self.map_list.count()):
                it = self.map_list.item(i)
                h, c = it.data(Qt.UserRole)
                if h == host:
                    existing = it
                    break

            text = f"{host}  →  {container}"
            if existing is None:
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, (host, container))
                self.map_list.addItem(item)
            else:
                existing.setText(text)
                existing.setData(Qt.UserRole, (host, container))

            self.host_edit.clear()
            self.container_edit.clear()

        def on_remove_mapping(self):
            row = self.map_list.currentRow()
            if row >= 0:
                self.map_list.takeItem(row)

        def accept(self):
            global CONFIG, PLEX_URL, PLEX_TOKEN, OUTPUT_FORMAT, OVERWRITE, MAPPED_FOLDERS, _MAPPED_FOLDERS

            url = self.url_edit.text().strip()
            token = self.token_edit.text().strip()
            format_value = self.format_combo.currentText().lower()
            overwrite_value = "true" if self.overwrite_cb.isChecked() else "false"

            if not url:
                QMessageBox.warning(self, "Missing URL", "Please enter a Plex server URL.")
                return

            CONFIG["PLEX"]["url"] = url
            CONFIG["PLEX"]["token"] = token
            CONFIG["PLEX"]["output_format"] = format_value
            CONFIG["PLEX"]["overwrite"] = overwrite_value

            if "MAPPED_FOLDERS" not in CONFIG:
                CONFIG["MAPPED_FOLDERS"] = {}

            CONFIG["MAPPED_FOLDERS"].clear()
            for i in range(self.map_list.count()):
                item = self.map_list.item(i)
                host, container = item.data(Qt.UserRole)
                CONFIG["MAPPED_FOLDERS"][host] = container

            save_config(CONFIG)

            PLEX_URL = url
            PLEX_TOKEN = token
            OUTPUT_FORMAT = format_value
            OVERWRITE = (overwrite_value == "true")

            MAPPED_FOLDERS = {}
            if "MAPPED_FOLDERS" in CONFIG:
                for host, container in CONFIG["MAPPED_FOLDERS"].items():
                    MAPPED_FOLDERS[Path(host)] = Path(container)
            _MAPPED_FOLDERS = MAPPED_FOLDERS

            super().accept()

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Save Plex Posters")
            self.resize(600, 400)

            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QVBoxLayout(central)

            mode_layout = QHBoxLayout()
            mode_layout.addWidget(QLabel("Mode:"))
            self.mode_combo = QComboBox()
            self.mode_combo.addItems(["Title search", "Library sweep"])
            mode_layout.addWidget(self.mode_combo)
            main_layout.addLayout(mode_layout)

            title_layout = QHBoxLayout()
            title_layout.addWidget(QLabel("Title:"))
            self.title_edit = QLineEdit()
            title_layout.addWidget(self.title_edit)
            main_layout.addLayout(title_layout)

            lib_layout = QHBoxLayout()
            lib_layout.addWidget(QLabel("Library:"))
            self.library_edit = QLineEdit()
            lib_layout.addWidget(self.library_edit)
            main_layout.addLayout(lib_layout)

            type_layout = QHBoxLayout()
            type_layout.addWidget(QLabel("Type:"))
            self.type_combo = QComboBox()
            self.type_combo.addItem("Any", userData=None)
            self.type_combo.addItem("movie", userData="movie")
            self.type_combo.addItem("show", userData="show")
            self.type_combo.addItem("season", userData="season")
            type_layout.addWidget(self.type_combo)
            main_layout.addLayout(type_layout)

            opts_layout = QHBoxLayout()
            self.poster_cb = QCheckBox("Poster")
            self.poster_cb.setChecked(True)
            self.art_cb = QCheckBox("Background")
            self.season_cb = QCheckBox("Seasons")
            self.season_art_cb = QCheckBox("Season backgrounds")
            opts_layout.addWidget(self.poster_cb)
            opts_layout.addWidget(self.art_cb)
            opts_layout.addWidget(self.season_cb)
            opts_layout.addWidget(self.season_art_cb)
            main_layout.addLayout(opts_layout)

            btn_layout = QHBoxLayout()
            self.run_btn = QPushButton("Run")
            self.config_btn = QPushButton("Config…")
            btn_layout.addWidget(self.run_btn)
            btn_layout.addWidget(self.config_btn)
            main_layout.addLayout(btn_layout)

            self.log = QTextEdit()
            self.log.setReadOnly(True)
            main_layout.addWidget(self.log)

            self.run_btn.clicked.connect(self.on_run)
            self.config_btn.clicked.connect(self.on_config)

        def append_log(self, text: str):
            self.log.append(text)
            print(text)

        def on_config(self):
            dlg = ConfigDialog(self)
            if dlg.exec():
                self.append_log("Updated Plex config and saved to config.ini.")

        def on_run(self):
            mode = self.mode_combo.currentText()
            title = self.title_edit.text().strip()
            library = self.library_edit.text().strip() or None
            libtype = self.type_combo.currentData()

            if not PLEX_URL or not PLEX_TOKEN:
                QMessageBox.warning(self, "Missing config",
                                    "Please set Plex URL and token in the Config dialog first.")
                return

            try:
                plex = PlexServer(PLEX_URL, PLEX_TOKEN)
            except Exception as e:
                QMessageBox.critical(self, "Plex error", f"Failed to connect to Plex:\n{e}")
                return

            poster = self.poster_cb.isChecked()
            art = self.art_cb.isChecked()
            season = self.season_cb.isChecked()
            season_art = self.season_art_cb.isChecked()

            if not (poster or art):
                QMessageBox.warning(self, "Nothing to do",
                                    "Please select at least Poster or Background.")
                return

            if mode == "Title search":
                if not title:
                    QMessageBox.warning(self, "Missing title", "Please enter a title.")
                    return
                self.run_title_mode(plex, title, library, libtype, poster, art, season, season_art)
            else:
                if not library:
                    QMessageBox.warning(self, "Missing library", "Please enter a library name.")
                    return
                self.run_library_mode(plex, library, libtype, poster, art)

        def run_title_mode(self, plex, title, library, libtype, poster, art, season, season_art):
            results = _search_by_title(plex, title, library=library, libtype=libtype)
            if not results:
                QMessageBox.information(self, "No results", "No items found for that query.")
                return

            if len(results) > 1:
                from PySide6.QtWidgets import QInputDialog
                items_str = [_describe_item_for_pick(it) for it in results]
                choice, ok = QInputDialog.getItem(
                    self,
                    "Choose item",
                    "Multiple matches found:",
                    items_str,
                    0,
                    False
                )
                if not ok:
                    return
                idx = items_str.index(choice)
                chosen = results[idx]
            else:
                chosen = results[0]

            self.append_log(f"Selected: {_describe_item_for_pick(chosen)}")

            try:
                if season:
                    if getattr(chosen, "type", None) == "show":
                        if poster or art:
                            self.append_log("Saving show-level assets…")
                            save_item(chosen, poster=poster, art=art)

                        seasons = chosen.seasons()
                        if not seasons:
                            self.append_log("No seasons found for this show.")
                            return

                        for s in seasons:
                            self.append_log(f"Saving season: {_describe_item_for_pick(s)}")
                            save_item(s, poster=True, art=bool(season_art))
                        self.append_log("Done.")
                        return

                    if getattr(chosen, "type", None) == "season":
                        show = chosen.show() if callable(getattr(chosen, "show", None)) else getattr(chosen, "show", None)
                        if show and (poster or art):
                            self.append_log("Saving show-level assets…")
                            save_item(show, poster=poster, art=art)

                        self.append_log("Saving season assets…")
                        save_item(chosen, poster=True, art=bool(season_art))
                        self.append_log("Done.")
                        return

                    QMessageBox.information(
                        self,
                        "Invalid selection",
                        "The selected item isn't a show or season. Disable 'Seasons' or pick a show/season."
                    )
                    return

                self.append_log("Saving assets…")
                save_item(chosen, poster=poster, art=art)
                self.append_log("Done.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")

        def run_library_mode(self, plex, library, libtype, poster, art):
            try:
                section = plex.library.section(library)
            except Exception as e:
                QMessageBox.critical(self, "Library error", f"Could not open library '{library}':\n{e}")
                return

            self.append_log(f"Processing library '{library}'…")
            try:
                for item in section.all(libtype=libtype, includeGuids=False):
                    self.append_log(f"Saving assets for: {_describe_item_for_pick(item)}")
                    save_item(item, poster=poster, art=art)
                self.append_log("Library processing complete.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rating_key", type=int, help="Fetch a single item by rating key.")
    parser.add_argument(
        "--title",
        nargs="?",
        const="__PROMPT__",
        help="Search by title (optional value). If omitted, you will be prompted.",
    )
    parser.add_argument(
        "--library",
        help="Limit search or library sweep to a specific library section.",
    )
    parser.add_argument(
        "--libtype",
        choices=["movie", "show", "season"],
        help="Limit to a specific media type.",
    )
    parser.add_argument("--poster", action="store_true", help="Save poster.")
    parser.add_argument("--art", action="store_true", help="Save background art.")
    parser.add_argument(
        "--season",
        action="store_true",
        help=(
            "When used with --title, fetch season posters for that show; "
            "when processing season items, names poster as 'season NN.ext'."
        ),
    )
    parser.add_argument(
        "--season_art",
        action="store_true",
        help="Also save backgrounds for each season (off by default).",
    )
    parser.add_argument(
        "--format",
        choices=["jpg", "png"],
        help="Override output format for this run.",
    )
    parser.add_argument(
        "--overwrite",
        choices=["true", "false"],
        help="Override overwrite policy for this run.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the simple GUI instead of using CLI.",
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Create a default config.ini and exit.",
    )

    opts = parser.parse_args()

    if opts.config:
        if CONFIG_PATH.exists():
            print(f"Config file already exists at: {CONFIG_PATH}")
        else:
            print("Creating default config.ini ...")
            cfg = configparser.ConfigParser()
            cfg["PLEX"] = {
                "url": "http://127.0.0.1:32400",
                "token": "",
                "output_format": "jpg",
                "overwrite": "false",
            }
            # You can leave this empty, or pre-populate with your mappings
            cfg["MAPPED_FOLDERS"] = {
                r"\\TOWER\Media\movies": "/data/movies",
                r"\\TOWER\Media\tv": "/data/tv",
            }
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                cfg.write(f)
            print(f"Config file created at: {CONFIG_PATH}")
        sys.exit(0)

    if opts.gui:
        run_gui()
        sys.exit(0)

    if opts.format:
        OUTPUT_FORMAT = opts.format
    if opts.overwrite:
        OVERWRITE = (opts.overwrite.lower() == "true")

    if not PLEX_URL or not PLEX_TOKEN:
        print("Plex URL or token not set. Run with --gui and use Config, or edit config.ini.")
        sys.exit(1)

    plex = PlexServer(PLEX_URL, PLEX_TOKEN)

    if opts.rating_key:
        item = plex.fetchItem(opts.rating_key)
        save_item(item, opts.poster, opts.art)

    elif opts.title is not None:
        if opts.title == "__PROMPT__":
            title = input("Enter title to search: ").strip()
            if not title:
                print("No title entered. Exiting.")
                sys.exit(0)
        else:
            title = opts.title

        results = _search_by_title(plex, title, library=opts.library, libtype=opts.libtype)
        chosen = _pick_one_cli(results)
        if chosen is None:
            sys.exit(0)

        if opts.season:
            if getattr(chosen, "type", None) == "show":
                if opts.poster or opts.art:
                    save_item(chosen, poster=opts.poster, art=opts.art)

                seasons = chosen.seasons()
                if not seasons:
                    print("No seasons found for this show.")
                    sys.exit(0)

                for s in seasons:
                    save_item(s, poster=True, art=bool(getattr(opts, "season_art", False)))
                sys.exit(0)

            if getattr(chosen, "type", None) == "season":
                show = chosen.show() if callable(getattr(chosen, "show", None)) else getattr(chosen, "show", None)
                if show and (opts.poster or opts.art):
                    save_item(show, poster=opts.poster, art=opts.art)

                save_item(chosen, poster=True, art=bool(getattr(opts, "season_art", False)))
                sys.exit(0)

            print("The selected item isn't a show or season. Use --title to pick the show, then add --season.")
            sys.exit(0)

        save_item(chosen, opts.poster, opts.art)

    elif opts.library:
        library = plex.library.section(opts.library)
        save_library(library, opts.libtype, opts.poster, opts.art)

    else:

        print("No --rating_key, --title, or --library specified. Exiting.")
