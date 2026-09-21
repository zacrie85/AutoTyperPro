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
- **Multi-target (baru di v1.2)**: tambahkan banyak titik klik, setiap target punya pengaturan sendiri:
  - Nama target bebas
  - Posisi X,Y (bisa diambil otomatis lewat tombol AMBIL POSISI)
  - Jeda detik per target
  - Ketik teks atau hanya klik (mis. untuk tombol kirim)
  - Enter otomatis per target
  - Urutan bisa diatur (NAIK/TURUN), bisa diedit/dihapus
- Hotkey global: **F6 = mulai**, **F7 / ESC = berhenti**
- Hitungan mundur sebelum mulai, supaya sempat fokus ke kolom tujuan
- Jeda antar pengiriman (anti spam) + batas pengiriman (0 = tanpa batas)
- Enter otomatis setelah tiap pengiriman (opsional, mode biasa)
- Pratinjau teks live sebelum dikirim
- Pengaturan + daftar target tersimpan otomatis (`auto_typer_settings.json`)
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

## Mode Multi-Target (Baru di v1.2)

Isi daftar TARGET dan aplikasi akan mengklik setiap titik secara berurutan lalu mengetik di sana — cocok untuk mengisi beberapa kolom sekaligus atau mengklik tombol kirim secara otomatis. Daftar target kosong = perilaku lama (mengetik ke aplikasi yang sedang fokus).

Detail langkah demi langkah ada di `PANDUAN.txt`, bagian *MODE MULTI-TARGET*.

## Catatan Versi AutoHotkey

Versi AutoHotkey (rilis v1.1) **dihentikan** karena ditemukan error saat dipakai. Aset lama masih tersedia di [Release v1.1](https://github.com/zacrie85/AutoTyperPro/releases/tag/v1.1) untuk referensi, namun pengembangan kembali fokus ke versi Python yang stabil.

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
