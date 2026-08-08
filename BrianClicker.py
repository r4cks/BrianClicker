import ctypes
import os
import sys
import time
import threading
from collections import deque
from ctypes import wintypes

import customtkinter as ctk
from PIL import Image


# ============================================================
# RESOURCE PATH
# ============================================================

def resource_path(filename):
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base, filename)


# ============================================================
# APPLICATION ID
# ============================================================

try:
    shell32 = ctypes.WinDLL(
        "shell32",
        use_last_error=True
    )

    shell32.SetCurrentProcessExplicitAppUserModelID(
        "BrianClicker.BrianClicker"
    )

except Exception:
    pass


# ============================================================
# APPEARANCE
# ============================================================

ctk.set_appearance_mode("Dark")

BG = "#000000"
WHITE = "#FFFFFF"
DARK = "#090909"
GRAY = "#151515"
BORDER = "#202020"


# ============================================================
# WINDOWS API
# ============================================================

user32 = ctypes.WinDLL(
    "user32",
    use_last_error=True
)

kernel32 = ctypes.WinDLL(
    "kernel32",
    use_last_error=True
)


# ============================================================
# WINDOWS CONSTANTS
# ============================================================

GWL_STYLE = -16
GWL_EXSTYLE = -20

WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WS_SYSMENU = 0x00080000

WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000

SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_FRAMECHANGED = 0x0020
SWP_NOACTIVATE = 0x0010

HWND_TOP = 0
SW_SHOW = 5

# Mouse
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

# Keyboard
KEYEVENTF_KEYUP = 0x0002

# Keyboard hook
WH_KEYBOARD_LL = 13

WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104

LLKHF_INJECTED = 0x00000010

LRESULT = ctypes.c_ssize_t


# ============================================================
# WINDOWS FUNCTION DEFINITIONS
# ============================================================

user32.GetWindowLongW.argtypes = [
    wintypes.HWND,
    ctypes.c_int
]
user32.GetWindowLongW.restype = ctypes.c_long

user32.SetWindowLongW.argtypes = [
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_long
]
user32.SetWindowLongW.restype = ctypes.c_long

user32.SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_uint
]
user32.SetWindowPos.restype = wintypes.BOOL

user32.ShowWindow.argtypes = [
    wintypes.HWND,
    ctypes.c_int
]
user32.ShowWindow.restype = wintypes.BOOL

user32.GetAsyncKeyState.argtypes = [
    ctypes.c_int
]
user32.GetAsyncKeyState.restype = ctypes.c_short

user32.SetWindowsHookExW.argtypes = [
    ctypes.c_int,
    ctypes.c_void_p,
    wintypes.HINSTANCE,
    wintypes.DWORD
]
user32.SetWindowsHookExW.restype = wintypes.HHOOK

user32.UnhookWindowsHookEx.argtypes = [
    wintypes.HHOOK
]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL

user32.CallNextHookEx.argtypes = [
    wintypes.HHOOK,
    ctypes.c_int,
    wintypes.WPARAM,
    wintypes.LPARAM
]
user32.CallNextHookEx.restype = LRESULT

user32.GetMessageW.argtypes = [
    ctypes.POINTER(wintypes.MSG),
    wintypes.HWND,
    wintypes.UINT,
    wintypes.UINT
]
user32.GetMessageW.restype = ctypes.c_int

user32.TranslateMessage.argtypes = [
    ctypes.POINTER(wintypes.MSG)
]
user32.TranslateMessage.restype = wintypes.BOOL

user32.DispatchMessageW.argtypes = [
    ctypes.POINTER(wintypes.MSG)
]
user32.DispatchMessageW.restype = LRESULT

user32.PostQuitMessage.argtypes = [
    ctypes.c_int
]
user32.PostQuitMessage.restype = None

kernel32.GetModuleHandleW.argtypes = [
    wintypes.LPCWSTR
]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE


# ============================================================
# KEYBOARD STRUCTURE
# ============================================================

class KBDLLHOOKSTRUCT(ctypes.Structure):

    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


HOOKPROC = ctypes.WINFUNCTYPE(
    LRESULT,
    ctypes.c_int,
    wintypes.WPARAM,
    wintypes.LPARAM
)


# ============================================================
# VIRTUAL KEYS
# ============================================================

VK_LBUTTON = 0x01
VK_R = 0x52

VK_6 = 0x36
VK_7 = 0x37
VK_8 = 0x38
VK_9 = 0x39
VK_0 = 0x30

VK_CAPSLOCK = 0x14
VK_F8 = 0x77


# ============================================================
# STATE
# ============================================================

running = True
enabled = False
physical_lmb = False

expanded = False
cps_value = 12

waiting_for_key = None

state_lock = threading.Lock()
click_event = threading.Event()

click_times = deque()
click_times_lock = threading.Lock()


# ============================================================
# KEYBINDS
# ============================================================

keybinds = {
    "6": {"input": None, "output": VK_6},
    "7": {"input": None, "output": VK_7},
    "8": {"input": None, "output": VK_8},
    "9": {"input": None, "output": VK_9},
    "0": {"input": None, "output": VK_0},
}


# ============================================================
# MAIN WINDOW
# ============================================================

app = ctk.CTk()

app.title("Brian Clicker")
app.resizable(False, False)
app.configure(fg_color=BORDER)


# ============================================================
# BORDERLESS WINDOWS STYLE
# ============================================================

def remove_windows_titlebar():

    app.update_idletasks()

    hwnd = app.winfo_id()

    style = user32.GetWindowLongW(
        hwnd,
        GWL_STYLE
    )

    ex_style = user32.GetWindowLongW(
        hwnd,
        GWL_EXSTYLE
    )

    style &= ~WS_CAPTION
    style &= ~WS_THICKFRAME
    style &= ~WS_MINIMIZEBOX
    style &= ~WS_MAXIMIZEBOX
    style &= ~WS_SYSMENU

    # Keep the application in the Windows taskbar.
    ex_style &= ~WS_EX_TOOLWINDOW
    ex_style |= WS_EX_APPWINDOW

    user32.SetWindowLongW(
        hwnd,
        GWL_STYLE,
        style
    )

    user32.SetWindowLongW(
        hwnd,
        GWL_EXSTYLE,
        ex_style
    )

    user32.SetWindowPos(
        hwnd,
        HWND_TOP,
        0,
        0,
        0,
        0,
        SWP_NOMOVE
        | SWP_NOSIZE
        | SWP_NOZORDER
        | SWP_NOACTIVATE
        | SWP_FRAMECHANGED
    )

    user32.ShowWindow(
        hwnd,
        SW_SHOW
    )


# ============================================================
# DRAGGING
# ============================================================

drag_x = 0
drag_y = 0


def start_drag(event):

    global drag_x
    global drag_y

    drag_x = (
        event.x_root
        - app.winfo_x()
    )

    drag_y = (
        event.y_root
        - app.winfo_y()
    )


def drag_window(event):

    x = (
        event.x_root
        - drag_x
    )

    y = (
        event.y_root
        - drag_y
    )

    app.geometry(
        f"+{x}+{y}"
    )


# ============================================================
# POWER
# ============================================================

def update_power_visual():

    if enabled:

        power_button.configure(
            fg_color=WHITE,
            hover_color="#DDDDDD",
            text_color=BG
        )

    else:

        power_button.configure(
            fg_color=BG,
            hover_color="#222222",
            text_color=WHITE
        )


def toggle_power():

    global enabled

    with state_lock:
        enabled = not enabled

    update_power_visual()
    click_event.set()


# ============================================================
# OVERLAY
# ============================================================

def toggle_overlay():

    app.attributes(
        "-topmost",
        bool(overlay_var.get())
    )


# ============================================================
# RESIZE
# ============================================================

def resize_window():

    app.update_idletasks()

    width = 400
    height = app.winfo_reqheight()

    app.geometry(
        f"{width}x{height}"
    )


# ============================================================
# EXPAND
# ============================================================

def toggle_expand():

    global expanded

    expanded = not expanded

    if expanded:

        settings_frame.pack(
            fill="x",
            padx=20,
            pady=(8, 5),
            before=expand_button
        )

        expand_button.configure(
            text="▲"
        )

    else:

        settings_frame.pack_forget()

        expand_button.configure(
            text="▼"
        )

    resize_window()


# ============================================================
# CPS
# ============================================================

def update_cps(value):

    global cps_value

    cps_value = int(float(value))

    cps_value_label.configure(
        text=f"{cps_value} CPS"
    )

    click_event.set()


# ============================================================
# SEND CLICK
# ============================================================

def send_left_click():

    user32.mouse_event(
        MOUSEEVENTF_LEFTDOWN,
        0,
        0,
        0,
        0
    )

    user32.mouse_event(
        MOUSEEVENTF_LEFTUP,
        0,
        0,
        0,
        0
    )


# ============================================================
# SEND KEY
# ============================================================

def send_key(vk):

    user32.keybd_event(
        vk,
        0,
        0,
        0
    )

    user32.keybd_event(
        vk,
        0,
        KEYEVENTF_KEYUP,
        0
    )


# ============================================================
# MOUSE MONITOR
# ============================================================

def mouse_state_monitor():

    global physical_lmb

    previous = False

    while running:

        current = bool(
            user32.GetAsyncKeyState(
                VK_LBUTTON
            ) & 0x8000
        )

        if current != previous:

            with state_lock:
                physical_lmb = current

            previous = current
            click_event.set()

        time.sleep(0.001)


# ============================================================
# AUTOCLICKER
# ============================================================

def autoclicker():

    next_click = time.perf_counter()

    while running:

        with state_lock:

            active = (
                enabled
                and physical_lmb
            )

            current_cps = cps_value

        interval = (
            1.0
            / max(current_cps, 1)
        )

        if not active:

            click_event.wait(0.01)
            click_event.clear()

            next_click = (
                time.perf_counter()
                + interval
            )

            continue

        now = time.perf_counter()

        if now < next_click:

            remaining = (
                next_click
                - now
            )

            if remaining > 0.002:

                time.sleep(
                    remaining - 0.001
                )

            continue

        send_left_click()

        click_time = time.perf_counter()

        with click_times_lock:

            click_times.append(
                click_time
            )

        next_click += interval

        now = time.perf_counter()

        if now > (
            next_click
            + interval * 3
        ):

            next_click = (
                now
                + interval
            )


# ============================================================
# LIVE CPS
# ============================================================

def cps_monitor():

    while running:

        now = time.perf_counter()
        cutoff = now - 1.0

        with click_times_lock:

            while (
                click_times
                and click_times[0] < cutoff
            ):

                click_times.popleft()

            live_cps = len(click_times)

        with state_lock:

            active = (
                enabled
                and physical_lmb
            )

        if not active:
            live_cps = 0

        try:

            app.after(
                0,
                lambda value=live_cps:
                cps_label.configure(
                    text=f"{value:02d} CPS"
                )
            )

        except Exception:

            break

        time.sleep(0.1)


# ============================================================
# KEY NAME
# ============================================================

def get_key_name(vk):

    names = {

        0x08: "BACKSPACE",
        0x09: "TAB",
        0x0D: "ENTER",
        0x10: "SHIFT",
        0x11: "CTRL",
        0x12: "ALT",
        0x14: "CAPS LOCK",
        0x1B: "ESC",
        0x20: "SPACE",

        0x70: "F1",
        0x71: "F2",
        0x72: "F3",
        0x73: "F4",
        0x74: "F5",
        0x75: "F6",
        0x76: "F7",
        0x77: "F8",
        0x78: "F9",
        0x79: "F10",
        0x7A: "F11",
        0x7B: "F12",
    }

    if vk in names:
        return names[vk]

    if 0x30 <= vk <= 0x39:
        return chr(vk)

    if 0x41 <= vk <= 0x5A:
        return chr(vk)

    return f"VK {vk}"


# ============================================================
# KEYBIND UI
# ============================================================

keybind_buttons = {}


def update_keybind_button(number):

    input_vk = keybinds[number]["input"]

    if input_vk is None:
        text = "UNBOUND"
    else:
        text = get_key_name(input_vk)

    keybind_buttons[number].configure(
        text=text
    )


def begin_key_capture(number):

    global waiting_for_key

    waiting_for_key = number

    keybind_buttons[number].configure(
        text="PRESS KEY..."
    )


# ============================================================
# KEYBOARD HOOK
# ============================================================

@HOOKPROC
def keyboard_hook(
    nCode,
    wParam,
    lParam
):

    global running
    global enabled
    global waiting_for_key

    if nCode < 0:

        return user32.CallNextHookEx(
            None,
            nCode,
            wParam,
            lParam
        )

    data = ctypes.cast(
        lParam,
        ctypes.POINTER(
            KBDLLHOOKSTRUCT
        )
    ).contents

    vk = data.vkCode
    flags = data.flags

    injected = bool(
        flags & LLKHF_INJECTED
    )

    is_down = (
        wParam == WM_KEYDOWN
        or
        wParam == WM_SYSKEYDOWN
    )

    # --------------------------------------------------------
    # KEY CAPTURE
    # --------------------------------------------------------

    if (
        waiting_for_key is not None
        and not injected
        and is_down
    ):

        number = waiting_for_key

        if vk != VK_F8:

            keybinds[number]["input"] = vk

        waiting_for_key = None

        app.after(
            0,
            lambda n=number:
            update_keybind_button(n)
        )

        return 1

    # --------------------------------------------------------
    # CAPS LOCK
    # --------------------------------------------------------

    if (
        vk == VK_CAPSLOCK
        and not injected
        and is_down
    ):

        with state_lock:
            enabled = not enabled

        app.after(
            0,
            update_power_visual
        )

        click_event.set()

        return 1

    # --------------------------------------------------------
    # R -> 7
    # --------------------------------------------------------

    if (
        vk == VK_R
        and not injected
        and is_down
    ):

        send_key(VK_7)

        return 1

    # --------------------------------------------------------
    # 6-0 KEYBINDS
    # --------------------------------------------------------

    if (
        not injected
        and is_down
    ):

        for number, bind in keybinds.items():

            input_vk = bind["input"]
            output_vk = bind["output"]

            if (
                input_vk is not None
                and
                vk == input_vk
            ):

                send_key(output_vk)

                return 1

    # --------------------------------------------------------
    # F8 CLOSE
    # --------------------------------------------------------

    if (
        vk == VK_F8
        and not injected
        and is_down
    ):

        running = False
        click_event.set()

        user32.PostQuitMessage(0)

        app.after(
            0,
            shutdown
        )

        return 1

    return user32.CallNextHookEx(
        None,
        nCode,
        wParam,
        lParam
    )


# ============================================================
# KEYBOARD HOOK THREAD
# ============================================================

def keyboard_hook_thread():

    global running

    module_handle = (
        kernel32.GetModuleHandleW(None)
    )

    if not module_handle:

        running = False
        return

    hook = user32.SetWindowsHookExW(
        WH_KEYBOARD_LL,
        keyboard_hook,
        module_handle,
        0
    )

    if not hook:

        running = False
        return

    msg = wintypes.MSG()

    while running:

        result = user32.GetMessageW(
            ctypes.byref(msg),
            None,
            0,
            0
        )

        if result <= 0:
            break

        user32.TranslateMessage(
            ctypes.byref(msg)
        )

        user32.DispatchMessageW(
            ctypes.byref(msg)
        )

    user32.UnhookWindowsHookEx(
        hook
    )


# ============================================================
# MAIN FRAME
# ============================================================

main_frame = ctk.CTkFrame(
    app,
    fg_color=BG,
    corner_radius=0
)

main_frame.pack(
    padx=2,
    pady=2,
    fill="both",
    expand=True
)


# ============================================================
# DRAG BAR
# ============================================================

drag_bar = ctk.CTkFrame(
    main_frame,
    height=7,
    fg_color=BORDER,
    corner_radius=0
)

drag_bar.pack(
    fill="x",
    side="top"
)

drag_bar.bind(
    "<Button-1>",
    start_drag
)

drag_bar.bind(
    "<B1-Motion>",
    drag_window
)


# ============================================================
# TOP SECTION
# ============================================================

top_frame = ctk.CTkFrame(
    main_frame,
    fg_color="transparent"
)

top_frame.pack(
    fill="x",
    padx=20,
    pady=(7, 5)
)


# ============================================================
# POWER BUTTON
# ============================================================

power_button = ctk.CTkButton(
    top_frame,
    text="⏻",
    width=85,
    height=75,
    corner_radius=15,
    font=("Arial", 38, "bold"),
    fg_color=BG,
    hover_color="#222222",
    text_color=WHITE,
    border_width=2,
    border_color=WHITE,
    command=toggle_power
)

power_button.grid(
    row=0,
    column=0,
    padx=(0, 15),
    pady=(5, 0),
    sticky="w"
)


# ============================================================
# CPS LABEL
# ============================================================

cps_label = ctk.CTkLabel(
    top_frame,
    text="00 CPS",
    font=("Arial", 18, "bold"),
    text_color=WHITE
)

cps_label.grid(
    row=1,
    column=0,
    padx=(0, 15),
    pady=(4, 0),
    sticky="w"
)


# ============================================================
# LOGO
# ============================================================

logo_path = resource_path(
    "logo.png"
)

try:

    logo_pil = Image.open(
        logo_path
    )

    logo_pil.load()

    logo_image = ctk.CTkImage(
        light_image=logo_pil,
        dark_image=logo_pil,
        size=(230, 90)
    )

    logo = ctk.CTkLabel(
        top_frame,
        image=logo_image,
        text=""
    )

except Exception:

    logo = ctk.CTkLabel(
        top_frame,
        text="BRIAN",
        font=("Arial", 32, "bold"),
        text_color=WHITE
    )


logo.grid(
    row=0,
    column=1,
    padx=(5, 0)
)


# ============================================================
# NAME
# ============================================================

name_label = ctk.CTkLabel(
    top_frame,
    text="Brian Clicker",
    font=("Arial", 20, "bold"),
    text_color=WHITE
)

name_label.grid(
    row=1,
    column=1,
    pady=(2, 0)
)


# ============================================================
# EXPAND BUTTON
# ============================================================

expand_button = ctk.CTkButton(
    main_frame,
    text="▼",
    width=45,
    height=25,
    corner_radius=8,
    font=("Arial", 14, "bold"),
    fg_color=GRAY,
    hover_color="#444444",
    text_color=WHITE,
    command=toggle_expand
)

expand_button.pack(
    pady=(5, 5)
)


# ============================================================
# SETTINGS FRAME
# ============================================================

settings_frame = ctk.CTkFrame(
    main_frame,
    fg_color=DARK,
    corner_radius=12
)


# ============================================================
# CPS SETTINGS
# ============================================================

range_title = ctk.CTkLabel(
    settings_frame,
    text="CPS",
    font=("Arial", 17, "bold"),
    text_color=WHITE
)

range_title.pack(
    pady=(15, 5)
)


cps_value_label = ctk.CTkLabel(
    settings_frame,
    text="12 CPS",
    font=("Arial", 15, "bold"),
    text_color=WHITE
)

cps_value_label.pack(
    pady=3
)


cps_slider = ctk.CTkSlider(
    settings_frame,
    from_=1,
    to=50,
    number_of_steps=49,
    width=280,
    height=15,
    fg_color="#333333",
    progress_color=WHITE,
    button_color=WHITE,
    button_hover_color="#DDDDDD",
    command=update_cps
)

cps_slider.set(12)

cps_slider.pack(
    pady=(0, 15)
)


# ============================================================
# OVERLAY
# ============================================================

overlay_var = ctk.BooleanVar(
    value=False
)

overlay_checkbox = ctk.CTkCheckBox(
    settings_frame,
    text="OVERLAY",
    variable=overlay_var,
    font=("Arial", 15, "bold"),
    text_color=WHITE,
    fg_color=WHITE,
    hover_color="#DDDDDD",
    border_color=WHITE,
    checkmark_color=BG,
    command=toggle_overlay
)

overlay_checkbox.pack(
    pady=8
)


# ============================================================
# TOGGLE DISPLAY
# ============================================================

toggle_title = ctk.CTkLabel(
    settings_frame,
    text="TOGGLE AUTOCLICKER",
    font=("Arial", 15, "bold"),
    text_color=WHITE
)

toggle_title.pack(
    pady=(12, 5)
)


toggle_display = ctk.CTkButton(
    settings_frame,
    text="CAPS LOCK",
    width=190,
    height=38,
    corner_radius=10,
    font=("Arial", 14, "bold"),
    fg_color=WHITE,
    hover_color=WHITE,
    text_color=BG,
    state="disabled"
)

toggle_display.pack(
    pady=(0, 15)
)


# ============================================================
# KEYBINDS
# ============================================================

keybind_title = ctk.CTkLabel(
    settings_frame,
    text="KEYBINDS",
    font=("Arial", 17, "bold"),
    text_color=WHITE
)

keybind_title.pack(
    pady=(5, 8)
)


keybind_frame = ctk.CTkFrame(
    settings_frame,
    fg_color="transparent"
)

keybind_frame.pack(
    fill="x",
    padx=20,
    pady=(0, 10)
)


# ============================================================
# R -> 7 GUIDE
# ============================================================

guide_frame = ctk.CTkFrame(
    keybind_frame,
    fg_color="#111111",
    corner_radius=8
)

guide_frame.pack(
    pady=(0, 10)
)


ctk.CTkLabel(
    guide_frame,
    text="R",
    width=45,
    font=("Arial", 15, "bold"),
    text_color=WHITE
).grid(
    row=0,
    column=0,
    padx=(12, 5),
    pady=7
)


ctk.CTkLabel(
    guide_frame,
    text="→",
    width=25,
    font=("Arial", 15, "bold"),
    text_color="#888888"
).grid(
    row=0,
    column=1
)


ctk.CTkLabel(
    guide_frame,
    text="7",
    width=45,
    font=("Arial", 15, "bold"),
    text_color=BG,
    fg_color=WHITE,
    corner_radius=6
).grid(
    row=0,
    column=2,
    padx=(5, 12),
    pady=7
)


# ============================================================
# SMALL KEYBINDS
# ============================================================

small_keybind_frame = ctk.CTkFrame(
    keybind_frame,
    fg_color="transparent"
)

small_keybind_frame.pack(
    anchor="center"
)


for number in ["6", "7", "8", "9", "0"]:

    row = ctk.CTkFrame(
        small_keybind_frame,
        fg_color="transparent"
    )

    row.pack(
        pady=2
    )

    input_button = ctk.CTkButton(
        row,
        text="UNBOUND",
        width=105,
        height=27,
        corner_radius=6,
        font=("Arial", 11, "bold"),
        fg_color=WHITE,
        hover_color="#DDDDDD",
        text_color=BG,
        command=lambda n=number:
        begin_key_capture(n)
    )

    input_button.grid(
        row=0,
        column=0,
        padx=(0, 6)
    )

    ctk.CTkLabel(
        row,
        text="→",
        width=20,
        font=("Arial", 12, "bold"),
        text_color="#777777"
    ).grid(
        row=0,
        column=1
    )

    ctk.CTkLabel(
        row,
        text=number,
        width=45,
        height=27,
        font=("Arial", 12, "bold"),
        text_color=BG,
        fg_color=WHITE,
        corner_radius=6
    ).grid(
        row=0,
        column=2,
        padx=(6, 0)
    )

    keybind_buttons[number] = input_button


# ============================================================
# HELP
# ============================================================

ctk.CTkLabel(
    settings_frame,
    text="R → 7 is fixed.\nConfigure the smaller binds below.",
    font=("Arial", 10),
    text_color="#777777"
).pack(
    pady=(0, 8)
)


# ============================================================
# STATUS
# ============================================================

ctk.CTkLabel(
    settings_frame,
    text="Caps Lock = Toggle  |  F8 = Close",
    font=("Arial", 11),
    text_color="#777777"
).pack(
    pady=(0, 12)
)


# ============================================================
# SHUTDOWN
# ============================================================

def shutdown():

    global running

    running = False
    click_event.set()

    try:
        app.destroy()

    except Exception:
        pass


app.protocol(
    "WM_DELETE_WINDOW",
    shutdown
)


# ============================================================
# INITIAL WINDOW
# ============================================================

app.update_idletasks()

app.geometry(
    f"400x{app.winfo_reqheight()}"
)


# ============================================================
# APPLY BORDERLESS STYLE
# ============================================================

app.after(
    100,
    remove_windows_titlebar
)


# ============================================================
# START THREADS
# ============================================================

threading.Thread(
    target=mouse_state_monitor,
    daemon=True
).start()

threading.Thread(
    target=autoclicker,
    daemon=True
).start()

threading.Thread(
    target=cps_monitor,
    daemon=True
).start()

threading.Thread(
    target=keyboard_hook_thread,
    daemon=True
).start()


# ============================================================
# START GUI
# ============================================================

app.mainloop()


# ============================================================
# FINAL SHUTDOWN
# ============================================================

running = False
click_event.set()