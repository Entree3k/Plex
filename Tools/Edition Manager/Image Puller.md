# [Image Puller](https://github.com/Entree3k/Image-Puller)

Plex Artwork Downloader is a Python tool that retrieves and downloads artwork (posters, backgrounds) from a Plex server. It is a read-only tool that does not modify your Plex library, ensuring a safe way to backup and organize your media artwork.

## Features
- Connects to a Plex server using a URL and authentication token.
- Downloads artwork for movies and TV shows from specified Plex libraries.
- Supports multi-threaded downloading for efficiency.
- Saves artwork in an organized folder structure.
- Logs successful and failed downloads with error reporting.

## Requirements
- Python 3.x
- Plex server with a valid authentication token
- Required Python dependencies (install with `pip install -r requirements.txt`)

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/plex-artwork-downloader.git
   cd plex-artwork-downloader
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the `config.yml` file:
   ```yaml
   # Plex server configuration
   plex_url: 'YOUR_PLEX_SERVER_URL'
   plex_token: 'YOUR_PLEX_AUTH_TOKEN'

   # Output directory for downloaded artwork
   output_directory: 'output'

   # Number of concurrent download threads
   download_threads: 4

   # Library sections to process
   libraries:
     movies:
       - 'Movies'
     tv_shows:
       - 'TV Shows'

   # Logging configuration
   logging:
     level: 'INFO'
     file: 'plex_artwork.log'
   ```

## Usage

### Running the Script
To start downloading artwork, run:
```bash
python plex-poster-script.py
```

### What Happens During Execution?
- The script connects to your Plex server using the provided URL and token.
- It scans the specified **Movies** and **TV Shows** libraries.
- It downloads:
  - **Posters** (`poster.jpg`) for movies, TV shows, and seasons.
  - **Background images** (`background.jpg`) for movies and TV shows.
- All images are saved in the `output/` directory.
- Failed downloads are logged in `failed_downloads.log`.

### Output Directory Structure
The artwork is saved in an organized format:

```
output/
│── Movies/
│   ├── Movie Title (Year)/
│   │   ├── poster.jpg
│   │   ├── background.jpg
│
│── TV Shows/
│   ├── Show Title (Year)/
│   │   ├── poster.jpg
│   │   ├── background.jpg
│   │   ├── Season 01/
│   │   │   ├── Season01.jpg
│   │   ├── Season 02/
│   │   │   ├── Season02.jpg
```

## Troubleshooting
- **Invalid Plex URL or token**: Ensure your `plex_url` and `plex_token` are correct in `config.yml`.
- **No artwork is being downloaded**: Verify that your Plex server is accessible and the libraries exist.
- **Failed downloads**: Check `failed_downloads.log` for details.

## License
This project is licensed under the MIT License.

## Contributing
Feel free to submit pull requests or open issues to improve this project.

---

