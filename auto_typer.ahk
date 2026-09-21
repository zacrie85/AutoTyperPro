;============================================================
;  AUTO TYPER PRO - Versi AutoHotkey v2  (v1.1)
;  Aplikasi ketik-otomatis dengan nomor berurutan
;------------------------------------------------------------
;  Contoh:
;    Teks utama : dadang film part
;    Nomor awal : 3
;    Hasil      : dadang film part 3 -> 4 -> 5 -> dst.
;
;  Hotkey:
;    F6        : Mulai
;    F7 / ESC  : Berhenti
;
;  Cara menjalankan:
;    - Portable   : klik dua kali JALANKAN-PORTABLE.bat
;    - Terpasang  : klik dua kali file ini
;                   (butuh AutoHotkey v2, gratis di
;                    https://www.autohotkey.com)
;============================================================

#Requires AutoHotkey v2.0
#SingleInstance Force
CoordMode "Mouse", "Screen"

; ---------------- Warna tema (dark neon) ----------------
C_BG     := "0F1220"
C_ENTRY  := "232948"
C_ACCENT := "00E68A"
C_RED    := "FF4D6D"
C_YELLOW := "FFD166"
C_TEXT   := "EEF0FF"
C_MUTED  := "9AA0C3"
C_BTN_TX := "052E1D"

; ---------------- Keadaan global ----------------
iniFile       := A_ScriptDir "\auto_typer_ahk.ini"
statusJalan   := false
stopFlag      := false
jumlahKirim   := 0
nomorSekarang := 0
savedNomorAwal := ""
cfg           := {}

; ---------------- GUI ----------------
main := Gui(, "Auto Typer Pro v1.1 (AutoHotkey)")
main.BackColor := C_BG
main.MarginX := 16
main.MarginY := 12

main.SetFont("s16 Bold c" C_ACCENT, "Segoe UI")
main.Add("Text",, "AUTO TYPER PRO (AutoHotkey)")
main.SetFont("s9 Norm c" C_MUTED)
main.Add("Text",, "Ketik teks + nomor berurutan secara otomatis")

; ================= 1. DATA YANG DIKETIK =================
main.SetFont("s10 Bold c" C_ACCENT)
main.Add("Text", "y+14", "1. DATA YANG DIKETIK")

main.SetFont("s9 Norm c" C_MUTED)
main.Add("Text", "y+8", "TEKS UTAMA (bagian yang tetap)")
main.SetFont("s10 c" C_TEXT)
edUtama := main.Add("Edit", "w440 Background" C_ENTRY, "dadang film part")

main.SetFont("s9 Norm c" C_MUTED)
main.Add("Text", "y+8", "NOMOR AWAL")
main.SetFont("s10 c" C_TEXT)
edNomor := main.Add("Edit", "w200 Background" C_ENTRY, "3")

main.SetFont("s9 Norm c" C_MUTED)
main.Add("Text", "x250 yp-22", "NAIK TIAP KALI")
main.SetFont("s10 c" C_TEXT)
edStep := main.Add("Edit", "x250 yp w200 Background" C_ENTRY, "1")

main.SetFont("s9 Norm c" C_MUTED)
main.Add("Text", "y+8", "TEKS TAMBAHAN SETELAH NOMOR (boleh dikosongkan)")
main.SetFont("s10 c" C_TEXT)
edTambahan := main.Add("Edit", "w440 Background" C_ENTRY)

main.SetFont("s9 c" C_TEXT)
cbSpasi := main.Add("Checkbox", "y+8 Checked Background" C_BG, "Beri spasi otomatis sebelum nomor")
main.SetFont("s10 Bold c" C_ACCENT)
lblPratinjau := main.Add("Text", "y+8 w440", "Pratinjau :  dadang film part 3")

; ================= 2. PENGATURAN PENGIRIMAN =================
main.SetFont("s10 Bold c" C_ACCENT)
main.Add("Text", "y+16", "2. PENGATURAN PENGIRIMAN")

main.SetFont("s9 Norm c" C_MUTED)
main.Add("Text", "y+8", "JEDA (detik)")
main.SetFont("s10 c" C_TEXT)
edJeda := main.Add("Edit", "w136 Background" C_ENTRY, "2.0")

main.SetFont("s9 Norm c" C_MUTED)
main.Add("Text", "x168 yp-22", "BATAS KIRIM")
main.SetFont("s10 c" C_TEXT)
edBatas := main.Add("Edit", "x168 yp w136 Background" C_ENTRY, "0")

main.SetFont("s9 Norm c" C_MUTED)
main.Add("Text", "x320 yp-22", "MUNDUR (detik)")
main.SetFont("s10 c" C_TEXT)
edMundur := main.Add("Edit", "x320 yp w136 Background" C_ENTRY, "5")

main.SetFont("s9 Norm c" C_MUTED)
main.Add("Text", "y+6 w440", "JEDA = jarak waktu antar pengiriman.`nBATAS KIRIM = 0 artinya berjalan terus sampai F7 ditekan.`nMUNDUR = hitungan mundur sebelum mulai.")

main.SetFont("s9 c" C_TEXT)
cbEnter := main.Add("Checkbox", "y+8 Background" C_BG, "Tekan Enter otomatis setelah tiap pengiriman")

; ================= 3. TARGET =================
main.SetFont("s10 Bold c" C_ACCENT)
main.Add("Text", "y+16", "3. TARGET")

main.SetFont("s9 c" C_TEXT)
rbFokus := main.Add("Radio", "Checked Background" C_BG, "Ketik ke aplikasi yang sedang fokus (klik dulu kolom tujuan)")
rbKlik  := main.Add("Radio", "y+2 Background" C_BG, "Klik posisi layar tertentu dulu, baru ketik")

main.SetFont("s9 Norm c" C_MUTED)
main.Add("Text", "y+10", "POSISI X")
main.SetFont("s10 c" C_TEXT)
edX := main.Add("Edit", "w150 Background" C_ENTRY)

main.SetFont("s9 Norm c" C_MUTED)
main.Add("Text", "x186 yp-22", "POSISI Y")
main.SetFont("s10 c" C_TEXT)
edY := main.Add("Edit", "x186 yp w150 Background" C_ENTRY)

btnAmbil := main.Add("Button", "x356 yp w104 h46 Background" C_ENTRY " c" C_ACCENT, "AMBIL POSISI")

main.SetFont("s9 Norm c" C_MUTED)
main.Add("Text", "y+6 w440", "Tekan AMBIL POSISI, lalu arahkan mouse ke titik target dan diamkan 5 detik.")

; ================= 4. STATUS =================
main.SetFont("s10 Bold c" C_ACCENT)
main.Add("Text", "y+16", "4. STATUS")

main.SetFont("s9 Bold c" C_ACCENT)
lblStatus := main.Add("Text", "y+8 w440", "● Siap — isi data, klik kolom tujuan, lalu tekan F6")
main.SetFont("s9 Norm c" C_MUTED)
lblProgress := main.Add("Text", "y+6 w440", "Terkirim: 0   |   Berikutnya: -")

; ================= TOMBOL =================
main.SetFont("s11 Bold")
btnMulai := main.Add("Button", "y+14 w216 h42 Background" C_ACCENT " c" C_BTN_TX, "MULAI (F6)")
btnStop  := main.Add("Button", "x+8 yp w216 h42 Background" C_RED " cFFFFFF Disabled", "BERHENTI (F7)")
main.SetFont("s9 Norm")
btnReset := main.Add("Button", "y+8 w440 Background" C_BG " c" C_MUTED, "Reset nomor ke NOMOR AWAL")

main.SetFont("s9 Norm c" C_MUTED)
main.Add("Text", "y+10 w440", "F6 = Mulai    |    F7 / ESC = Berhenti    |    Pengaturan tersimpan otomatis")

; ---------------- Kejadian (event) ----------------
btnMulai.OnEvent("Click", Mulai)
btnStop.OnEvent("Click", (*) => StopSemua())
btnAmbil.OnEvent("Click", (*) => AmbilPosisi())
btnReset.OnEvent("Click", ResetNomor)
edUtama.OnEvent("Change", (*) => Pratinjau())
edNomor.OnEvent("Change", (*) => Pratinjau())
edTambahan.OnEvent("Change", (*) => Pratinjau())
cbSpasi.OnEvent("Click", (*) => Pratinjau())
main.OnEvent("Close", SimpanDanKeluar)

MuatIni()
Pratinjau()
main.Show("w480")

;============================================================
;  FUNGSI-FUNGSI
;============================================================

Kompose(utama, nomor, tambahan, spasi) {
    if (spasi && utama != "" && !RegExMatch(utama, "\s$"))
        utama .= " "
    return utama . nomor . tambahan
}

Pratinjau(*) {
    global edUtama, edNomor, edTambahan, cbSpasi, lblPratinjau
    n := 0
    try n := Integer(edNomor.Value)
    lblPratinjau.Text := "Pratinjau :  " Kompose(edUtama.Value, n, edTambahan.Value, cbSpasi.Value)
}

Mulai(*) {
    global cfg, statusJalan, stopFlag, jumlahKirim, nomorSekarang, savedNomorAwal
    global edUtama, edNomor, edStep, edTambahan, edJeda, edBatas, edMundur, edX, edY
    global rbKlik, cbSpasi, cbEnter, btnMulai, btnStop

    if statusJalan
        return
    nomorAwal := 0, langkah := 0, jeda := 0.0, batas := 0, mundur := 0
    try {
        nomorAwal := Integer(Trim(edNomor.Value))
        langkah   := Integer(Trim(edStep.Value))
        jeda      := Float(StrReplace(Trim(edJeda.Value), ",", "."))
        batas     := Integer(Trim(edBatas.Value))
        mundur    := Integer(Trim(edMundur.Value))
    } catch {
        MsgBox("NOMOR AWAL, NAIK TIAP KALI, JEDA, BATAS KIRIM, dan MUNDUR`nharus diisi dengan angka yang benar.", "Auto Typer Pro", "Icon! 4096")
        return
    }
    if (jeda < 0.1) {
        MsgBox("JEDA minimal 0.1 detik supaya sistem tetap stabil.", "Auto Typer Pro", "Icon! 4096")
        return
    }
    if (mundur < 0 || mundur > 60) {
        MsgBox("MUNDUR harus antara 0 sampai 60 detik.", "Auto Typer Pro", "Icon! 4096")
        return
    }
    modeKlik := rbKlik.Value
    posX := 0, posY := 0
    if modeKlik {
        try {
            posX := Integer(Trim(edX.Value))
            posY := Integer(Trim(edY.Value))
        } catch {
            MsgBox("Mode klik: isi POSISI X dan Y dulu,`natau tekan tombol AMBIL POSISI.", "Auto Typer Pro", "Icon! 4096")
            return
        }
    }
    SimpanIni()
    cfg := {utama: edUtama.Value, tambahan: edTambahan.Value, spasi: cbSpasi.Value
          , enter: cbEnter.Value, langkah: langkah, jeda: jeda, batas: batas
          , mundur: mundur, modeKlik: modeKlik, posX: posX, posY: posY}
    savedNomorAwal := nomorAwal
    nomorSekarang  := nomorAwal
    jumlahKirim    := 0
    stopFlag       := false
    statusJalan    := true
    btnMulai.Enabled := false
    btnStop.Enabled  := true
    SetTimer JalankanLoop, -1
}

JalankanLoop() {
    global cfg, statusJalan, stopFlag, jumlahKirim, nomorSekarang
    global lblStatus, lblProgress, C_ACCENT, C_YELLOW, C_RED
    if (cfg.mundur > 0) {
        s := cfg.mundur
        while (s > 0) {
            if stopFlag {
                Selesai("Dibatalkan sebelum mulai.", true)
                return
            }
            lblStatus.Text := "● Mulai dalam " s " detik — segera fokuskan kolom tujuan..."
            lblStatus.SetFont("c" C_YELLOW)
            Sleep 1000
            s -= 1
        }
    }
    lblStatus.Text := "● Sedang berjalan... (tekan F7 untuk berhenti)"
    lblStatus.SetFont("c" C_ACCENT)
    while (!stopFlag) {
        if (cfg.batas > 0 && jumlahKirim >= cfg.batas) {
            Selesai("Selesai! Total terkirim: " jumlahKirim)
            return
        }
        teks := Kompose(cfg.utama, nomorSekarang, cfg.tambahan, cfg.spasi)
        if cfg.modeKlik {
            MouseMove cfg.posX, cfg.posY, 0
            Click "Left"
            Sleep 250
            if stopFlag
                break
        }
        SendText teks
        if cfg.enter
            Send "{Enter}"
        jumlahKirim += 1
        nomorSekarang += cfg.langkah
        berikut := Kompose(cfg.utama, nomorSekarang, cfg.tambahan, cfg.spasi)
        lblProgress.Text := "Terkirim: " jumlahKirim "   |   Berikutnya: " berikut
        if (cfg.batas > 0 && jumlahKirim >= cfg.batas) {
            Selesai("Selesai! Total terkirim: " jumlahKirim)
            return
        }
        sisa := Round(cfg.jeda * 1000)
        while (sisa > 0 && !stopFlag) {
            potong := (sisa > 50) ? 50 : sisa
            Sleep potong
            sisa -= potong
        }
    }
    Selesai("Dihentikan. Total terkirim: " jumlahKirim, true)
}

Selesai(pesan, merah := false) {
    global statusJalan, btnMulai, btnStop, lblStatus, C_ACCENT, C_RED
    statusJalan := false
    btnMulai.Enabled := true
    btnStop.Enabled  := false
    lblStatus.Text := "● " pesan
    lblStatus.SetFont("c" (merah ? C_RED : C_ACCENT))
}

StopSemua(*) {
    global statusJalan, stopFlag, lblStatus, C_YELLOW
    if statusJalan {
        stopFlag := true
        lblStatus.Text := "● Menghentikan..."
        lblStatus.SetFont("c" C_YELLOW)
    }
}

AmbilPosisi(*) {
    SetTimer AmbilCountdown, -1
}

AmbilCountdown() {
    global lblStatus, edX, edY, C_ACCENT, C_YELLOW
    s := 5
    while (s > 0) {
        lblStatus.Text := "● Arahkan mouse ke titik target dan diamkan... " s
        lblStatus.SetFont("c" C_YELLOW)
        Sleep 1000
        s -= 1
    }
    CoordMode "Mouse", "Screen"
    MouseGetPos &mx, &my
    edX.Value := mx
    edY.Value := my
    lblStatus.Text := "● Posisi tersimpan: X=" mx ", Y=" my ". Tekan F6 untuk mulai."
    lblStatus.SetFont("c" C_ACCENT)
}

ResetNomor(*) {
    global edNomor, lblProgress, jumlahKirim, savedNomorAwal
    global edUtama, edTambahan, cbSpasi, C_MUTED
    if (savedNomorAwal != "")
        edNomor.Value := savedNomorAwal
    jumlahKirim := 0
    Pratinjau()
    n := 0
    try n := Integer(edNomor.Value)
    lblProgress.Text := "Terkirim: 0   |   Berikutnya: " Kompose(edUtama.Value, n, edTambahan.Value, cbSpasi.Value)
}

SimpanDanKeluar(*) {
    SimpanIni()
    ExitApp
}

SimpanIni() {
    global iniFile, edUtama, edNomor, edStep, edTambahan, cbSpasi
    global edJeda, edBatas, edMundur, cbEnter, rbKlik, edX, edY
    try {
        IniWrite edUtama.Value, iniFile, "Set", "utama"
        IniWrite edNomor.Value, iniFile, "Set", "nomor"
        IniWrite edStep.Value, iniFile, "Set", "step"
        IniWrite edTambahan.Value, iniFile, "Set", "tambahan"
        IniWrite cbSpasi.Value, iniFile, "Set", "spasi"
        IniWrite edJeda.Value, iniFile, "Set", "jeda"
        IniWrite edBatas.Value, iniFile, "Set", "batas"
        IniWrite edMundur.Value, iniFile, "Set", "mundur"
        IniWrite cbEnter.Value, iniFile, "Set", "enter"
        IniWrite (rbKlik.Value ? "klik" : "fokus"), iniFile, "Set", "mode"
        IniWrite edX.Value, iniFile, "Set", "x"
        IniWrite edY.Value, iniFile, "Set", "y"
    } catch {
        ; diamkan bila gagal menyimpan (mis. folder read-only)
    }
}

MuatIni() {
    global iniFile, edUtama, edNomor, edStep, edTambahan, cbSpasi
    global edJeda, edBatas, edMundur, cbEnter, rbFokus, rbKlik, edX, edY
    try {
        edUtama.Value     := IniRead(iniFile, "Set", "utama", "dadang film part ")
        edNomor.Value     := IniRead(iniFile, "Set", "nomor", "3")
        edStep.Value      := IniRead(iniFile, "Set", "step", "1")
        edTambahan.Value  := IniRead(iniFile, "Set", "tambahan", "")
        cbSpasi.Value     := IniRead(iniFile, "Set", "spasi", 1)
        edJeda.Value      := IniRead(iniFile, "Set", "jeda", "2.0")
        edBatas.Value     := IniRead(iniFile, "Set", "batas", "0")
        edMundur.Value    := IniRead(iniFile, "Set", "mundur", "5")
        cbEnter.Value     := IniRead(iniFile, "Set", "enter", 0)
        mode := IniRead(iniFile, "Set", "mode", "fokus")
        if (mode = "klik")
            rbKlik.Value := 1
        else
            rbFokus.Value := 1
        edX.Value := IniRead(iniFile, "Set", "x", "")
        edY.Value := IniRead(iniFile, "Set", "y", "")
    } catch {
        ; pakai nilai bawaan bila ini rusak
    }
}

;============================================================
;  HOTKEY GLOBAL
;============================================================
F6::Mulai()
F7::StopSemua()
~Esc::StopSemua()
