from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.db_connect import get_db

songs = Blueprint('songs', __name__)

@songs.route('/', methods=['GET', 'POST'])
def show_songs():
    db = get_db()
    cursor = db.cursor()

    # Handle POST request to add a new song
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        album = request.form.get('album', '')
        duration = request.form.get('duration', None)
        genre = request.form.get('genre', '')
        release_year = request.form.get('release_year', None)
        spotify_id = request.form.get('spotify_id', '')
        youtube_url = request.form.get('youtube_url', '')

        # Convert empty strings to None for nullable fields
        duration = int(duration) if duration and duration.strip() else None
        release_year = int(release_year) if release_year and release_year.strip() else None

        # Insert the new song into the database
        cursor.execute('''INSERT INTO songs (title, artist, album, duration, genre, release_year, spotify_id, youtube_url)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                       (title, artist, album, duration, genre, release_year, spotify_id, youtube_url))
        db.commit()

        flash('New song added successfully!', 'success')
        return redirect(url_for('songs.show_songs'))

    # Handle GET request to display all songs
    cursor.execute('SELECT * FROM songs ORDER BY created_at DESC')
    all_songs = cursor.fetchall()
    return render_template('songs.html', all_songs=all_songs)

@songs.route('/update_song/<int:song_id>', methods=['POST'])
def update_song(song_id):
    db = get_db()
    cursor = db.cursor()

    # Update the song's details
    title = request.form['title']
    artist = request.form['artist']
    album = request.form.get('album', '')
    duration = request.form.get('duration', None)
    genre = request.form.get('genre', '')
    release_year = request.form.get('release_year', None)
    spotify_id = request.form.get('spotify_id', '')
    youtube_url = request.form.get('youtube_url', '')

    # Convert empty strings to None for nullable fields
    duration = int(duration) if duration and duration.strip() else None
    release_year = int(release_year) if release_year and release_year.strip() else None

    cursor.execute('''UPDATE songs SET title = %s, artist = %s, album = %s, duration = %s,
                     genre = %s, release_year = %s, spotify_id = %s, youtube_url = %s
                     WHERE song_id = %s''',
                   (title, artist, album, duration, genre, release_year, spotify_id, youtube_url, song_id))
    db.commit()

    flash('Song updated successfully!', 'success')
    return redirect(url_for('songs.show_songs'))

@songs.route('/delete_song/<int:song_id>', methods=['POST'])
def delete_song(song_id):
    db = get_db()
    cursor = db.cursor()

    # Delete the song
    cursor.execute('DELETE FROM songs WHERE song_id = %s', (song_id,))
    db.commit()

    flash('Song deleted successfully!', 'danger')
    return redirect(url_for('songs.show_songs'))

# AJAX endpoints for autosave functionality
@songs.route('/api/songs', methods=['POST'])
def api_create_song():
    db = get_db()
    cursor = db.cursor()

    data = request.json
    title = data.get('title')
    artist = data.get('artist')
    album = data.get('album', '')
    duration = int(data.get('duration')) if data.get('duration') else None
    genre = data.get('genre', '')
    release_year = int(data.get('release_year')) if data.get('release_year') else None
    spotify_id = data.get('spotify_id', '')
    youtube_url = data.get('youtube_url', '')

    cursor.execute('''INSERT INTO songs (title, artist, album, duration, genre, release_year, spotify_id, youtube_url)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                   (title, artist, album, duration, genre, release_year, spotify_id, youtube_url))
    db.commit()

    song_id = cursor.lastrowid
    return jsonify({'success': True, 'song_id': song_id, 'message': 'Song created successfully!'})

@songs.route('/api/songs/<int:song_id>', methods=['PUT'])
def api_update_song(song_id):
    db = get_db()
    cursor = db.cursor()

    data = request.json
    field = data.get('field')
    value = data.get('value')

    # Handle different field types
    if field in ['duration', 'release_year']:
        value = int(value) if value else None

    # Build dynamic query
    cursor.execute(f'UPDATE songs SET {field} = %s WHERE song_id = %s', (value, song_id))
    db.commit()

    if cursor.rowcount > 0:
        return jsonify({'success': True, 'message': f'{field.replace("_", " ").title()} updated successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Song not found'})

@songs.route('/api/songs/<int:song_id>', methods=['DELETE'])
def api_delete_song(song_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('DELETE FROM songs WHERE song_id = %s', (song_id,))
    db.commit()

    if cursor.rowcount > 0:
        return jsonify({'success': True, 'message': 'Song deleted successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Song not found'})