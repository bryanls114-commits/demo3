-- Database Schema for Flask Starter Kit
-- Run this file to create the required database structure

-- Create sample_table
CREATE TABLE sample_table (
    sample_table_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Add indexes for common queries
CREATE INDEX idx_sample_table_name ON sample_table (last_name, first_name);
CREATE INDEX idx_sample_table_dob ON sample_table (date_of_birth);

-- Create songs table
CREATE TABLE songs (
    song_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255) NOT NULL,
    album VARCHAR(255),
    duration INT, -- duration in seconds
    genre VARCHAR(100),
    release_year YEAR,
    spotify_id VARCHAR(100),
    youtube_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create playlists table
CREATE TABLE playlists (
    playlist_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(100), -- could be user_id if you have users table
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create playlist_songs junction table (many-to-many relationship)
CREATE TABLE playlist_songs (
    playlist_song_id INT AUTO_INCREMENT PRIMARY KEY,
    playlist_id INT NOT NULL,
    song_id INT NOT NULL,
    position_in_playlist INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE,
    UNIQUE KEY unique_playlist_song (playlist_id, song_id)
);

-- Add indexes for playlist tables
CREATE INDEX idx_songs_artist ON songs (artist);
CREATE INDEX idx_songs_genre ON songs (genre);
CREATE INDEX idx_songs_title ON songs (title);
CREATE INDEX idx_playlists_name ON playlists (name);
CREATE INDEX idx_playlists_created_by ON playlists (created_by);
CREATE INDEX idx_playlist_songs_playlist ON playlist_songs (playlist_id);
CREATE INDEX idx_playlist_songs_position ON playlist_songs (playlist_id, position_in_playlist);