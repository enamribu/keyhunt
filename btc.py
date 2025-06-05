# === Auto Install Dependencies ===
import subprocess
import sys
import importlib

required_modules = ["requests"]

for module in required_modules:
    try:
        importlib.import_module(module)
    except ImportError:
        print(f"[!] Modul '{module}' tidak ditemukan. Menginstall...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])
    else:
        pass  # Modul sudah terinstall, lanjut

# =================================

import subprocess
import requests
import os
import time
from datetime import datetime
import sys
import html 

# Konfigurasi Telegram
TELEGRAM_TOKEN = "7513012504:AAFYmIgQgLzp0k_J63E22LtM-A6Xq9UvXEU"  # GANTI DENGAN TOKEN BOT ANDA
TELEGRAM_CHAT_ID = "513265991"  # GANTI DENGAN CHAT ID ANDA

def send_to_telegram(message):
    """Mengirim pesan ke Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"[!] Gagal mengirim ke Telegram: {str(e)}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[!] Terjadi kesalahan tak terduga saat mengirim ke Telegram: {str(e)}", file=sys.stderr)
        return False

def print_banner():
    """Menampilkan banner informasi."""
    print("""
    #############################################
    #           Keyhunt Automation Tool         #
    #           Telegram Notifications          #
    #############################################
    """)

def get_new_keys(file_path, last_position):
    """
    Mendapatkan blok key baru yang ditambahkan ke file.
    Setiap key baru adalah list dari baris-baris string dalam blok tersebut.
    """
    new_key_blocks = [] 
    try:
        if not os.path.exists(file_path):
            return new_key_blocks, last_position

        current_size = os.path.getsize(file_path)
        if current_size == last_position:
            return new_key_blocks, last_position

        with open(file_path, "r", encoding='utf-8', errors='replace') as f:
            f.seek(last_position)
            new_content = f.read()
            
            if new_content:
                content_to_process = new_content.strip()
                if not content_to_process:
                    last_position = f.tell()
                    return new_key_blocks, last_position

                key_blocks_text = content_to_process.split('\n\n') 
                for block_text in key_blocks_text:
                    block_text_stripped = block_text.strip() 
                    if not block_text_stripped: 
                        continue
                    
                    lines_in_block = [line.strip() for line in block_text_stripped.split('\n') if line.strip()]
                    
                    if lines_in_block: 
                        new_key_blocks.append(lines_in_block)
            
            last_position = f.tell()
    except FileNotFoundError:
        pass 
    except Exception as e:
        print(f"[!] Gagal membaca file output '{file_path}': {str(e)}", file=sys.stderr)
    return new_key_blocks, last_position

def format_key_info(key_block_lines):
    """
    Memformat informasi key (sebagai list of strings) untuk Telegram
    sesuai dengan contoh format yang diberikan pengguna.
    """
    
    header = "💰 <b>KEY FOUND!</b> 💰\n" 
    telegram_message_lines = []

    if key_block_lines and \
       (key_block_lines[0].startswith("Privkey ") or key_block_lines[0].startswith("Private Key: ")):
        
        line1_text = key_block_lines[0]
        val1 = ""
        if line1_text.startswith("Privkey "): val1 = line1_text[len("Privkey "):].strip()
        elif line1_text.startswith("Private Key: "): val1 = line1_text[len("Private Key: "):].strip()
        if val1: telegram_message_lines.append(f"Private Key: <code>{html.escape(val1)}</code>")

        if len(key_block_lines) > 1:
            line2_text = key_block_lines[1]
            val2 = ""
            if line2_text.startswith("Publickey "): val2 = line2_text[len("Publickey "):].strip()
            elif line2_text.startswith("pubkey: "): val2 = line2_text[len("pubkey: "):].strip()
            if val2: telegram_message_lines.append(f"pubkey: <code>{html.escape(val2)}</code>")
        
        if len(key_block_lines) > 2:
            line3_text = key_block_lines[2]
            val3 = ""
            if line3_text.startswith("Address "): val3 = line3_text[len("Address "):].strip()
            elif line3_text.startswith("Address: "): val3 = line3_text[len("Address: "):].strip()
            if val3:
                if val3.upper() == "N/A": telegram_message_lines.append(f"Address: ({html.escape(val3)})")
                else: telegram_message_lines.append(f"Address: <code>{html.escape(val3)}</code>")

        if len(key_block_lines) > 3:
            line4_text = key_block_lines[3]
            val4 = ""
            if line4_text.startswith("Rmd160 "): val4 = line4_text[len("Rmd160 "):].strip()
            elif line4_text.startswith("rmd160: "): val4 = line4_text[len("rmd160: "):].strip()
            if val4:
                if val4.upper() == "N/A": telegram_message_lines.append(f"rmd160: ({html.escape(val4)})")
                else: telegram_message_lines.append(f"rmd160: <code>{html.escape(val4)}</code>")
    
    elif key_block_lines and key_block_lines[0].startswith("Key found privkey "):
        line1_text = key_block_lines[0]
        val1 = line1_text[len("Key found privkey"):].strip()
        if val1: telegram_message_lines.append(f"Key found privkey: <code>{html.escape(val1)}</code>")

        if len(key_block_lines) > 1:
            line2_text = key_block_lines[1]
            val2 = ""
            if line2_text.startswith("Publickey:"): 
                val2 = line2_text[len("Publickey:"):].strip()
            elif line2_text.startswith("Publickey "):
                val2 = line2_text[len("Publickey "):].strip()
            
            if val2:
                telegram_message_lines.append(f"Publickey: <code>{html.escape(val2)}</code>")
    
    else: 
        for line_text in key_block_lines:
            telegram_message_lines.append(f"<code>{html.escape(line_text)}</code>")

    if telegram_message_lines:
        return header + "\n" + "\n".join(telegram_message_lines)
    else: 
        return header + "<i>(Unable to parse key block content)</i>"

def format_vanity_key_info(key_block_lines):
    """
    Memformat informasi vanity key untuk Telegram.
    """
    header = "🎯 <b>VANITY ADDRESS FOUND!</b> 🎯\n"
    telegram_message_lines = []
    
    for line in key_block_lines:
        if line.startswith("Vanity Private Key:"):
            val = line[len("Vanity Private Key:"):].strip()
            telegram_message_lines.append(f"Private Key: <code>{html.escape(val)}</code>")
        elif line.startswith("pubkey:"):
            val = line[len("pubkey:"):].strip()
            telegram_message_lines.append(f"pubkey: <code>{html.escape(val)}</code>")
        elif line.startswith("Address:"):
            val = line[len("Address:"):].strip()
            telegram_message_lines.append(f"Address: <code>{html.escape(val)}</code>")
        elif line.startswith("rmd160:"):
            val = line[len("rmd160:"):].strip()
            telegram_message_lines.append(f"rmd160: <code>{html.escape(val)}</code>")
        else:
            telegram_message_lines.append(f"<code>{html.escape(line)}</code>")
    
    if telegram_message_lines:
        return header + "\n" + "\n".join(telegram_message_lines)
    else:
        return header + "<i>(Unable to parse vanity key block content)</i>"

def parse_config(file_path):
    """Membaca konfigurasi dari file dan memungkinkan pemilihan script."""
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            
            if not lines:
                print("[!] Error: File BTC_Setting.txt kosong")
                return None
            
            print("[*] List script:")
            selectable_options = [] 
            
            for line in lines:
                if line.startswith('***') or not line: 
                    print(line) 
                else:
                    selectable_options.append(line)
                    print(f"[{len(selectable_options)}] {line}") 
            
            while True:
                try:
                    choice_input = input("\nPilih nomor atau masukkan parameter manual: ")
                    if choice_input.lower() == 'q':
                        print("[*] Keluar dari pemilihan script.")
                        return None
                    
                    try:
                        choice = int(choice_input)
                        if 1 <= choice <= len(selectable_options):
                            command = selectable_options[choice - 1].split()
                            return command
                        else:
                            print("[!] Pilihan tidak valid. Silakan coba lagi.")
                    except ValueError:
                        # Jika input bukan angka, asumsikan itu parameter manual
                        return choice_input.split()

                except Exception as e:
                    print(f"[!] Terjadi kesalahan saat memproses pilihan: {str(e)}", file=sys.stderr)
                    return None

    except FileNotFoundError:
        print(f"[!] Error: File konfigurasi '{file_path}' tidak ditemukan.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[!] Gagal membaca file konfigurasi '{file_path}': {str(e)}", file=sys.stderr)
        return None

def run_keyhunt():
    """Menjalankan keyhunt.exe dengan parameter dari BTC_Setting.txt atau manual."""
    print_banner()
    
    try:
        command = parse_config("BTC_Setting.txt")
        if not command:
            return
        
        print("\n[*] Menjalankan command:")
        print(" ".join(command))
        print(f"[*] Waktu mulai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        output_file = "KEYFOUNDKEYFOUND.txt"
        vanity_file = "VANITYKEYFOUND.txt"
        last_position = os.path.getsize(output_file) if os.path.exists(output_file) else 0
        last_vanity_position = os.path.getsize(vanity_file) if os.path.exists(vanity_file) else 0
        
        process = subprocess.Popen(
            command,
            stdout=sys.stdout,
            stderr=sys.stderr,
            stdin=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
            encoding='utf-8',
            errors='replace'
        )
        
        start_time = time.time()
        keys_found_session = 0
        vanity_keys_found_session = 0
        
        while True:
            if process.poll() is not None: 
                print(f"[*] Proses keyhunt selesai dengan kode: {process.returncode}")
                break
            
            # Check for regular keys
            if os.path.exists(output_file):
                new_key_blocks_list, last_pos_update = get_new_keys(output_file, last_position)
                if new_key_blocks_list:
                    last_position = last_pos_update
                    for key_block_lines_item in new_key_blocks_list: 
                        keys_found_session += 1
                        formatted_message = format_key_info(key_block_lines_item)
                        print(f"\n[+] Key ditemukan! Mengirim ke Telegram...")
                        if send_to_telegram(formatted_message):
                            print("[+] Notifikasi berhasil terkirim ke Telegram.")
                        else:
                            print("[-] Gagal mengirim notifikasi ke Telegram.")
            
            # Check for vanity keys
            if os.path.exists(vanity_file):
                new_vanity_blocks, last_vanity_pos_update = get_new_keys(vanity_file, last_vanity_position)
                if new_vanity_blocks:
                    last_vanity_position = last_vanity_pos_update
                    for vanity_block in new_vanity_blocks:
                        vanity_keys_found_session += 1
                        formatted_message = format_vanity_key_info(vanity_block)
                        print(f"\n[+] Vanity address ditemukan! Mengirim ke Telegram...")
                        if send_to_telegram(formatted_message):
                            print("[+] Notifikasi vanity address berhasil terkirim ke Telegram.")
                        else:
                            print("[-] Gagal mengirim notifikasi vanity address ke Telegram.")
            
            time.sleep(1)
        
        print("\n[*] Pemantauan selesai.")
        print(f"[*] Waktu eksekusi total: {time.time() - start_time:.2f} detik")
        print(f"[*] Total key ditemukan dalam sesi ini: {keys_found_session}")
        print(f"[*] Total vanity address ditemukan dalam sesi ini: {vanity_keys_found_session}")
        
        # Final check for regular keys
        if os.path.exists(output_file):
            final_key_blocks, _ = get_new_keys(output_file, last_position)
            if final_key_blocks:
                print("[*] Memeriksa key terakhir setelah proses selesai...")
                for key_block_lines_item in final_key_blocks:
                    keys_found_session += 1
                    formatted_message = format_key_info(key_block_lines_item)
                    print(f"\n[+] Key ditemukan (final check)! Mengirim ke Telegram...")
                    if send_to_telegram(formatted_message):
                        print("[+] Notifikasi berhasil terkirim ke Telegram (final check).")
                    else:
                        print("[-] Gagal mengirim notifikasi ke Telegram (final check).")
                print(f"[*] Total key ditemukan (termasuk final check): {keys_found_session}")
        
        # Final check for vanity keys
        if os.path.exists(vanity_file):
            final_vanity_blocks, _ = get_new_keys(vanity_file, last_vanity_position)
            if final_vanity_blocks:
                print("[*] Memeriksa vanity address terakhir setelah proses selesai...")
                for vanity_block in final_vanity_blocks:
                    vanity_keys_found_session += 1
                    formatted_message = format_vanity_key_info(vanity_block)
                    print(f"\n[+] Vanity address ditemukan (final check)! Mengirim ke Telegram...")
                    if send_to_telegram(formatted_message):
                        print("[+] Notifikasi vanity address berhasil terkirim ke Telegram (final check).")
                    else:
                        print("[-] Gagal mengirim notifikasi vanity address ke Telegram (final check).")
                print(f"[*] Total vanity address ditemukan (termasuk final check): {vanity_keys_found_session}")

    except FileNotFoundError:
        print(f"[!] Error: Pastikan 'keyhunt.exe' berada di direktori yang sama atau dalam PATH, dan 'BTC_Setting.txt' ada.", file=sys.stderr)
    except subprocess.SubprocessError as e:
        error_msg = f"Gagal menjalankan keyhunt: {str(e)}"
        print(f"[!] {error_msg}", file=sys.stderr)
        send_to_telegram(f"❌ <b>ERROR Subprocess</b> ❌\n\n{html.escape(error_msg)}")
    except Exception as e:
        error_msg = f"Terjadi kesalahan umum: {str(e)}"
        print(f"[!] {error_msg}", file=sys.stderr)
        send_to_telegram(f"❌ <b>ERROR Umum</b> ❌\n\n{html.escape(error_msg)}")

if __name__ == "__main__":
    run_keyhunt()
    print("\n[*] Tekan Enter untuk keluar.")
    input()
