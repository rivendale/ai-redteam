"""Settings for the station-photo uploader. Secrets come from the environment."""
import os

DOCK_API_KEY = os.environ.get("PEDALO_DOCK_API_KEY", "")
PHOTO_BUCKET = "pedalo-station-photos"
