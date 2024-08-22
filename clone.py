from telethon import TelegramClient
import re

# Informasi Anda
api_id = 
api_hash = ''
phone = '+62'

# ID grup dan topik yang tetap
source_group_id =   # ID grup sumber
target_group_id =   # ID grup tujuan
topic_id =   # ID topik episode

# Inisialisasi client
client = TelegramClient('session_name', api_id, api_hash)

async def download_videos_from_file(file_path):
    await client.start(phone)
    
    try:
        # Membuka file download.txt dan membaca setiap link
        with open(file_path, 'r') as file:
            links = file.readlines()
        
        for link in links:
            # Menyaring ID pesan dari setiap link
            match = re.search(r'/(\d+)$', link.strip())
            if match:
                message_id = int(match.group(1))
            else:
                print(f"Link tidak valid: {link.strip()}")
                continue

            try:
                # Mendapatkan input entity grup sumber
                group_entity_source = await client.get_input_entity(source_group_id)
                print(f"Group source entity: {group_entity_source}")

                # Mengambil pesan dari grup sumber
                message = await client.get_messages(group_entity_source, ids=message_id)
                print(f"Pesan {message_id} berhasil diambil!")

                if message.video:
                    # Mendownload video
                    file_name = f"video_{message_id}.mp4"
                    await message.download_media(file=file_name)
                    print(f"Video {file_name} berhasil diunduh!")

                    # Mengambil teks dari pesan
                    caption_text = message.text if message.text else ''
                    print(f"Teks yang diambil: {caption_text}")

                    # Mendapatkan entitas grup tujuan
                    target_group_entity = await client.get_input_entity(target_group_id)
                    print(f"Group target entity: {target_group_entity}")

                    # Mengirim video ke topik tertentu dengan streaming support
                    await client.send_file(
                        target_group_entity,
                        file_name,
                        caption=caption_text,
                        supports_streaming=True,  # Pastikan streaming didukung
                        reply_to=topic_id  # Mencoba mengirim ke topik yang ditentukan
                    )
                    print(f"Video {file_name} dan teks berhasil dikirim ke topik {topic_id}!")
                else:
                    print(f"Pesan {message_id} tidak berisi video.")
            except Exception as e:
                print(f"Error saat memproses pesan {message_id}: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Menjalankan client
with client:
    client.loop.run_until_complete(download_videos_from_file('download.txt'))
