import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import time

### 1. Paramètres Spotify
SPOTIFY_CLIENT_ID = "TA_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "TON_SECRET"
SPOTIFY_REDIRECT_URI = "http://localhost:8888/callback"
SPOTIFY_SCOPE = "playlist-read-private"

### 2. Paramètres YouTube
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube"]
YOUTUBE_CLIENT_SECRETS_FILE = "client_secrets.json"

# ----------------------------------------------------
# Connexion à Spotify
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SPOTIFY_SCOPE
)
sp = spotipy.Spotify(auth_manager=sp_oauth)

# ----------------------------------------------------
# Connexion à YouTube
flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRETS_FILE, YOUTUBE_SCOPES)
credentials = flow.run_console()
youtube = build("youtube", "v3", credentials=credentials)

# ----------------------------------------------------
# Fonction pour récupérer les titres Spotify
def get_spotify_tracks(playlist_id):
    results = sp.playlist_items(playlist_id)
    tracks = []
    for item in results["items"]:
        track = item["track"]
        title = track["name"]
        artist = track["artists"][0]["name"]
        tracks.append(f"{artist} - {title}")
    return tracks

# ----------------------------------------------------
# Fonction pour chercher une vidéo sur YouTube
def search_youtube_video(query):
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=1,
        type="video"
    ).execute()
    items = search_response.get("items")
    if items:
        return items[0]["id"]["videoId"]
    return None

# ----------------------------------------------------
# Créer une playlist YouTube
def create_youtube_playlist(title, description):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )
    response = request.execute()
    return response["id"]

# ----------------------------------------------------
# Ajouter une vidéo à une playlist YouTube
def add_video_to_playlist(playlist_id, video_id):
    youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    ).execute()

# ----------------------------------------------------
# 🔁 Exécution
spotify_playlist_id = "ta_playlist_spotify_id"
youtube_playlist_title = "Playlist migrée de Spotify"
youtube_playlist_desc = "Importée automatiquement"

print("Récupération des titres Spotify...")
tracks = get_spotify_tracks(spotify_playlist_id)

print("Création de la playlist YouTube...")
youtube_playlist_id = create_youtube_playlist(youtube_playlist_title, youtube_playlist_desc)

for track in tracks:
    print(f"Recherche : {track}")
    video_id = search_youtube_video(track)
    if video_id:
        print(f"Ajout de {track} → https://youtu.be/{video_id}")
        add_video_to_playlist(youtube_playlist_id, video_id)
        time.sleep(1)  # pause pour éviter les quotas
    else:
        print(f"❌ Aucune vidéo trouvée pour : {track}")

print("✅ Terminé ! Playlist créée sur YouTube.")
