from langchain_core.tools import tool
from typing import Optional
import requests

import os
from dotenv import load_dotenv
load_dotenv()

# Make sure this is your EXACT active Render URL
movie_url = os.getenv("movie_URL")
TIMEOUT = 60


def _handle_response(res: requests.Response) -> str:
    """Shared response formatting so every tool below returns errors the same way."""
    if not res.ok:
        return (
            "Movie Booking API Error\n"
            f"Status Code: {res.status_code}\n"
            f"Response: {res.text}"
        )
    return res.text


def _handle_error(e: requests.exceptions.RequestException) -> str:
    return f"Movie Booking API connection error: {e}"


# ============================================================
# MOVIES
# ============================================================

@tool
def list_movies() -> str:
    """List every movie currently available for booking."""
    try:
        res = requests.get(f"{movie_url}/movies", timeout=TIMEOUT)
        return _handle_response(res)
    except requests.exceptions.RequestException as e:
        return _handle_error(e)


@tool
def get_movies_by_language(language: str) -> str:
    """List movies available in a specific language.

    Args:
        language: The language to filter movies by, e.g. "Telugu", "English", "Hindi".
    """
    try:
        res = requests.get(f"{movie_url}/movies/language/{language}", timeout=TIMEOUT)
        return _handle_response(res)
    except requests.exceptions.RequestException as e:
        return _handle_error(e)


@tool
def get_movie(movie_id: int) -> str:
    """Get full details for a single movie by its ID.

    Args:
        movie_id: The ID of the movie to look up.
    """
    try:
        res = requests.get(f"{movie_url}/movies/{movie_id}", timeout=TIMEOUT)
        return _handle_response(res)
    except requests.exceptions.RequestException as e:
        return _handle_error(e)


@tool
def add_movie(
    title: Optional[str] = None,
    movie_name: Optional[str] = None,
    Movie_name: Optional[str] = None,
    theatre: Optional[str] = None,
    theatre_name: Optional[str] = None,
    Theatre_name: Optional[str] = None,
    language: Optional[str] = "Telugu",
    ticket_price: int = 200,
    total_seats: int = 100,
) -> str:
    """Add a new movie to the Movie Booking system.

    Args:
        title: The movie's title. Required.
        movie_name: Alternative title parameter. Optional.
        Movie_name: Capitalized title parameter. Optional.
        theatre: The theatre showing the movie. Required.
        theatre_name: Alternative theatre parameter. Optional.
        Theatre_name: Capitalized theatre parameter. Optional.
        language: The movie's language. Optional.
        ticket_price: Ticket price as an integer. Defaults to 200.
        total_seats: Total seats available as an integer. Defaults to 100.
    """
    final_title = title or movie_name or Movie_name
    final_theatre = theatre or theatre_name or Theatre_name
    
    if not final_title or not final_theatre:
        return "Please provide both the movie title and the theatre name."

    payload = {
        "Movie_name": str(final_title).strip(),
        "Theatre_name": str(final_theatre).strip(),
        "Language": str(language or "Telugu").strip(),
        "Ticket_price": int(ticket_price),
        "Total_seats": int(total_seats),
    }
    
    try:
        res = requests.post(f"{movie_url}/movies", json=payload, timeout=TIMEOUT)
        return _handle_response(res)
    except requests.exceptions.RequestException as e:
        return _handle_error(e)


@tool
def update_movie(
    movie_id: int,
    title: Optional[str] = None,
    language: Optional[str] = None,
    genre: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    price: Optional[float] = None,
    total_seats: Optional[int] = None,
) -> str:
    """Update an existing movie's details.

    Only include the fields that should change; anything left as None is skipped.

    Args:
        movie_id: The ID of the movie to update. Required.
        title: New title for the movie. Optional.
        language: New language for the movie. Optional.
        genre: New genre for the movie. Optional.
        duration_minutes: New runtime in minutes. Optional.
        price: New ticket price. Optional.
        total_seats: New total seat count. Optional.
    """
    payload = {
        k: v
        for k, v in {
            "title": title,
            "language": language,
            "genre": genre,
            "duration_minutes": duration_minutes,
            "price": price,
            "total_seats": total_seats,
        }.items()
        if v is not None
    }
    if not payload:
        return "No fields provided to update. Specify at least one field to change."
    try:
        res = requests.put(f"{movie_url}/movies/{movie_id}", json=payload, timeout=TIMEOUT)
        return _handle_response(res)
    except requests.exceptions.RequestException as e:
        return _handle_error(e)


@tool
def delete_movie(movie_id: int) -> str:
    """Delete a movie from the Movie Booking system.

    Args:
        movie_id: The ID of the movie to delete.
    """
    try:
        res = requests.delete(f"{movie_url}/movies/{movie_id}", timeout=TIMEOUT)
        return _handle_response(res)
    except requests.exceptions.RequestException as e:
        return _handle_error(e)


@tool
def get_seat_count(movie_id: int) -> str:
    """Get the number of seats remaining/available for a movie.

    Args:
        movie_id: The ID of the movie to check seat availability for.
    """
    try:
        res = requests.get(f"{movie_url}/movies/{movie_id}/seats", timeout=TIMEOUT)
        return _handle_response(res)
    except requests.exceptions.RequestException as e:
        return _handle_error(e)


# ============================================================
# BOOKINGS
# ============================================================

@tool
def book_tickets(title: str, seats: int = 1, language: str = "Telugu") -> str:
    """Books movie tickets. Pass the title of the movie, seats count, and language."""
    try:
        # 1. Fetch the list of movies to ensure it exists and grab metadata if needed
        res = requests.get(f"{movie_url}/movies", timeout=60)
        if not res.ok:
            return _handle_response(res)
            
        movies = res.json()
        
        # Optional: Verify movie exists against the list
        matched_movie_name = title
        found = False
        for m in movies:
            m_safe = {str(k).lower().strip(): v for k, v in m.items()}
            db_title = str(m_safe.get("title") or m_safe.get("movie_name") or m_safe.get("name") or "")
            if db_title.strip().lower() == title.strip().lower():
                matched_movie_name = db_title
                language = m_safe.get("language", language)
                found = True
                break
                
        if not found:
            return f"Could not find a movie named '{title}' in the system."

        # 2. Make the booking with the exact keys your Render backend's Pydantic schema demands
        payload = {
            "movie_name": matched_movie_name,
            "seats_to_book": seats,
            "language": language
        }
        
        book_res = requests.post(
            f"{movie_url}/bookings", 
            json=payload, 
            timeout=60
        )
        return _handle_response(book_res)
        
    except requests.exceptions.RequestException as e:
        return f"Movie booking service is unreachable. ({e})"
    except Exception as e:
        return f"An error occurred: {e}"


@tool
def get_booking(booking_id: int) -> str:
    """Get details for a single booking by its ID.

    Args:
        booking_id: The ID of the booking to look up.
    """
    try:
        res = requests.get(f"{movie_url}/bookings/{booking_id}", timeout=TIMEOUT)
        return _handle_response(res)
    except requests.exceptions.RequestException as e:
        return _handle_error(e)


@tool
def cancel_booking(booking_id: int) -> str:
    """Cancel an existing booking.

    Args:
        booking_id: The ID of the booking to cancel.
    """
    try:
        res = requests.delete(f"{movie_url}/bookings/{booking_id}", timeout=TIMEOUT)
        return _handle_response(res)
    except requests.exceptions.RequestException as e:
        return _handle_error(e)