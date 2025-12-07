# **Poster Save**

A lightweight tool for Plex users who want full control over their media artwork.
It automatically downloads **posters**, **backgrounds**, and **season artwork** directly from your Plex server and saves them next to your media files in a clean, consistent format that Plex, Jellyfin, and Emby can all recognize.

Save Poster works in **two modes**:

* A **simple GUI** for everyday use
* A **powerful CLI** for automation, scripting, and batch processing

Whether you want to update a single movie’s poster or refresh artwork for your entire library, Poster Save gives you a fast, reliable, and fully configurable workflow.

---

Save Poster connects to your Plex Media Server using your Plex URL and authentication token, then retrieves high-resolution artwork for movies, TV shows, seasons, artists, and albums. It saves all artwork directly inside each media folder using standardized filenames such as `poster.jpg`, `background.jpg`, and `season 01.jpg`.

The tool supports:

* **Title search**
  Search Plex by name and select the exact match to download artwork for a single item.

* **Library sweeps**
  Automatically walk through an entire library (e.g., *Movies*, *TV Shows*) and save artwork for every item.

* **Season extraction**
  Grab poster images for every season of a TV show, with optional background art for the show itself.

* **Multiple formats**
  Save artwork as either **JPG** or **PNG**, with overwrite rules controlled via the config file.

* **Docker host-path mapping**
  Automatically converts container paths into real filesystem paths, ensuring correct saving in Unraid, Docker, or bare-metal installations.

The project includes a built-in configuration system (`config.ini`) and a clean PySide6 GUI that allows users to update server settings, choose their download mode, and monitor activity through a real-time log window. For advanced or automated workflows, the full CLI remains available with support for flags such as `--title`, `--library`, `--season`, and `--rating_key`.

Save Poster is designed to be simple, predictable, and fast—making it ideal for Plex power-users, metadata collectors, archivists, and anyone who wants their media library artwork stored locally and under their control.

---

# **Usage**

A tool for downloading **posters**, **backgrounds**, and **season artwork** directly from your Plex server and saving them next to your media files.

Supports **CLI** (terminal) and a **GUI**.

---

# **Installation**

### 1. Install dependencies

```bash
pip install plexapi requests pillow pyside6
```

---

# **Configuration (Required)**

Before running anything, you must set:

* **Plex Server URL**
  Example: `http://192.168.1.50:32400`

* **Plex Token**
  (You can obtain this by viewing Plex logs or using browser tools.)

### Two ways to set config:

---

## **Method A — Use the GUI**

```bash
python poster_save.py --gui
```

1. Click **Config…**
2. Enter your **Server URL** and **Token**
3. Click **Save**

The script writes these into `config.ini`.

---

## **Method B — Use the CLI**

Run `--config` to create the confi.ini file:

```bash
python poster_save.py --config
```

fill in:

```ini
[PLEX]
url = http://your-ip:32400
token = your-token-here
output_format = jpg
overwrite = false
```

---

# **GUI Mode**

Launch the visual interface:

```bash
python poster_save.py --gui
```

The GUI contains:

---

## **Mode**

### **Title search**

Search Plex by name.
Example: enter **"Pluribus"**, choose the matching show or movie.

### **Library sweep**

Process every item in an entire Plex library (Movies, TV Shows, etc.)

---

## **Title**

Used with **Title search**.
Enter the name of a movie/show/season/album.

---

## **Library**

Used for:

* **Title search** -> optional filter
* **Library sweep** -> required

Examples:
`Movies`, `TV Shows`, `Anime`, etc.

---

## **Type**

Limits what Plex returns:

* Any
* movie
* show
* season

---

## **Artwork Options**

### Poster

Downloads the main poster (`poster.jpg/png`).

### Background

Downloads the background / backdrop image (`background.jpg/png`).

### Seasons

If the selected item is a TV show:
-> Downloads posters for **every season** (`season 01.jpg`, etc.)

If you select a season:
-> Downloads only that season’s poster.

### Season backgrounds

Downloads the **show-level** background once and saves it for season mode.
(*Plex does not provide per-season backgrounds.*)

---

## Buttons

### **Run**

Starts processing with your selected options.

### **Config...**

Opens the config window to set:

* Plex URL
* Plex Token

### **Log Window**

Shows progress:

* What’s being downloaded
* Where files are saved
* Errors or skipped items

---

# **CLI Mode**

The script can be used fully from the terminal.

---

## **CLI Syntax**

```
python poster_save.py [options]
```

If `--gui` is NOT provided, script automatically runs in CLI mode.

---

# **Common CLI Examples**

---

## 1. **1️Download poster + background for a movie**

```bash
python poster_save.py --title "Pluribus" --libtype movie --poster --art
```

---

## 2. **Prompt for title interactively**

```bash
python poster_save.py --title --poster --art
```

If you omit the title, it asks:

```
Enter title to search:
```

---

## 3. **Download artwork for all movies in a library**

```bash
python poster_save.py --library "Movies" --libtype movie --poster --art
```

---

## 4. **Save poster/background for a TV show + all its seasons**

```bash
python poster_save.py --title "Breaking Bad" --poster --art --season --season_art
```

---

## 5. **Download based on Plex rating key**

```bash
python poster_save.py --rating_key 12345 --poster --art
```

---

## 6. **Override output format (config is default)**

```bash
python poster_save.py --title "Pluribus" --format png
```

---

## 7. **Override overwrite behavior temporarily**

```bash
python poster_save.py --title "Pluribus" --overwrite true
```

---

# **CLI Options Overview**

| Flag           | Description                           |
| -------------- | ------------------------------------- |
| `--gui`        | Launch the GUI                        |
| `--title`      | Search Plex by title                  |
| `--rating_key` | Fetch an item directly                |
| `--library`    | Specify a library for search or sweep |
| `--libtype`    | Filter by type (movie, show, etc.)    |
| `--poster`     | Save poster image                     |
| `--art`        | Save background image                 |
| `--season`     | Auto-download season posters          |
| `--season_art` | Auto-download season backgrounds      |
| `--format`     | Override output format (jpg/png)      |
| `--overwrite`  | Override overwrite (true/false)       |

The script always loads your Plex **URL**, **token**, and default settings from:

```
config.ini
```

---

# **Where Images Are Saved**

Images are stored **next to the media files** on your system.

Examples:

### Movie:

```
Movie Folder/
 ├─ poster.jpg
 └─ background.jpg
```

### TV Show:

```
Show Folder/
 ├─ poster.jpg
 ├─ background.jpg
 ├─ Season 01/
 │   └─ season 01.jpg
 └─ Season 02/
     └─ season 02.jpg
```
