"""
오버레이 타이머
- 평소엔 화면 구석에 작은 창으로 항상 위에 떠 있음 (드래그로 이동 가능)
- 시간이 다 되면 화면 전체를 덮는 알림이 뜸 (Esc / Enter / 확인 버튼으로 닫기)

사용법
- 프리셋 버튼(1·5·10·25·50분)으로 시간 설정
- 직접 입력: ✎ 버튼 또는 시간 숫자를 더블클릭 → 25(분), 1:30(1분 30초), 1:00:00(1시간), 90초 등
- 시간 숫자 위에서 마우스 휠: ±1분 / Shift+휠: ±10초
- ▶ 시작 / ⏸ 일시정지, ↺ 초기화, ✕ 종료

실행: python timer_overlay.py   (Windows에서 콘솔창 없이 쓰려면 확장자를 .pyw로 바꾸면 됨)
"""
import math
import sys
import time
import tkinter as tk

# ---- 플랫폼별 글꼴 ----
if sys.platform.startswith("win"):
    FONT, MONO = "Malgun Gothic", "Consolas"
elif sys.platform == "darwin":
    FONT, MONO = "Apple SD Gothic Neo", "Menlo"
else:
    FONT, MONO = "Noto Sans CJK KR", "DejaVu Sans Mono"

# ---- 색상 ----
BG = "#1e1e1e"
FG = "#f2f2f2"
BTN = "#333333"
BTN_HOVER = "#4a4a4a"
WARN = "#ff6b6b"
ALARM_A = "#c62828"
ALARM_B = "#7f0000"


def parse_time(text):
    """'25' → 25분, '90초'/'90s' → 90초, '1:30' → 1분30초, '1:00:00' → 1시간. 실패하면 None."""
    t = text.strip().replace("：", ":").replace(" ", "").lower()
    if not t:
        return None
    try:
        if ":" in t:
            parts = [float(x) if x else 0.0 for x in t.split(":")]
            if len(parts) == 2:
                sec = parts[0] * 60 + parts[1]
            elif len(parts) == 3:
                sec = parts[0] * 3600 + parts[1] * 60 + parts[2]
            else:
                return None
        elif t.endswith(("초", "s", "sec")):
            sec = float(t.rstrip("초sec"))
        elif t.endswith(("시간", "h")):
            sec = float(t.rstrip("시간h")) * 3600
        else:
            sec = float(t.rstrip("분min")) * 60
    except ValueError:
        return None
    sec = int(round(sec))
    return sec if 0 < sec <= 24 * 3600 else None


def fmt(seconds):
    seconds = max(0, int(math.ceil(seconds)))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.set_seconds = 5 * 60
        self.remaining = self.set_seconds
        self.end_at = None
        self.running = False
        self.tick_id = None
        self.alarm = None
        self.flash_widgets = []
        self.flash_on = False
        self.input_win = None

        # 작은 오버레이 창 설정
        root.title("타이머")
        root.overrideredirect(True)          # 테두리/제목줄 없음
        root.attributes("-topmost", True)    # 항상 위
        try:
            root.attributes("-alpha", 0.9)   # 살짝 투명
        except tk.TclError:
            pass
        root.configure(bg=BG)

        box = tk.Frame(root, bg=BG, padx=10, pady=6,
                       highlightthickness=1, highlightbackground="#444")
        box.pack()

        self.label = tk.Label(box, font=(MONO, 26, "bold"), fg=FG, bg=BG, cursor="fleur")
        self.label.pack()

        presets = tk.Frame(box, bg=BG)
        presets.pack(pady=(2, 4))
        for m in (1, 5, 10, 25, 50):
            self._btn(presets, f"{m}분", lambda m=m: self.set_minutes(m)).pack(side="left", padx=1)

        ctrl = tk.Frame(box, bg=BG)
        ctrl.pack()
        self.play_btn = self._btn(ctrl, "▶ 시작", self.toggle, width=8)
        self.play_btn.pack(side="left", padx=1)
        self._btn(ctrl, "✎", self.open_input, width=3).pack(side="left", padx=1)
        self._btn(ctrl, "↺", self.reset, width=3).pack(side="left", padx=1)
        self._btn(ctrl, "✕", root.destroy, width=3).pack(side="left", padx=1)

        # 드래그 이동
        for w in (box, self.label):
            w.bind("<ButtonPress-1>", self._drag_start)
            w.bind("<B1-Motion>", self._drag_move)

        # 시간 숫자 더블클릭 → 직접 입력
        self.label.bind("<Double-Button-1>", lambda e: self.open_input())

        # 마우스 휠로 시간 조절
        self.label.bind("<MouseWheel>", self._on_wheel)                 # Windows / macOS
        self.label.bind("<Button-4>", lambda e: self.adjust(60))        # Linux
        self.label.bind("<Button-5>", lambda e: self.adjust(-60))

        self.update_label()
        self._place_top_right()
        self._keep_on_top()

    # ---------- UI 헬퍼 ----------
    def _btn(self, parent, text, cmd, width=None):
        # 플랫폼 상관없이 같은 모양이 나오도록 Label을 버튼처럼 사용
        b = tk.Label(parent, text=text, font=(FONT, 9), bg=BTN, fg=FG,
                     padx=6, pady=2, cursor="hand2")
        if width:
            b.config(width=width)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.config(bg=BTN_HOVER))
        b.bind("<Leave>", lambda e: b.config(bg=BTN))
        return b

    def _place_top_right(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        w = self.root.winfo_width()
        self.root.geometry(f"+{sw - w - 24}+24")

    def _keep_on_top(self):
        # 다른 프로그램이 위로 올라와도 다시 맨 위로
        if self.alarm is None:
            self.root.attributes("-topmost", True)
        self.root.after(3000, self._keep_on_top)

    def _drag_start(self, e):
        self._dx = e.x_root - self.root.winfo_x()
        self._dy = e.y_root - self.root.winfo_y()

    def _drag_move(self, e):
        self.root.geometry(f"+{e.x_root - self._dx}+{e.y_root - self._dy}")

    def _on_wheel(self, e):
        step = 10 if (e.state & 0x0001) else 60   # Shift 누르면 10초 단위
        self.adjust(step if e.delta > 0 else -step)

    def update_label(self):
        self.label.config(text=fmt(self.remaining))
        warn = self.running and math.ceil(self.remaining) <= 10
        self.label.config(fg=WARN if warn else FG)

    # ---------- 타이머 동작 ----------
    def set_minutes(self, m):
        self._stop()
        self.set_seconds = m * 60
        self.remaining = self.set_seconds
        self.update_label()

    def adjust(self, delta):
        if self.running:
            self.end_at = max(time.monotonic() + 1, self.end_at + delta)
            self.remaining = self.end_at - time.monotonic()
        else:
            self.remaining = max(0, self.remaining + delta)
            self.set_seconds = self.remaining
        self.update_label()

    def toggle(self):
        if self.running:
            self.remaining = max(0, self.end_at - time.monotonic())
            self._stop()
        else:
            if self.remaining <= 0:
                self.remaining = self.set_seconds
            if self.remaining <= 0:
                return
            self.end_at = time.monotonic() + self.remaining
            self.running = True
            self.play_btn.config(text="⏸ 일시정지")
            self._tick()
        self.update_label()

    def reset(self):
        self._stop()
        self.remaining = self.set_seconds
        self.update_label()

    def _stop(self):
        self.running = False
        if self.tick_id:
            self.root.after_cancel(self.tick_id)
            self.tick_id = None
        self.play_btn.config(text="▶ 시작")

    def _tick(self):
        if not self.running:
            return
        self.remaining = max(0, self.end_at - time.monotonic())
        self.update_label()
        if self.remaining <= 0:
            self._stop()
            self.update_label()
            self.show_alarm()
        else:
            self.tick_id = self.root.after(200, self._tick)

    # ---------- 시간 직접 입력 ----------
    def open_input(self):
        if self.input_win is not None and self.input_win.winfo_exists():
            self.input_win.lift()
            self.input_win.focus_force()
            return
        d = tk.Toplevel(self.root)
        self.input_win = d
        d.title("시간 입력")
        d.configure(bg=BG)
        d.resizable(False, False)
        d.attributes("-topmost", True)

        f = tk.Frame(d, bg=BG, padx=14, pady=12)
        f.pack()
        tk.Label(f, text="시간을 입력하세요", font=(FONT, 11, "bold"), fg=FG, bg=BG).pack(anchor="w")
        tk.Label(f, text="25 → 25분   1:30 → 1분 30초   1:00:00 → 1시간   90초",
                 font=(FONT, 9), fg="#aaaaaa", bg=BG).pack(anchor="w", pady=(2, 8))

        var = tk.StringVar(value=fmt(self.set_seconds))
        entry = tk.Entry(f, textvariable=var, font=(MONO, 18), width=12, justify="center",
                         bg="#2b2b2b", fg=FG, insertbackground=FG, relief="flat")
        entry.pack(fill="x", ipady=4)
        err = tk.Label(f, text="", font=(FONT, 9), fg=WARN, bg=BG)
        err.pack(anchor="w", pady=(4, 6))

        def apply(start):
            sec = parse_time(var.get())
            if sec is None:
                err.config(text="형식을 확인해 주세요 (예: 25, 1:30, 90초)")
                return
            self._stop()
            self.set_seconds = sec
            self.remaining = sec
            self.update_label()
            close()
            if start:
                self.toggle()

        def close():
            if self.input_win is not None:
                self.input_win.destroy()
                self.input_win = None

        btns = tk.Frame(f, bg=BG)
        btns.pack(fill="x")
        self._btn(btns, "▶ 바로 시작", lambda: apply(True), width=10).pack(side="left")
        self._btn(btns, "설정만", lambda: apply(False), width=6).pack(side="left", padx=4)
        self._btn(btns, "취소", close, width=5).pack(side="right")

        d.bind("<Return>", lambda e: apply(True))
        d.bind("<Escape>", lambda e: close())
        d.protocol("WM_DELETE_WINDOW", close)

        # 타이머 창 근처에 띄우기
        d.update_idletasks()
        x = max(0, self.root.winfo_x() + self.root.winfo_width() - d.winfo_width())
        y = self.root.winfo_y() + self.root.winfo_height() + 8
        d.geometry(f"+{x}+{y}")
        d.lift()
        d.focus_force()
        entry.focus_set()
        entry.select_range(0, "end")

    # ---------- 전체화면 알림 ----------
    def show_alarm(self):
        if self.alarm:
            return
        a = tk.Toplevel(self.root)
        self.alarm = a
        a.configure(bg=ALARM_A)
        a.attributes("-topmost", True)
        try:
            a.attributes("-fullscreen", True)
        except tk.TclError:
            a.overrideredirect(True)
            a.geometry(f"{a.winfo_screenwidth()}x{a.winfo_screenheight()}+0+0")

        inner = tk.Frame(a, bg=ALARM_A)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        t1 = tk.Label(inner, text="⏰ 시간 종료!", font=(FONT, 72, "bold"), fg="white", bg=ALARM_A)
        t1.pack()
        t2 = tk.Label(inner, text=f"{fmt(self.set_seconds)} 타이머가 끝났어요",
                      font=(FONT, 24), fg="white", bg=ALARM_A)
        t2.pack(pady=(10, 30))

        btns = tk.Frame(inner, bg=ALARM_A)
        btns.pack()
        for text, cmd in (("확인", self.dismiss), ("+5분 더", self.snooze)):
            b = tk.Label(btns, text=text, font=(FONT, 18, "bold"), bg="white", fg=ALARM_B,
                         padx=28, pady=10, cursor="hand2")
            b.bind("<Button-1>", lambda e, c=cmd: c())
            b.pack(side="left", padx=12)

        t3 = tk.Label(inner, text="Esc 또는 Enter로도 닫을 수 있어요",
                      font=(FONT, 12), fg="#ffd6d6", bg=ALARM_A)
        t3.pack(pady=(24, 0))

        self.flash_widgets = [a, inner, t1, t2, btns, t3]
        for key in ("<Escape>", "<Return>", "<space>"):
            a.bind(key, lambda e: self.dismiss())

        a.lift()
        a.focus_force()
        self._flash()
        self._beep(0)

    def _flash(self):
        if not self.alarm:
            return
        self.flash_on = not self.flash_on
        color = ALARM_B if self.flash_on else ALARM_A
        for w in self.flash_widgets:
            w.config(bg=color)
        self.root.after(600, self._flash)

    def _beep(self, count):
        if not self.alarm or count >= 10:
            return
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            self.root.bell()
        self.root.after(1000, lambda: self._beep(count + 1))

    def dismiss(self):
        if self.alarm:
            self.alarm.destroy()
            self.alarm = None
        self.remaining = self.set_seconds
        self.update_label()

    def snooze(self):
        if self.alarm:
            self.alarm.destroy()
            self.alarm = None
        self.set_minutes(5)
        self.toggle()


if __name__ == "__main__":
    root = tk.Tk()
    TimerApp(root)
    root.mainloop()
