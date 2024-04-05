# My Configs for Plex-Meta-Manager


![Trending](https://user-images.githubusercontent.com/28127566/233728814-d6743ed2-990f-4efe-a7f2-13f8be38e5d3.png)

```yaml
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
  Trending:
    overlay:
      name: Trending
      url_poster: https://raw.githubusercontent.com/Entree3k/Plex/main/Plex%20Meta%20Manager%20Configs/Overlays/images/Trending.png
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

![Networks](https://user-images.githubusercontent.com/28127566/233728875-6f5560be-18a6-407c-bc26-cf94472d64f3.png)

![4k](https://user-images.githubusercontent.com/28127566/233728910-b5bbd5d0-d079-4519-81eb-d2af4a0678e9.png)

```yaml
  4K:
    overlay:
      name: 4K
      url_poster: https://raw.githubusercontent.com/Entree3k/Plex/main/Plex%20Meta%20Manager%20Configs/Overlays/images/4K.png
    plex_search:
      all:
        resolution: 4K
```
