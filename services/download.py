"""
Google Drive public file download service
"""
import os
import requests
from urllib.parse import urlparse, parse_qs

def extract_file_id_from_url(gdrive_url):
    """Extract file ID from Google Drive URL"""
    if "/file/d/" in gdrive_url:
        # Standard sharing URL: https://drive.google.com/file/d/FILE_ID/view
        file_id = gdrive_url.split("/file/d/")[1].split("/")[0]
    elif "id=" in gdrive_url:
        # Direct URL with id parameter
        parsed = urlparse(gdrive_url)
        file_id = parse_qs(parsed.query)["id"][0]
    else:
        raise ValueError("Cannot extract file ID from URL")

    return file_id

def download_from_gdrive(gdrive_url, output_path):
    """Download file from Google Drive public URL"""
    print(f"📥 Downloading from Google Drive...")

    file_id = extract_file_id_from_url(gdrive_url)
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    response = requests.get(download_url, stream=True)

    # Handle large files that require confirmation
    if "quota exceeded" in response.text.lower():
        raise Exception("Google Drive quota exceeded. Try again later.")

    # Check for download warning (large files)
    if "download_warning" in response.text:
        # Extract confirmation token
        for line in response.text.splitlines():
            if "confirm=" in line:
                confirm_token = line.split("confirm=")[1].split("&")[0]
                download_url = f"https://drive.google.com/uc?export=download&confirm={confirm_token}&id={file_id}"
                response = requests.get(download_url, stream=True)
                break

    # Save file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    file_size = os.path.getsize(output_path)
    print(f"✅ Downloaded {file_size:,} bytes to {output_path}")

    return output_path