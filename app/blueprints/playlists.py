from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.db_connect import get_db

playlists = Blueprint('playlists', __name__)

@playlists.route('/', methods=['GET', 'POST'])
def show_playlists():
    db = get_db()
    cursor = db.cursor()

    # Handle POST request to add a new playlist
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        is_public = 'is_public' in request.form
        created_by = request.form.get('created_by', '')

        # Insert the new playlist into the database
        cursor.execute('''INSERT INTO playlists (name, description, is_public, created_by)
                         VALUES (%s, %s, %s, %s)''',
                       (name, description, is_public, created_by))
        db.commit()

        flash('New playlist created successfully!', 'success')
        return redirect(url_for('playlists.show_playlists'))

    # Handle GET request to display all playlists and songs
    cursor.execute('SELECT * FROM playlists ORDER BY created_at DESC')
    all_playlists = cursor.fetchall()

    cursor.execute('SELECT * FROM songs ORDER BY created_at DESC')
    all_songs = cursor.fetchall()

    return render_template('playlists.html', all_playlists=all_playlists, all_songs=all_songs)

@playlists.route('/view/<int:playlist_id>')
def view_playlist(playlist_id):
    db = get_db()
    cursor = db.cursor()

    # Get playlist details
    cursor.execute('SELECT * FROM playlists WHERE playlist_id = %s', (playlist_id,))
    playlist = cursor.fetchone()

    if not playlist:
        flash('Playlist not found!', 'error')
        return redirect(url_for('playlists.show_playlists'))

    # Get songs in the playlist with their details
    cursor.execute('''SELECT s.*, ps.position_in_playlist, ps.added_at
                     FROM songs s
                     JOIN playlist_songs ps ON s.song_id = ps.song_id
                     WHERE ps.playlist_id = %s
                     ORDER BY ps.position_in_playlist''', (playlist_id,))
    playlist_songs = cursor.fetchall()

    # Get all songs for adding to playlist
    cursor.execute('SELECT * FROM songs ORDER BY title')
    all_songs = cursor.fetchall()

    return render_template('playlist_detail.html', playlist=playlist,
                         playlist_songs=playlist_songs, all_songs=all_songs)

@playlists.route('/update_playlist/<int:playlist_id>', methods=['POST'])
def update_playlist(playlist_id):
    db = get_db()
    cursor = db.cursor()

    # Update the playlist's details
    name = request.form['name']
    description = request.form.get('description', '')
    is_public = 'is_public' in request.form
    created_by = request.form.get('created_by', '')

    cursor.execute('''UPDATE playlists SET name = %s, description = %s, is_public = %s, created_by = %s
                     WHERE playlist_id = %s''',
                   (name, description, is_public, created_by, playlist_id))
    db.commit()

    flash('Playlist updated successfully!', 'success')
    return redirect(url_for('playlists.show_playlists'))

@playlists.route('/delete_playlist/<int:playlist_id>', methods=['POST'])
def delete_playlist(playlist_id):
    db = get_db()
    cursor = db.cursor()

    # Delete the playlist (cascade will handle playlist_songs)
    cursor.execute('DELETE FROM playlists WHERE playlist_id = %s', (playlist_id,))
    db.commit()

    flash('Playlist deleted successfully!', 'danger')
    return redirect(url_for('playlists.show_playlists'))

@playlists.route('/add_song_to_playlist/<int:playlist_id>', methods=['POST'])
def add_song_to_playlist(playlist_id):
    db = get_db()
    cursor = db.cursor()

    song_id = request.form['song_id']

    # Get the next position in the playlist
    cursor.execute('SELECT MAX(position_in_playlist) FROM playlist_songs WHERE playlist_id = %s', (playlist_id,))
    result = cursor.fetchone()
    next_position = (result[0] or 0) + 1

    try:
        # Add song to playlist
        cursor.execute('''INSERT INTO playlist_songs (playlist_id, song_id, position_in_playlist)
                         VALUES (%s, %s, %s)''',
                       (playlist_id, song_id, next_position))
        db.commit()
        flash('Song added to playlist successfully!', 'success')
    except Exception as e:
        flash('Song is already in this playlist!', 'warning')

    return redirect(url_for('playlists.view_playlist', playlist_id=playlist_id))

@playlists.route('/remove_song_from_playlist/<int:playlist_id>/<int:song_id>', methods=['POST'])
def remove_song_from_playlist(playlist_id, song_id):
    db = get_db()
    cursor = db.cursor()

    # Remove song from playlist
    cursor.execute('DELETE FROM playlist_songs WHERE playlist_id = %s AND song_id = %s',
                   (playlist_id, song_id))
    db.commit()

    flash('Song removed from playlist!', 'info')
    return redirect(url_for('playlists.view_playlist', playlist_id=playlist_id))

# AJAX endpoints for autosave functionality
@playlists.route('/api/playlists', methods=['POST'])
def api_create_playlist():
    db = get_db()
    cursor = db.cursor()

    data = request.json
    name = data.get('name')
    description = data.get('description', '')
    is_public = data.get('is_public', False)
    created_by = data.get('created_by', '')

    cursor.execute('''INSERT INTO playlists (name, description, is_public, created_by)
                     VALUES (%s, %s, %s, %s)''',
                   (name, description, is_public, created_by))
    db.commit()

    playlist_id = cursor.lastrowid
    return jsonify({'success': True, 'playlist_id': playlist_id, 'message': 'Playlist created successfully!'})

@playlists.route('/api/playlists/<int:playlist_id>', methods=['PUT'])
def api_update_playlist(playlist_id):
    db = get_db()
    cursor = db.cursor()

    data = request.json
    field = data.get('field')
    value = data.get('value')

    # Handle boolean field
    if field == 'is_public':
        value = bool(value)

    cursor.execute(f'UPDATE playlists SET {field} = %s WHERE playlist_id = %s', (value, playlist_id))
    db.commit()

    if cursor.rowcount > 0:
        return jsonify({'success': True, 'message': f'{field.replace("_", " ").title()} updated successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Playlist not found'})

@playlists.route('/api/playlists/<int:playlist_id>', methods=['DELETE'])
def api_delete_playlist(playlist_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('DELETE FROM playlists WHERE playlist_id = %s', (playlist_id,))
    db.commit()

    if cursor.rowcount > 0:
        return jsonify({'success': True, 'message': 'Playlist deleted successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Playlist not found'})

@playlists.route('/api/playlists/<int:playlist_id>/songs', methods=['POST'])
def api_add_song_to_playlist(playlist_id):
    db = get_db()
    cursor = db.cursor()

    data = request.json
    song_id = data.get('song_id')

    # Get the next position in the playlist
    cursor.execute('SELECT MAX(position_in_playlist) FROM playlist_songs WHERE playlist_id = %s', (playlist_id,))
    result = cursor.fetchone()
    next_position = (result[0] or 0) + 1

    try:
        cursor.execute('''INSERT INTO playlist_songs (playlist_id, song_id, position_in_playlist)
                         VALUES (%s, %s, %s)''',
                       (playlist_id, song_id, next_position))
        db.commit()
        return jsonify({'success': True, 'message': 'Song added to playlist successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Song is already in this playlist!'})

@playlists.route('/api/playlists/<int:playlist_id>/songs/<int:song_id>', methods=['DELETE'])
def api_remove_song_from_playlist(playlist_id, song_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('DELETE FROM playlist_songs WHERE playlist_id = %s AND song_id = %s',
                   (playlist_id, song_id))
    db.commit()

    if cursor.rowcount > 0:
        return jsonify({'success': True, 'message': 'Song removed from playlist!'})
    else:
        return jsonify({'success': False, 'message': 'Song not found in playlist'})

# Songs CRUD endpoints (moved from songs blueprint)
@playlists.route('/api/songs', methods=['POST'])
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

@playlists.route('/api/songs/<int:song_id>', methods=['PUT'])
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

@playlists.route('/api/songs/<int:song_id>', methods=['DELETE'])
def api_delete_song(song_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('DELETE FROM songs WHERE song_id = %s', (song_id,))
    db.commit()

    if cursor.rowcount > 0:
        return jsonify({'success': True, 'message': 'Song deleted successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Song not found'})