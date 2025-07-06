from fastapi import HTTPException
import dotenv
import os
import discogs_client  # API
from album.model import AlbumInfoCreateRequest
import logging

dotenv.load_dotenv()
APP_NAME = os.getenv("APP_NAME")
APP_VERSION = os.getenv("APP_VERSION")


# Initialize Discogs client
DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN")
if not DISCOGS_TOKEN:
    raise RuntimeError("Missing DISCOGS_TOKEN in environment variables")

client = discogs_client.Client(
    APP_NAME+"/"+APP_VERSION, user_token=DISCOGS_TOKEN)


def get_album_info(artist_name: str, album_name: str) -> AlbumInfoCreateRequest:
    try:
        results = client.search(
            album_name, artist=artist_name, type='release')

        if not results:
            logging.error(
                f'No results found for search: album={album_name}, artist={artist_name}')
            raise HTTPException(status_code=404, detail="Album not found")

        release = results[0].master.main_release

        title = release.title
        artist = ', '.join(a.name for a in release.artists)
        release_date = str(release.year) if release.year else 'Unknown'
        genres = release.genres or release.styles or ['Unknown']
        genre = ', '.join(genres)
        image_url = release.thumb or None

        return AlbumInfoCreateRequest(
            title=title,
            artist=artist,
            release_date=release_date,
            genre=genre,
            image_url=image_url
        )

    except Exception as e:
        logging.error(f'Album search API error: {str(e)}')
        raise HTTPException(
            status_code=500, detail=f"Album search API error: {str(e)}")
