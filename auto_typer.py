# -*- coding: utf-8 -*-
"""
============================================================
  AUTO TYPER PRO  v1.2
  Aplikasi desktop ketik-otomatis dengan nomor berurutan
------------------------------------------------------------
  Contoh pemakaian:
    Teks utama : dadang film part
    Nomor awal : 3
    Hasil      : dadang film part 3
                 dadang film part 4
                 dadang film part 5   (naik terus otomatis)

  Hotkey:
    F6         : Mulai
    F7 / ESC   : Berhenti

  Dibuat dengan Python + tkinter + pynput.
  Kompatibel Windows / macOS / Linux.
============================================================
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
import json
import os
import sys

# Tampilan tajam di layar Windows beresolusi tinggi (High-DPI)
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# ------------------------------------------------------------
# Library pynput: pengendali keyboard & mouse global
# ------------------------------------------------------------
PYNPUT_OK = False
IMPORT_ERROR = ""
try:
    from pynput import keyboard as kb_mod
    from pynput.keyboard import Controller as KeyboardController, Key
    from pynput.mouse import Controller as MouseController, Button
    PYNPUT_OK = True
except Exception as _e:
    IMPORT_ERROR = str(_e)

APP_NAME = "Auto Typer Pro"
APP_VERSION = "1.2"


def app_dir():
    """Folder tempat aplikasi berada (aman juga saat sudah jadi .exe)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


SETTINGS_FILE = os.path.join(app_dir(), "auto_typer_settings.json")

# ------------------------------------------------------------
# Tema warna: dark neon
# ------------------------------------------------------------
C_BG       = "#0f1220"
C_CARD     = "#171b30"
C_LINE     = "#2a3054"
C_ACCENT   = "#00e68a"
C_ACCENT_D = "#0f9d63"
C_RED      = "#ff4d6d"
C_RED_D    = "#c7314e"
C_YELLOW   = "#ffd166"
C_TEXT     = "#eef0ff"
C_MUTED    = "#9aa0c3"
C_ENTRY    = "#232948"
C_BTN_TXT  = "#052e1d"

F_TITLE = ("Segoe UI", 17, "bold")
F_SUB   = ("Segoe UI", 9)
F_H     = ("Segoe UI", 10, "bold")
F_N     = ("Segoe UI", 10)
F_S     = ("Segoe UI", 9)
F_MONO  = ("Consolas", 11, "bold")


def compose_text(utama, nomor, tambahan, spasi_auto):
    """Menggabungkan teks utama + nomor + teks tambahan menjadi satu kalimat."""
    utama = utama or ""
    tambahan = tambahan or ""
    if spasi_auto and utama and not utama.endswith(" "):
        utama = utama + " "
    return "{}{}{}".format(utama, nomor, tambahan)


class AutoTyperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("{} v{}".format(APP_NAME, APP_VERSION))
        self.root.configure(bg=C_BG)
        self.root.geometry("560x850")
        self.root.minsize(480, 620)

        self.stop_event = threading.Event()
        self.running = False
        self.sent_count = 0
        self.saved_start_number = None
        self.targets = []  # daftar target klik: {nama,x,y,detik,ketik,enter}

        if PYNPUT_OK:
            self.kb = KeyboardController()
            self.mouse = MouseController()
            self._listener = kb_mod.Listener(on_press=self._on_key)
            self._listener.daemon = True
            self._listener.start()

        self._build_ui()
        self._load_settings()
        self._update_preview()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ================== PEMBANGUNAN TAMPILAN ==================
    def _card(self, title):
        outer = tk.Frame(self.body, bg=C_CARD,
                         highlightbackground=C_LINE, highlightthickness=1)
        outer.pack(fill="x", padx=14, pady=(8, 0))
        tk.Label(outer, text=title, bg=C_CARD, fg=C_ACCENT,
                 font=F_H, anchor="w").pack(fill="x", padx=14, pady=(10, 2))
        inner = tk.Frame(outer, bg=C_CARD)
        inner.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        return inner

    def _field(self, parent, label, initial=""):
        tk.Label(parent, text=label, bg=C_CARD, fg=C_MUTED,
                 font=F_S, anchor="w").pack(fill="x", pady=(6, 1))
        ent = tk.Entry(parent, bg=C_ENTRY, fg=C_TEXT, insertbackground=C_TEXT,
                       relief="flat", font=F_N, highlightthickness=1,
                       highlightbackground=C_LINE, highlightcolor=C_ACCENT)
        ent.pack(fill="x", ipady=6)
        if initial:
            ent.insert(0, initial)
        return ent

    def _check(self, parent, text, var, cmd=None):
        cb = tk.Checkbutton(parent, text=text, variable=var,
                            bg=C_CARD, fg=C_TEXT, activebackground=C_CARD,
                            activeforeground=C_TEXT, selectcolor=C_ENTRY,
                            font=F_S, bd=0, highlightthickness=0,
                            command=cmd, cursor="hand2", anchor="w")
        cb.pack(fill="x", pady=(8, 0))
        return cb

    def _on_wheel(self, e):
        try:
            if getattr(e, "delta", 0) > 0:
                self.canvas.yview_scroll(-1, "units")
            elif getattr(e, "delta", 0) < 0:
                self.canvas.yview_scroll(1, "units")
        except Exception:
            pass

    def _build_ui(self):
        # ----- Judul -----
        head = tk.Frame(self.root, bg=C_BG)
        head.pack(fill="x", padx=18, pady=(12, 4))
        tk.Label(head, text="AUTO TYPER PRO", bg=C_BG, fg=C_ACCENT,
                 font=F_TITLE).pack(anchor="w")
        tk.Label(head, text="Ketik teks + nomor berurutan secara otomatis",
                 bg=C_BG, fg=C_MUTED, font=F_SUB).pack(anchor="w")

        # ----- Area isi yang bisa digulir (scroll) -----
        container = tk.Frame(self.root, bg=C_BG)
        container.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(container, bg=C_BG, highlightthickness=0, bd=0)
        vsb = tk.Scrollbar(container, orient="vertical",
                           command=self.canvas.yview, width=10, bd=0,
                           elementborderwidth=0, troughcolor=C_BG)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.body = tk.Frame(self.canvas, bg=C_BG)
        self._win = self.canvas.create_window((0, 0), window=self.body,
                                              anchor="nw")
        self.body.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self._win, width=e.width))
        self.canvas.bind_all("<MouseWheel>", self._on_wheel)
        self.canvas.bind_all("<Button-4>",
                             lambda e: self.canvas.yview_scroll(-2, "units"))
        self.canvas.bind_all("<Button-5>",
                             lambda e: self.canvas.yview_scroll(2, "units"))

        # ----- Peringatan bila pynput belum terpasang -----
        if not PYNPUT_OK:
            warn = tk.Frame(self.body, bg="#3a1220",
                            highlightbackground=C_RED, highlightthickness=1)
            warn.pack(fill="x", padx=14, pady=(8, 0))
            tk.Label(warn, text="Library pynput belum terpasang!\n"
                                "Buka CMD lalu jalankan:  pip install pynput",
                     bg="#3a1220", fg=C_RED, font=F_S, wraplength=470,
                     justify="left").pack(padx=10, pady=8, anchor="w")

        # ================= 1. DATA YANG DIKETIK =================
        c1 = self._card("1. DATA YANG DIKETIK")
        self.ent_utama = self._field(c1, "TEKS UTAMA (bagian yang tetap)",
                                     "dadang film part ")
        row1 = tk.Frame(c1, bg=C_CARD)
        row1.pack(fill="x")
        kiri = tk.Frame(row1, bg=C_CARD)
        kiri.pack(side="left", expand=True, fill="x", padx=(0, 6))
        kanan = tk.Frame(row1, bg=C_CARD)
        kanan.pack(side="left", expand=True, fill="x", padx=(6, 0))
        self.ent_nomor = self._field(kiri, "NOMOR AWAL", "3")
        self.ent_step = self._field(kanan, "NAIK TIAP KALI", "1")
        self.ent_tambahan = self._field(
            c1, "TEKS TAMBAHAN SETELAH NOMOR (boleh dikosongkan)", "")
        self.spasi_var = tk.BooleanVar(value=True)
        self._check(c1, "Beri spasi otomatis sebelum nomor",
                    self.spasi_var, cmd=self._update_preview)
        self.lbl_preview = tk.Label(c1, text="", bg=C_CARD, fg=C_ACCENT,
                                    font=F_MONO, anchor="w")
        self.lbl_preview.pack(fill="x", pady=(8, 0))
        for e in (self.ent_utama, self.ent_nomor, self.ent_tambahan):
            e.bind("<KeyRelease>", lambda ev: self._update_preview())

        # ================= 2. PENGATURAN PENGIRIMAN =================
        c2 = self._card("2. PENGATURAN PENGIRIMAN")
        row2 = tk.Frame(c2, bg=C_CARD)
        row2.pack(fill="x")
        f1 = tk.Frame(row2, bg=C_CARD)
        f1.pack(side="left", expand=True, fill="x", padx=(0, 4))
        f2 = tk.Frame(row2, bg=C_CARD)
        f2.pack(side="left", expand=True, fill="x", padx=4)
        f3 = tk.Frame(row2, bg=C_CARD)
        f3.pack(side="left", expand=True, fill="x", padx=(4, 0))
        self.ent_delay = self._field(f1, "JEDA (detik)", "2.0")
        self.ent_limit = self._field(f2, "BATAS KIRIM", "0")
        self.ent_cd = self._field(f3, "MUNDUR (detik)", "5")
        tk.Label(c2, text="JEDA = jarak waktu antar pengiriman.\n"
                          "BATAS KIRIM = 0 artinya berjalan terus sampai F7.\n"
                          "MUNDUR = waktu persiapan sebelum mulai.",
                 bg=C_CARD, fg=C_MUTED, font=F_S, wraplength=470,
                 justify="left").pack(fill="x", pady=(6, 0))
        self.enter_var = tk.BooleanVar(value=False)
        self._check(c2, "Tekan Enter otomatis setelah tiap pengiriman",
                    self.enter_var)

        # ================= 3. TARGET =================
        c3 = self._card("3. TARGET (urutan klik)")
        self.lb_target = tk.Listbox(
            c3, bg=C_ENTRY, fg=C_TEXT, selectbackground=C_ACCENT,
            selectforeground=C_BTN_TXT, relief="flat", font=F_N,
            height=5, highlightthickness=1, highlightbackground=C_LINE,
            activestyle="none", exportselection=False)
        self.lb_target.pack(fill="x")
        self.lb_target.bind("<Double-Button-1>",
                            lambda ev: self._edit_target())
        rowt = tk.Frame(c3, bg=C_CARD)
        rowt.pack(fill="x", pady=(8, 0))
        self.btn_tambah = tk.Button(
            rowt, text="+ TAMBAH TARGET", command=self._tambah_target,
            bg=C_ACCENT, fg=C_BTN_TXT, font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0, cursor="hand2",
            activebackground=C_ACCENT_D, activeforeground=C_BTN_TXT)
        self.btn_tambah.pack(side="left", ipady=5, padx=(0, 6))
        self.btn_edit_t = tk.Button(
            rowt, text="EDIT", command=self._edit_target,
            bg=C_ENTRY, fg=C_TEXT, font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0, cursor="hand2",
            activebackground=C_LINE, activeforeground=C_TEXT)
        self.btn_edit_t.pack(side="left", ipady=5, padx=(0, 6))
        self.btn_hapus_t = tk.Button(
            rowt, text="HAPUS", command=self._hapus_target,
            bg=C_ENTRY, fg=C_RED, font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0, cursor="hand2",
            activebackground=C_LINE, activeforeground=C_RED)
        self.btn_hapus_t.pack(side="left", ipady=5, padx=(0, 6))
        self.btn_naik_t = tk.Button(
            rowt, text="NAIK", command=self._naik_target,
            bg=C_ENTRY, fg=C_TEXT, font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0, cursor="hand2",
            activebackground=C_LINE, activeforeground=C_TEXT)
        self.btn_naik_t.pack(side="left", ipady=5, padx=(0, 6))
        self.btn_turun_t = tk.Button(
            rowt, text="TURUN", command=self._turun_target,
            bg=C_ENTRY, fg=C_TEXT, font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0, cursor="hand2",
            activebackground=C_LINE, activeforeground=C_TEXT)
        self.btn_turun_t.pack(side="left", ipady=5)
        tk.Label(c3, text="+ TAMBAH TARGET = pilih titik klik baru. Setiap "
                          "target punya jeda detik sendiri (diatur saat "
                          "menambah).\nDaftar kosong = mengetik ke aplikasi "
                          "yang sedang fokus (mode lama).",
                 bg=C_CARD, fg=C_MUTED, font=F_S, wraplength=470,
                 justify="left").pack(fill="x", pady=(6, 0))
        self.naik_var = tk.BooleanVar(value=True)
        self._check(c3, "Nomor naik tiap selesai mengetik",
                    self.naik_var)
        tk.Label(c3, text="Matikan centang ini bila semua target memakai "
                          "nomor yang sama.",
                 bg=C_CARD, fg=C_MUTED, font=F_S, wraplength=470,
                 justify="left").pack(fill="x")

        # ================= 4. STATUS =================
        c4 = self._card("4. STATUS")
        self.lbl_status = tk.Label(
            c4, text="● Siap — isi data, klik kolom tujuan, lalu tekan F6",
            bg=C_CARD, fg=C_ACCENT, font=F_H, anchor="w",
            wraplength=470, justify="left")
        self.lbl_status.pack(fill="x")
        self.lbl_progress = tk.Label(c4, text="Terkirim: 0   |   Berikutnya: -",
                                     bg=C_CARD, fg=C_MUTED, font=F_N,
                                     anchor="w")
        self.lbl_progress.pack(fill="x", pady=(4, 0))

        # ================= TOMBOL =================
        btns = tk.Frame(self.body, bg=C_BG)
        btns.pack(fill="x", padx=14, pady=(14, 0))
        self.btn_start = tk.Button(btns, text="MULAI (F6)",
                                   command=self._start, bg=C_ACCENT,
                                   fg=C_BTN_TXT, font=("Segoe UI", 11, "bold"),
                                   relief="flat", bd=0, cursor="hand2",
                                   activebackground=C_ACCENT_D,
                                   activeforeground=C_BTN_TXT)
        self.btn_start.pack(side="left", expand=True, fill="x",
                            ipady=10, padx=(0, 6))
        self.btn_stop = tk.Button(btns, text="BERHENTI (F7)",
                                  command=self._stop, bg=C_RED, fg="white",
                                  font=("Segoe UI", 11, "bold"), relief="flat",
                                  bd=0, cursor="hand2",
                                  activebackground=C_RED_D,
                                  activeforeground="white",
                                  state="disabled",
                                  disabledforeground="#ffd0da")
        self.btn_stop.pack(side="left", expand=True, fill="x",
                           ipady=10, padx=(6, 0))
        tk.Button(self.body, text="Reset nomor ke NOMOR AWAL",
                  command=self._reset_number, bg=C_BG, fg="#b8bede", font=F_S,
                  bd=0, cursor="hand2", activebackground=C_BG,
                  activeforeground=C_TEXT).pack(pady=(8, 0))

        # ----- Footer -----
        tk.Label(self.root,
                 text="F6 = Mulai    |    F7 / ESC = Berhenti    |    "
                      "Pengaturan tersimpan otomatis",
                 bg=C_BG, fg=C_MUTED, font=F_S).pack(side="bottom", pady=8)

    # ================== HOTKEY GLOBAL ==================
    def _on_key(self, key):
        try:
            if key == kb_mod.Key.f6:
                self.root.after(0, self._start)
            elif key in (kb_mod.Key.f7, kb_mod.Key.esc):
                self.root.after(0, self._stop)
        except Exception:
            pass

    # ================== PRATINJAU ==================
    def _safe_number(self):
        try:
            return int(self.ent_nomor.get().strip())
        except ValueError:
            return 0

    def _update_preview(self, *_):
        teks = compose_text(self.ent_utama.get(), self._safe_number(),
                            self.ent_tambahan.get(), self.spasi_var.get())
        self.lbl_preview.config(text="Pratinjau :  " + teks)

    # ================== BANTU UI (THREAD-SAFE) ==================
    def _set_status(self, msg, color):
        def do():
            self.lbl_status.config(text="● " + msg, fg=color)
        self.root.after(0, do)

    def _set_progress(self, msg):
        def do():
            self.lbl_progress.config(text=msg)
        self.root.after(0, do)

    def _sleep(self, seconds):
        """Tidur yang bisa dibatalkan kapan saja lewat tombol stop."""
        end = time.time() + seconds
        while not self.stop_event.is_set():
            remain = end - time.time()
            if remain <= 0:
                break
            time.sleep(min(0.05, remain))

    def _snapshot(self):
        return {
            "utama": self.ent_utama.get(),
            "tambahan": self.ent_tambahan.get(),
            "spasi": bool(self.spasi_var.get()),
            "enter": bool(self.enter_var.get()),
            "targets": [dict(t) for t in self.targets],
            "naik_per_ketik": bool(self.naik_var.get()),
        }

    # ================== MULAI / BERHENTI ==================
    def _start(self):
        if self.running:
            return
        if not PYNPUT_OK:
            messagebox.showerror(
                APP_NAME, "Library pynput belum terpasang.\n\n"
                          "Buka CMD lalu jalankan:\n  pip install pynput")
            return
        try:
            start_num = int(self.ent_nomor.get().strip())
            step = int(self.ent_step.get().strip())
            delay = float(self.ent_delay.get().strip().replace(",", "."))
            limit = int(self.ent_limit.get().strip())
            cd = int(self.ent_cd.get().strip())
        except ValueError:
            messagebox.showwarning(
                APP_NAME,
                "NOMOR AWAL, NAIK TIAP KALI, JEDA, BATAS KIRIM, dan MUNDUR\n"
                "harus diisi dengan angka yang benar.")
            return
        if delay < 0.1:
            messagebox.showwarning(
                APP_NAME, "JEDA minimal 0.1 detik supaya sistem tetap stabil.")
            return
        if cd < 0 or cd > 60:
            messagebox.showwarning(
                APP_NAME, "MUNDUR harus antara 0 sampai 60 detik.")
            return
        self._save_settings()
        self.saved_start_number = start_num
        self.sent_count = 0
        self.stop_event.clear()
        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        snap = self._snapshot()
        threading.Thread(
            target=self._worker,
            args=(snap, start_num, step, delay, limit, cd),
            daemon=True).start()

    def _worker(self, snap, start_num, step, delay, limit, cd):
        try:
            targets = snap["targets"]
            naik = snap["naik_per_ketik"]
            nomor = start_num
            if cd > 0:
                for s in range(cd, 0, -1):
                    if self.stop_event.is_set():
                        self._finish("Dibatalkan sebelum mulai.", warn=True)
                        return
                    self._set_status(
                        "Mulai dalam {} detik — siapkan aplikasi target "
                        "di layar...".format(s), C_YELLOW)
                    self._sleep(1.0)
            self._set_status("Sedang berjalan... (tekan F7 untuk berhenti)",
                             C_ACCENT)
            while not self.stop_event.is_set():
                if limit > 0 and self.sent_count >= limit:
                    self._finish(
                        "Selesai! Total terkirim: {}".format(self.sent_count))
                    return
                if not targets:
                    # ---- daftar kosong: ketik ke aplikasi yang fokus ----
                    teks = compose_text(snap["utama"], nomor,
                                        snap["tambahan"], snap["spasi"])
                    self.kb.type(teks)
                    if snap["enter"]:
                        self.kb.press(Key.enter)
                        self.kb.release(Key.enter)
                    self.sent_count += 1
                    nomor += step
                    berikut = compose_text(snap["utama"], nomor,
                                           snap["tambahan"], snap["spasi"])
                    self._set_progress(
                        "Terkirim: {}   |   Berikutnya: {}".format(
                            self.sent_count, berikut))
                    if limit > 0 and self.sent_count >= limit:
                        self._finish(
                            "Selesai! Total terkirim: {}".format(
                                self.sent_count))
                        return
                    self._sleep(delay)
                else:
                    # ---- mode multi-target: klik tiap target berurutan ----
                    for t in targets:
                        if self.stop_event.is_set():
                            break
                        self.mouse.position = (t["x"], t["y"])
                        self.mouse.click(Button.left, 1)
                        self._sleep(0.25)
                        if self.stop_event.is_set():
                            break
                        if t["ketik"]:
                            teks = compose_text(snap["utama"], nomor,
                                                snap["tambahan"],
                                                snap["spasi"])
                            self.kb.type(teks)
                            if t["enter"]:
                                self.kb.press(Key.enter)
                                self.kb.release(Key.enter)
                            self.sent_count += 1
                            if naik:
                                nomor += step
                            berikut = compose_text(snap["utama"], nomor,
                                                   snap["tambahan"],
                                                   snap["spasi"])
                            self._set_progress(
                                "Terkirim: {}   |   Berikutnya: {}".format(
                                    self.sent_count, berikut))
                        if t["detik"] > 0:
                            self._sleep(t["detik"])
                    if self.stop_event.is_set():
                        break
                    if not naik:
                        nomor += step
                    if targets[-1]["detik"] <= 0 and delay > 0:
                        self._sleep(delay)
            self._finish(
                "Dihentikan. Total terkirim: {}".format(self.sent_count),
                warn=True)
        except Exception as e:
            self._finish("Terjadi error: {}".format(e), warn=True)

    def _finish(self, msg, warn=False):
        def do():
            self.running = False
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.lbl_status.config(text="● " + msg,
                                   fg=C_RED if warn else C_ACCENT)
        self.root.after(0, do)

    def _stop(self):
        if self.running:
            self.stop_event.set()
            self._set_status("Menghentikan...", C_YELLOW)

    def _reset_number(self):
        if self.saved_start_number is not None:
            self.ent_nomor.delete(0, "end")
            self.ent_nomor.insert(0, str(self.saved_start_number))
        self.sent_count = 0
        self._update_preview()
        self._set_progress("Terkirim: 0   |   Berikutnya: " + compose_text(
            self.ent_utama.get(), self._safe_number(),
            self.ent_tambahan.get(), self.spasi_var.get()))

    # ================== DAFTAR TARGET ==================
    def _refresh_list(self):
        self.lb_target.delete(0, "end")
        for i, t in enumerate(self.targets):
            aksi = "ketik" if t["ketik"] else "klik saja"
            ekstra = ", enter" if (t["ketik"] and t["enter"]) else ""
            self.lb_target.insert(
                "end", "{}. {}  |  ({}, {})  |  jeda {} dtk  |  {}{}".format(
                    i + 1, t["nama"], t["x"], t["y"],
                    "{:g}".format(t["detik"]), aksi, ekstra))

    def _pilihan(self):
        sel = self.lb_target.curselection()
        return sel[0] if sel else None

    def _tambah_target(self):
        self._dialog_target()

    def _edit_target(self):
        idx = self._pilihan()
        if idx is None:
            messagebox.showinfo(
                APP_NAME, "Pilih dulu target di daftar yang mau diedit.")
            return
        self._dialog_target(index=idx)

    def _hapus_target(self):
        idx = self._pilihan()
        if idx is None:
            messagebox.showinfo(
                APP_NAME, "Pilih dulu target yang mau dihapus.")
            return
        nama = self.targets[idx]["nama"]
        del self.targets[idx]
        self._refresh_list()
        self._save_settings()
        self._set_status("Target '{}' dihapus.".format(nama), C_ACCENT)

    def _naik_target(self):
        idx = self._pilihan()
        if idx is None or idx == 0:
            return
        self.targets[idx - 1], self.targets[idx] = (
            self.targets[idx], self.targets[idx - 1])
        self._refresh_list()
        self.lb_target.selection_set(idx - 1)
        self._save_settings()

    def _turun_target(self):
        idx = self._pilihan()
        if idx is None or idx >= len(self.targets) - 1:
            return
        self.targets[idx + 1], self.targets[idx] = (
            self.targets[idx], self.targets[idx + 1])
        self._refresh_list()
        self.lb_target.selection_set(idx + 1)
        self._save_settings()

    def _dialog_target(self, index=None):
        if not PYNPUT_OK:
            messagebox.showerror(
                APP_NAME, "Library pynput belum terpasang.\n\n"
                          "Buka CMD lalu jalankan:\n  pip install pynput")
            return
        baru = index is None
        dlg = tk.Toplevel(self.root)
        dlg.title("Target Baru" if baru else "Edit Target")
        dlg.configure(bg=C_BG)
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        if baru:
            t0 = {"nama": "Target {}".format(len(self.targets) + 1),
                  "x": "", "y": "", "detik": 2.0,
                  "ketik": True, "enter": False}
        else:
            t0 = self.targets[index]

        def lbl(parent, text):
            return tk.Label(parent, text=text, bg=C_BG, fg=C_MUTED,
                            font=F_S, anchor="w")

        def ent(parent, initial=""):
            e = tk.Entry(parent, bg=C_ENTRY, fg=C_TEXT,
                         insertbackground=C_TEXT, relief="flat", font=F_N,
                         highlightthickness=1, highlightbackground=C_LINE,
                         highlightcolor=C_ACCENT)
            e.pack(fill="x", ipady=6)
            if initial != "":
                e.insert(0, str(initial))
            return e

        body = tk.Frame(dlg, bg=C_BG)
        body.pack(fill="both", expand=True, padx=18, pady=(10, 4))

        head_d = tk.Label(body, text="TAMBAH TARGET BARU" if baru
                           else "EDIT TARGET", bg=C_BG, fg=C_ACCENT,
                           font=F_H, anchor="w")
        head_d.pack(fill="x", pady=(0, 8))

        lbl(body, "NAMA TARGET").pack(fill="x", pady=(0, 1))
        ent_nama = ent(body, t0["nama"])

        lbl(body, "POSISI KLIK (X dan Y)").pack(fill="x", pady=(8, 1))
        rowxy = tk.Frame(body, bg=C_BG)
        rowxy.pack(fill="x")
        fx = tk.Frame(rowxy, bg=C_BG)
        fx.pack(side="left", expand=True, fill="x", padx=(0, 4))
        fy = tk.Frame(rowxy, bg=C_BG)
        fy.pack(side="left", expand=True, fill="x", padx=(0, 4))
        tk.Label(fx, text="X", bg=C_BG, fg=C_MUTED, font=F_S,
                 anchor="w").pack(fill="x")
        ent_x = ent(fx, t0["x"])
        tk.Label(fy, text="Y", bg=C_BG, fg=C_MUTED, font=F_S,
                 anchor="w").pack(fill="x")
        ent_y = ent(fy, t0["y"])
        btn_ambil = tk.Button(rowxy, text="AMBIL\nPOSISI",
                              bg=C_ENTRY, fg=C_ACCENT,
                              font=("Segoe UI", 9, "bold"), relief="flat",
                              bd=0, cursor="hand2", activebackground=C_LINE,
                              activeforeground=C_ACCENT, justify="center")
        btn_ambil.pack(side="left", fill="y")

        lbl(body, "JEDA SETELAH TARGET INI (detik)").pack(fill="x",
                                                          pady=(8, 1))
        ent_detik = ent(body, "{:g}".format(float(t0["detik"])))

        var_ketik = tk.BooleanVar(value=bool(t0["ketik"]))
        var_enter = tk.BooleanVar(value=bool(t0["enter"]))
        tk.Checkbutton(body, text="Ketik teks di target ini (matikan bila "
                                  "hanya ingin klik tombol)",
                       variable=var_ketik, bg=C_BG, fg=C_TEXT,
                       activebackground=C_BG, activeforeground=C_TEXT,
                       selectcolor=C_ENTRY, font=F_S, bd=0,
                       highlightthickness=0, cursor="hand2",
                       anchor="w").pack(fill="x", pady=(8, 0))
        tk.Checkbutton(body, text="Tekan Enter setelah mengetik di target ini",
                       variable=var_enter, bg=C_BG, fg=C_TEXT,
                       activebackground=C_BG, activeforeground=C_TEXT,
                       selectcolor=C_ENTRY, font=F_S, bd=0,
                       highlightthickness=0, cursor="hand2",
                       anchor="w").pack(fill="x", pady=(4, 0))

        lbl_ambil = tk.Label(body, text="", bg=C_BG, fg=C_YELLOW, font=F_S,
                             anchor="w", wraplength=470, justify="left")
        lbl_ambil.pack(fill="x", pady=(8, 0))

        def ambil():
            def kerja():
                try:
                    for s in range(5, 0, -1):
                        dlg.after(0, lambda s=s: lbl_ambil.config(
                            text="Arahkan mouse ke titik target dan "
                                 "diamkan... {}".format(s)))
                        time.sleep(1)
                    px, py = self.mouse.position

                    def isi():
                        ent_x.delete(0, "end")
                        ent_x.insert(0, str(px))
                        ent_y.delete(0, "end")
                        ent_y.insert(0, str(py))
                        lbl_ambil.config(text="Posisi tersimpan: X={}, Y={}"
                                         .format(px, py))

                    dlg.after(0, isi)
                except Exception:
                    pass
            threading.Thread(target=kerja, daemon=True).start()

        btn_ambil.config(command=ambil)

        def batal():
            dlg.grab_release()
            dlg.destroy()

        def simpan():
            try:
                x = int(ent_x.get().strip())
                y = int(ent_y.get().strip())
                detik = float(ent_detik.get().strip().replace(",", "."))
            except ValueError:
                messagebox.showwarning(
                    APP_NAME,
                    "POSISI X dan Y harus angka bulat,\n"
                    "JEDA harus berupa angka.", parent=dlg)
                return
            if detik < 0:
                detik = 0.0
            data = {
                "nama": ent_nama.get().strip() or "Target",
                "x": x, "y": y, "detik": detik,
                "ketik": bool(var_ketik.get()),
                "enter": bool(var_enter.get()),
            }
            if baru:
                self.targets.append(data)
            else:
                self.targets[index] = data
            self._refresh_list()
            self._save_settings()
            dlg.grab_release()
            dlg.destroy()
            self._set_status("Target '{}' tersimpan. Tekan F6 untuk mulai."
                             .format(data["nama"]), C_ACCENT)

        btnrow = tk.Frame(body, bg=C_BG)
        btnrow.pack(fill="x", pady=(12, 6))
        tk.Button(btnrow, text="SIMPAN", command=simpan, bg=C_ACCENT,
                  fg=C_BTN_TXT, font=("Segoe UI", 10, "bold"), relief="flat",
                  bd=0, cursor="hand2", activebackground=C_ACCENT_D,
                  activeforeground=C_BTN_TXT).pack(
                      side="left", expand=True, fill="x", ipady=8,
                      padx=(0, 6))
        tk.Button(btnrow, text="BATALKAN", command=batal, bg=C_ENTRY,
                  fg=C_TEXT, font=("Segoe UI", 10, "bold"), relief="flat",
                  bd=0, cursor="hand2", activebackground=C_LINE,
                  activeforeground=C_TEXT).pack(
                      side="left", expand=True, fill="x", ipady=8,
                      padx=(6, 0))
        ent_nama.focus_set()

    # ================== SIMPAN / MUAT PENGATURAN ==================
    def _save_settings(self):
        data = {
            "utama": self.ent_utama.get(),
            "nomor": self.ent_nomor.get(),
            "step": self.ent_step.get(),
            "tambahan": self.ent_tambahan.get(),
            "spasi": bool(self.spasi_var.get()),
            "delay": self.ent_delay.get(),
            "limit": self.ent_limit.get(),
            "cd": self.ent_cd.get(),
            "enter": bool(self.enter_var.get()),
            "targets": self.targets,
            "naik": bool(self.naik_var.get()),
        }
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            return
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return
        if not isinstance(data, dict):
            return
        pasangan = [
            ("utama", self.ent_utama), ("nomor", self.ent_nomor),
            ("step", self.ent_step), ("tambahan", self.ent_tambahan),
            ("delay", self.ent_delay), ("limit", self.ent_limit),
            ("cd", self.ent_cd),
        ]
        for key, ent in pasangan:
            val = data.get(key)
            if val is not None:
                ent.delete(0, "end")
                ent.insert(0, str(val))
        self.spasi_var.set(bool(data.get("spasi", True)))
        self.enter_var.set(bool(data.get("enter", False)))
        self.naik_var.set(bool(data.get("naik", True)))
        ts = data.get("targets")
        if isinstance(ts, list):
            self.targets = []
            for t in ts:
                if not isinstance(t, dict):
                    continue
                try:
                    x = int(t.get("x"))
                    y = int(t.get("y"))
                    d = float(t.get("detik", 0))
                except (TypeError, ValueError):
                    continue
                self.targets.append({
                    "nama": str(t.get("nama") or "Target"),
                    "x": x, "y": y, "detik": d,
                    "ketik": bool(t.get("ketik", True)),
                    "enter": bool(t.get("enter", False))})
            self._refresh_list()

    def _on_close(self):
        try:
            self._save_settings()
            if self.running:
                self.stop_event.set()
            if PYNPUT_OK and hasattr(self, "_listener"):
                self._listener.stop()
        finally:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = AutoTyperApp(root)
    if "--selftest" in sys.argv:
        def _ok():
            print("SELFTEST_OK")
            root.destroy()
        root.after(1800, _ok)
    if "--selftest-dialog" in sys.argv:
        def _dlg():
            app._dialog_target()
        root.after(1000, _dlg)

        def _ok2():
            print("SELFTEST_DIALOG_OK")
            root.destroy()
        root.after(4500, _ok2)
    root.mainloop()
    if ("--selftest" in sys.argv) or ("--selftest-dialog" in sys.argv):
        print("SELFTEST_DONE")


if __name__ == "__main__":
    main()
