# Auto Typer Pro

Aplikasi desktop (Windows) untuk **mengetik teks + nomor berurutan secara otomatis** ke aplikasi lain: browser, Notepad, Excel, form komentar, dll.

Contoh: isi teks utama `dadang film part` dan nomor awal `3`, maka aplikasi akan mengetik otomatis:

```
dadang film part 3
dadang film part 4
dadang film part 5
... dst sampai kamu tekan F7
```

## Fitur

- Dua kolom inti: **teks utama** (tetap) + **nomor awal** (naik otomatis, langkah bisa diatur)
- Hotkey global: **F6 = mulai**, **F7 / ESC = berhenti**
- Hitungan mundur sebelum mulai, supaya sempat fokus ke kolom tujuan
- Jeda antar pengiriman (anti spam) + batas pengiriman (0 = tanpa batas)
- Enter otomatis setelah tiap pengiriman (opsional)
- Dua mode target:
  - Ketik ke aplikasi yang sedang fokus
  - Klik posisi layar tertentu dulu (koordinat bisa diambil otomatis), lalu ketik
- Pratinjau teks live sebelum dikirim
- Pengaturan tersimpan otomatis (`auto_typer_settings.json`)
- Tampilan dark neon, bahasa antarmuka Indonesia

## Cara Pakai Cepat

1. Install [Python](https://www.python.org/downloads/) (centang **Add Python to PATH** saat instalasi).
2. Klik dua kali `JALANKAN.bat` — library `pynput` otomatis dipasang, aplikasi langsung terbuka.
3. Isi teks utama + nomor awal, klik kolom tujuan di aplikasi lain, tekan **F6**.
4. Berhenti kapan saja dengan **F7**.

## Jadi File .EXE (Standalone)

Klik dua kali `build_exe.bat` → tunggu 1–3 menit → hasilnya ada di `dist/AutoTyperPro.exe`.
Setelah jadi `.exe`, aplikasi bisa dijalankan tanpa install Python.

Panduan lengkap: lihat `PANDUAN.txt`.

## Struktur Proyek

```
AutoTyperPro/
├── auto_typer.py      # Program utama (Python + tkinter + pynput)
├── JALANKAN.bat       # Jalankan cepat + auto-install dependensi
├── build_exe.bat      # Build .exe dengan PyInstaller
├── requirements.txt   # Daftar dependensi
└── PANDUAN.txt        # Panduan lengkap Bahasa Indonesia
```

## Teknologi

- Python 3 (tkinter untuk GUI, pynput untuk kontrol keyboard/mouse global)
- Kompatibel Windows / macOS / Linux (panduan & script diarahkan ke Windows)

## Catatan

- Gunakan secara bijak; sebagian game dengan anti-cheat dapat memblokir input otomatis.
- Jika antivirus memperingatkan file `.exe` hasil PyInstaller, itu false alarm — pilih "Izinkan".
