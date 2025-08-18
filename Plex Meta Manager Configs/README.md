# My Configs for Kometa

<img width="1445" height="1087" alt="show" src="https://github.com/user-attachments/assets/6c9f599a-40e3-42d1-b049-b8eb79e08794" />

```yml
overlays:
  NewSeason:
    overlay:
      name: NewSeason
      file: config/overlays/images/new_season.png
      group: FRESH
      weight: 900
    plex_all: true
    filters:
      added.not: 30              # show wasn't added in the last 30 days
      seasons:
        percentage: 1            # at least one season matches
        added: 21                # that season was added in the last 21 days
        title.not: Specials      # skip Season 00 / Specials
```
```yml
overlays:
  RecentlyAddedShow:
    overlay:
      name: Recently Added
      file: config/overlays/images/recently_added.png
      group: RECENT
      weight: 950
    plex_all: true
    filters:
      added: 7                   # that season was added in the last 7 days
```

<img width="1445" height="1630" alt="show1" src="https://github.com/user-attachments/assets/ddea1582-4d88-44e2-972a-3e71218dac07" />

## Just pick the style you want [here](https://github.com/Entree3k/Plex/tree/main/Plex%20Meta%20Manager%20Configs/Overlays/images/Status)
```yaml
overlays:
  Airing:
    overlay:
      name: airing
      url: https://raw.githubusercontent.com/Entree3k/Plex/refs/heads/main/Plex%20Meta%20Manager%20Configs/Overlays/images/Status/Minimal/airing_minimal.png
      group: STATUS
      weight: 950
    tmdb_on_the_air: 2000

  Returning:
    overlay:
      name: returning
      url: https://raw.githubusercontent.com/Entree3k/Plex/refs/heads/main/Plex%20Meta%20Manager%20Configs/Overlays/images/Status/Minimal/returning_minimal.png
      group: STATUS
      weight: 800
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production

  Ended:
    overlay:
      name: ended
      url: https://raw.githubusercontent.com/Entree3k/Plex/refs/heads/main/Plex%20Meta%20Manager%20Configs/Overlays/images/Status/Minimal/ended_minimal.png
      group: STATUS
      weight: 700
    plex_all: true
    filters:
      tmdb_status: ended

  Canceled:
    overlay:
      name: canceled
      url: https://raw.githubusercontent.com/Entree3k/Plex/refs/heads/main/Plex%20Meta%20Manager%20Configs/Overlays/images/Status/Lower%20Small/canceled_small.png
      group: STATUS
      weight: 600
    plex_all: true
    filters:
      tmdb_status: canceled
```

<img width="1462" height="448" alt="Screenshot 2025-08-18 153953" src="https://github.com/user-attachments/assets/66f360d2-097d-4873-ab9b-7e5230643c97" />

```yaml
collections:
  Trending Movies:
    trakt_chart:
      chart: trending
      limit: 30
    collection_order: custom
    sync_mode: sync
    summary: Movies that are currently Trending
    url_poster: https://raw.githubusercontent.com/Entree3k/Plex/main/Plex%20Meta%20Manager%20Configs/images/trendingshows.jpg
    url_background:
    visible_home: true
    visible_shared: true
    visible_library: true
```

```yaml
overlays:
  Trending:
    overlay:
      name: Trending
      url: https://raw.githubusercontent.com/Entree3k/Plex/refs/heads/main/Plex%20Meta%20Manager%20Configs/Overlays/images/trending.png
    plex_search:
      all:
        collection: Trending Movies
```

![Oscars](https://user-images.githubusercontent.com/28127566/233728846-b0bb434b-08fd-46a7-9ebc-a228a2c33115.png)

```yaml
    Oscars Best Picture Winners:
    sort_title: '*Oscars Best Picture Winners'
    trakt_list: https://trakt.tv/users/pjcob/lists/1970-2021-oscars-best-picture-winners?sort=rank,asc
    summary: The Academy Award for Best Picture is one of the Academy Awards presented annually by the Academy of Motion Picture Arts and Sciences since the awards debuted in 1929.
    url_poster: https://raw.githubusercontent.com/Entree3k/Plex/main/Plex%20Meta%20Manager%20Configs/images/bestpicture.jpg
```

```yaml
   Oscar:
    overlay:
      name: Oscar
      url_poster: https://raw.githubusercontent.com/Entree3k/Plex/main/Plex%20Meta%20Manager%20Configs/Overlays/images/Oscar.png
    plex_search:
      all:
        collection: Oscars Best Picture Winners
```

<img width="1630" height="699" alt="net" src="https://github.com/user-attachments/assets/886df0f9-aa73-4c8e-96b9-6e96c3c89663" />

## Network config [here](https://github.com/Entree3k/Plex/blob/main/Plex%20Meta%20Manager%20Configs/TV%20Shows/Networks.yml)

![4k](https://user-images.githubusercontent.com/28127566/233728910-b5bbd5d0-d079-4519-81eb-d2af4a0678e9.png)

```yaml
overlays:
  4K:
    overlay:
      name: 4K
      url: https://raw.githubusercontent.com/Entree3k/Plex/refs/heads/main/Plex%20Meta%20Manager%20Configs/Overlays/images/4k.png
    plex_search:
      all:
        resolution: 4K
```
