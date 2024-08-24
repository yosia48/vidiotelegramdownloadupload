from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import io
from telegram import Bot, InputFile
import asyncio
import re
import os

# Konfigurasi
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'xxxcreditial.json'
TOKEN = ''
CHAT_ID = '-100'  # ID grup
TOPIC_ID = ''  # ID topik musik
bot = Bot(token=TOKEN)

# Setup Google Drive API
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

def extract_folder_id(url):
    """Extract folder ID from Google Drive URL"""
    match = re.search(r'folders/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Drive URL")

def save_file_info_to_folder_file(folder_id, file_id, file_name):
    """Save file ID and name to folder_id.txt"""
    file_name_with_extension = f"{folder_id}.txt"
    with open(file_name_with_extension, 'a') as f:
        f.write(f"{file_id}: {file_name}\n")

async def send_document_to_telegram(file_name, file_content):
    """Send file to Telegram topic"""
    try:
        await bot.send_document(
            chat_id=CHAT_ID,
            document=InputFile(file_content, filename=file_name),
            disable_notification=False,
            allow_sending_without_reply=True,
            message_thread_id=TOPIC_ID  # Set this to the topic ID
        )
    except Exception as e:
        print(f"Error sending document to Telegram: {e}")

async def process_files_from_drive(folder_id):
    """Download files from Google Drive folder and upload them to Telegram"""
    query = f"'{folder_id}' in parents"
    results = drive_service.files().list(q=query).execute()
    items = results.get('files', [])

    # Load processed file IDs
    processed_files = set()
    if os.path.exists(f"{folder_id}.txt"):
        with open(f"{folder_id}.txt", 'r') as f:
            for line in f:
                processed_files.add(line.split(':')[0].strip())

    if not items:
        print('No files found.')
    else:
        # Sort files by name
        items_sorted = sorted(items, key=lambda x: x['name'])
        for item in items_sorted:
            file_id = item['id']
            file_name = item['name']
            
            if file_id in processed_files:
                print(f"Skipping already processed file {file_name}...")
                continue

            print(f"Processing {file_name}...")

            # Download file
            try:
                request = drive_service.files().get_media(fileId=file_id)
                fh = io.BytesIO()  # Use BytesIO instead of FileIO
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(f"Downloading {file_name} ({int(status.progress() * 100)}%)")

                # Seek to the start of the BytesIO object
                fh.seek(0)

                print(f"Uploading {file_name} to Telegram group...")
                try:
                    await send_document_to_telegram(file_name, fh)
                    print(f"{file_name} uploaded successfully.")
                    # Save file ID and name to the folder file
                    save_file_info_to_folder_file(folder_id, file_id, file_name)
                except Exception as e:
                    print(f"Error uploading {file_name}: {e}")

                # Add to processed files
                processed_files.add(file_id)
                
            except Exception as e:
                print(f"Error while processing file {file_name}: {e}")

async def main():
    url = input("Masukkan URL folder Google Drive: ")
    folder_id = extract_folder_id(url)
    # Save the folder ID to folderid.txt
    with open('folderid.txt', 'w') as f:
        f.write(f"{folder_id}\n")
    print(f"Extracted folder ID: {folder_id}")
    await process_files_from_drive(folder_id)

# Start the event loop
asyncio.run(main())
