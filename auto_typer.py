# -*- coding: utf-8 -*-
"""
============================================================
  AUTO TYPER PRO  v1.0
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
APP_VERSION = "1.0"


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
        self._capturing = False

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

    def _radio(self, parent, text, value):
        rb = tk.Radiobutton(parent, text=text, variable=self.mode_var,
                            value=value, bg=C_CARD, fg=C_TEXT,
                            activebackground=C_CARD, activeforeground=C_TEXT,
                            selectcolor=C_ENTRY, font=F_S, bd=0,
                            highlightthickness=0, cursor="hand2", anchor="w")
        rb.pack(fill="x")
        return rb

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
        c3 = self._card("3. TARGET")
        self.mode_var = tk.StringVar(value="fokus")
        self._radio(c3, "Ketik ke aplikasi yang sedang fokus "
                        "(klik dulu kolom tujuan)", "fokus")
        self._radio(c3, "Klik posisi layar tertentu dulu, baru ketik", "klik")
        row3 = tk.Frame(c3, bg=C_CARD)
        row3.pack(fill="x", pady=(6, 0))
        fx = tk.Frame(row3, bg=C_CARD)
        fx.pack(side="left", expand=True, fill="x", padx=(0, 4))
        fy = tk.Frame(row3, bg=C_CARD)
        fy.pack(side="left", expand=True, fill="x", padx=(0, 4))
        self.ent_x = self._field(fx, "POSISI X", "")
        self.ent_y = self._field(fy, "POSISI Y", "")
        btn_cap = tk.Button(row3, text="AMBIL\nPOSISI",
                            command=self._capture_position,
                            bg=C_ENTRY, fg=C_ACCENT,
                            font=("Segoe UI", 9, "bold"), relief="flat",
                            bd=0, cursor="hand2", activebackground=C_LINE,
                            activeforeground=C_ACCENT, justify="center")
        btn_cap.pack(side="left", fill="y", padx=(4, 0))
        tk.Label(c3, text="Tekan AMBIL POSISI, lalu arahkan mouse ke titik "
                          "target dan diamkan 5 detik.",
                 bg=C_CARD, fg=C_MUTED, font=F_S, wraplength=470,
                 justify="left").pack(fill="x", pady=(6, 0))

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
        mode = self.mode_var.get()
        x = y = None
        if mode == "klik":
            try:
                x = int(self.ent_x.get().strip())
                y = int(self.ent_y.get().strip())
            except ValueError:
                messagebox.showwarning(
                    APP_NAME, "Mode klik: isi POSISI X dan Y dulu,\n"
                              "atau tekan tombol AMBIL POSISI.")
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
            args=(snap, start_num, step, delay, limit, cd, mode, x, y),
            daemon=True).start()

    def _worker(self, snap, start_num, step, delay, limit, cd, mode, x, y):
        try:
            nomor = start_num
            if cd > 0:
                for s in range(cd, 0, -1):
                    if self.stop_event.is_set():
                        self._finish("Dibatalkan sebelum mulai.", warn=True)
                        return
                    self._set_status(
                        "Mulai dalam {} detik — segera fokuskan kolom "
                        "tujuan di aplikasi target...".format(s), C_YELLOW)
                    self._sleep(1.0)
            self._set_status("Sedang berjalan... (tekan F7 untuk berhenti)",
                             C_ACCENT)
            while not self.stop_event.is_set():
                if limit > 0 and self.sent_count >= limit:
                    self._finish(
                        "Selesai! Total terkirim: {}".format(self.sent_count))
                    return
                teks = compose_text(snap["utama"], nomor,
                                    snap["tambahan"], snap["spasi"])
                if mode == "klik":
                    self.mouse.position = (x, y)
                    self.mouse.click(Button.left, 1)
                    self._sleep(0.25)
                    if self.stop_event.is_set():
                        break
                self.kb.type(teks)
                if snap["enter"]:
                    self.kb.press(Key.enter)
                    self.kb.release(Key.enter)
                self.sent_count += 1
                nomor += step
                berikut = compose_text(snap["utama"], nomor,
                                       snap["tambahan"], snap["spasi"])
                self._set_progress("Terkirim: {}   |   Berikutnya: {}".format(
                    self.sent_count, berikut))
                if limit > 0 and self.sent_count >= limit:
                    self._finish(
                        "Selesai! Total terkirim: {}".format(self.sent_count))
                    return
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

    # ================== AMBIL POSISI MOUSE ==================
    def _capture_position(self):
        if self._capturing or not PYNPUT_OK:
            return
        self._capturing = True
        threading.Thread(target=self._capture_worker, daemon=True).start()

    def _capture_worker(self):
        try:
            for s in range(5, 0, -1):
                self._set_status(
                    "Arahkan mouse ke titik target dan diamkan... "
                    "{}".format(s), C_YELLOW)
                time.sleep(1)
            px, py = self.mouse.position
            self.root.after(0, self._fill_xy, px, py)
        finally:
            self._capturing = False

    def _fill_xy(self, x, y):
        self.ent_x.delete(0, "end")
        self.ent_x.insert(0, str(x))
        self.ent_y.delete(0, "end")
        self.ent_y.insert(0, str(y))
        self._set_status(
            "Posisi tersimpan: X={}, Y={}. Tekan F6 untuk mulai.".format(x, y),
            C_ACCENT)

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
            "mode": self.mode_var.get(),
            "x": self.ent_x.get(),
            "y": self.ent_y.get(),
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
            ("cd", self.ent_cd), ("x", self.ent_x), ("y", self.ent_y),
        ]
        for key, ent in pasangan:
            val = data.get(key)
            if val is not None:
                ent.delete(0, "end")
                ent.insert(0, str(val))
        self.spasi_var.set(bool(data.get("spasi", True)))
        self.enter_var.set(bool(data.get("enter", False)))
        mode = data.get("mode", "fokus")
        self.mode_var.set(mode if mode in ("fokus", "klik") else "fokus")

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
    AutoTyperApp(root)
    if "--selftest" in sys.argv:
        def _ok():
            print("SELFTEST_OK")
            root.destroy()
        root.after(1800, _ok)
    root.mainloop()
    if "--selftest" in sys.argv:
        print("SELFTEST_DONE")


if __name__ == "__main__":
    main()
