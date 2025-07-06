from fastapi import HTTPException
from entities.album import Rating, Album
from database.core import DbSession
from auth.service import CurrentUser
from .model import RatingDeleteRequest, RatingResponse, RatingCreateRequest, RatingUpdateRequest, AlbumInfoResponse, AlbumInfoCreateRequest
from .utils import get_album_info
from utils.current_user_utils import get_current_db_user
from messages.error_messages import RATING_ALREADY_EXISTS, ALBUM_CREATION_FAILED, USER_NOT_FOUND, RATING_NOT_FOUND, RATINGS_NOT_FOUND, ALBUM_NOT_FOUND, RATING_CREATION_FAILED, ALBUM_ALREADY_EXISTS
from messages.success_messages import ALBUM_DATABASE_INSERTION_SUCCESS, ALL_RATINGS_DELETION_SUCCESS, RATING_CREATION_SUCCESS, RATING_DELETION_SUCCESS, RATING_UPDATE_SUCCESS
from sqlalchemy import func
import logging
import dotenv
import os

# Load environment variables
dotenv.load_dotenv()
STRING_SIMILARITY_THRESHOLD = float(
    os.getenv("STRING_SIMILARITY_THRESHOLD", "0.8"))


def get_ratings(db: DbSession, current_user: CurrentUser):
    ''' Retrieve all ratings for the current user from the database '''
    logging.info('Retrieving ratings for the current user')

    db_user = get_current_db_user(db, current_user)
    user_id = db_user.id

    if not db_user:
        logging.error(USER_NOT_FOUND)
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND)

    ratings_db = db.query(Rating).filter(Rating.user_id == user_id).all()
    if not ratings_db:
        logging.error(RATINGS_NOT_FOUND)
        raise HTTPException(status_code=404, detail=RATINGS_NOT_FOUND)

    ratings = []

    for rating_db in ratings_db:
        album_db = db.query(Album).filter(
            Album.id == rating_db.album_id).first()

        if not album_db:
            logging.error(ALBUM_NOT_FOUND)
            raise HTTPException(status_code=404, detail=ALBUM_NOT_FOUND)

        rating = RatingResponse(
            title=album_db.title,
            artist=album_db.artist,
            release_date=album_db.release_date,
            genre=album_db.genre,
            image_url=album_db.image_url,
            created_at=rating_db.created_at,
            rating=rating_db.rating
        )
        ratings.append(rating)

    logging.info(f'Current user has {len(ratings)} ratings')
    return ratings


def search_album(artist_name: str, album_name: str, db: DbSession) -> AlbumInfoResponse:
    ''' Search for an album by artist and album name in the database or external API '''
    logging.info(f'Searching for album: {album_name} by artist: {artist_name}')
    # Check if the album already exists in the database
    album_db = verify_album_exists(artist_name, album_name, db)

    # If the album is found in the database, return its information
    if album_db:
        logging.info(
            f'Album found in database: {album_db.title} by {album_db.artist}')
        return AlbumInfoResponse(
            album_id=album_db.id,
            title=album_db.title,
            artist=album_db.artist,
            release_date=album_db.release_date,
            genre=album_db.genre,
            image_url=album_db.image_url
        )
    # If not found in the database, search using external API
    else:
        logging.info(
            f'Album not found in database, fetching from external API: {album_name} by {artist_name}')
        album_info = get_album_info(artist_name, album_name)
        db_album = create_album(album_info, db)

        return AlbumInfoResponse(
            album_id=db_album.id,
            title=album_info.title,
            artist=album_info.artist,
            release_date=album_info.release_date,
            genre=album_info.genre,
            image_url=album_info.image_url
        )


def create_album(album_info: AlbumInfoCreateRequest, db: DbSession):
    ''' Create a new album in the database '''
    logging.info(
        f'Inserting album: {album_info.title} by {album_info.artist} into the database')
    new_album = Album(
        title=album_info.title,
        artist=album_info.artist,
        release_date=album_info.release_date,
        genre=album_info.genre,
        image_url=album_info.image_url
    )

    if not new_album:
        logging.error('Failed to create a new album instance')
        raise HTTPException(status_code=500, detail=ALBUM_CREATION_FAILED)

    db.add(new_album)
    db.commit()
    db.refresh(new_album)
    logging.info(ALBUM_DATABASE_INSERTION_SUCCESS)
    return new_album


def verify_album_exists(artist_name: str, album_name: str, db: DbSession):
    ''' Check if an album already exists in the database '''
    db_album = (
        db.query(Album)
        .filter(
            func.similarity(
                Album.artist, artist_name) > STRING_SIMILARITY_THRESHOLD,
            func.similarity(
                Album.title, album_name) > STRING_SIMILARITY_THRESHOLD
        )
        .order_by(
            func.similarity(Album.artist, artist_name) +
            func.similarity(Album.title, album_name)
        )
        .first()
    )

    return db_album


def verify_rating_exists(album_id: int, user_id: int, db: DbSession):
    ''' Check if a rating already exists for the album by the user '''
    rating_db = db.query(Rating).filter(
        Rating.album_id == album_id,
        Rating.user_id == user_id
    ).first()

    return rating_db


def rate_album(rating: RatingCreateRequest, db: DbSession, current_user: CurrentUser):
    # Get the current user from the request context
    db_user = get_current_db_user(db, current_user)
    user_id = db_user.id

    # retrieve album info from external API
    album_info = search_album(rating.artist, rating.title, db)

    if not album_info:
        logging.error(ALBUM_NOT_FOUND)
        raise HTTPException(status_code=404, detail=ALBUM_NOT_FOUND)

    # Check if user already rated this album
    existing_rating = verify_rating_exists(album_info.album_id, user_id, db)

    if existing_rating:
        logging.error(RATING_ALREADY_EXISTS)
        raise HTTPException(status_code=400, detail=RATING_ALREADY_EXISTS)

    # Create a new rating in the database

    new_rating = Rating(
        user_id=user_id,
        album_id=album_info.album_id,
        rating=rating.rating
    )

    if not new_rating:
        logging.error(RATING_CREATION_FAILED)
        raise HTTPException(status_code=500, detail=RATING_CREATION_FAILED)

    # Add row to the database
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    logging.info(RATING_CREATION_SUCCESS)
    # Return the created rating with album info
    return RatingResponse(
        title=album_info.title,
        artist=album_info.artist,
        release_date=album_info.release_date,
        genre=album_info.genre,
        image_url=album_info.image_url,
        created_at=new_rating.created_at,
        rating=new_rating.rating
    )


def delete_rating(rating: RatingDeleteRequest, db: DbSession, current_user: CurrentUser):
    db_user = get_current_db_user(db, current_user)

    db_album = verify_album_exists(rating.artist, rating.title, db)

    if not db_album:
        logging.error(ALBUM_NOT_FOUND)
        raise HTTPException(status_code=500, detail=ALBUM_NOT_FOUND)

    db_rating = verify_rating_exists(db_album.id, db_user.id, db)

    if not db_rating:
        logging.error(RATING_NOT_FOUND)
        raise HTTPException(status_code=404, detail=RATING_NOT_FOUND)

    db.delete(db_rating)
    db.commit()
    logging.info(RATING_DELETION_SUCCESS)
    return {"detail": RATING_DELETION_SUCCESS}


def delete_all_ratings(db: DbSession, current_user: CurrentUser):
    db_user = get_current_db_user(db, current_user)

    ratings_db = db.query(Rating).filter(Rating.user_id == db_user.id).all()
    if not ratings_db:
        raise HTTPException(status_code=404, detail=RATINGS_NOT_FOUND)

    for rating_db in ratings_db:
        db.delete(rating_db)

    db.commit()
    logging.info(ALL_RATINGS_DELETION_SUCCESS)
    return {"detail": ALL_RATINGS_DELETION_SUCCESS}


def change_rating(new_rating: RatingUpdateRequest, db: DbSession, current_user: CurrentUser):
    db_user = get_current_db_user(db, current_user)

    db_album = verify_album_exists(new_rating.artist, new_rating.title, db)

    if not db_album:
        logging.error(ALBUM_NOT_FOUND)
        raise HTTPException(status_code=500, detail=ALBUM_NOT_FOUND)

    db_rating = verify_rating_exists(db_album.id, db_user.id, db)

    if not db_rating:
        raise HTTPException(status_code=404, detail=RATING_NOT_FOUND)

    # Update the rating
    db_rating.rating = new_rating.rating
    db.commit()
    db.refresh(db_rating)

    logging.info(RATING_UPDATE_SUCCESS)
    return RatingResponse(
        title=db_rating.album.title,
        artist=db_rating.album.artist,
        release_date=db_rating.album.release_date,
        genre=db_rating.album.genre,
        image_url=db_rating.album.image_url,
        created_at=db_rating.created_at,
        rating=db_rating.rating
    )
