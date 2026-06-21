import ctypes
import json
import os
import queue
import re
import sys
import threading
import time
import winreg
from ctypes import wintypes
from enum import Enum
from pathlib import Path


def configure_tcl_tk_paths():
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        tcl_root = base / "tcl"
    else:
        tcl_root = Path(sys.base_prefix) / "tcl"

    tcl_library = tcl_root / "tcl8.6"
    tk_library = tcl_root / "tk8.6"
    if tcl_library.exists():
        os.environ.setdefault("TCL_LIBRARY", str(tcl_library))
    if tk_library.exists():
        os.environ.setdefault("TK_LIBRARY", str(tk_library))


configure_tcl_tk_paths()



APP_NAME = "いつもの改行 for Excel"
APP_VERSION = "20260621-153915"
APP_BUILD_DATETIME = "2026-06-21 15:39:15 +09:00"
CONFIG_PATH = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
) / "settings.json"
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_KEYUP = 0x0101
WM_SYSKEYUP = 0x0105
WM_QUIT = 0x0012
WM_COMMAND = 0x0111
WM_CLOSE = 0x0010
WM_DESTROY = 0x0002
WM_TIMER = 0x0113
WM_IME_CONTROL = 0x0283
WM_RBUTTONUP = 0x0205
WM_LBUTTONDBLCLK = 0x0203
WM_TRAYICON = 0x0400 + 77

VK_RETURN = 0x0D
VK_TAB = 0x09
VK_ESCAPE = 0x1B
VK_MENU = 0x12
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_BACK = 0x08
VK_SPACE = 0x20
VK_PRIOR = 0x21
VK_NEXT = 0x22
VK_END = 0x23
VK_HOME = 0x24
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_DELETE = 0x2E
VK_F2 = 0x71
VK_PROCESSKEY = 0xE5

LLKHF_INJECTED = 0x10
GUI_CARETBLINKING = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
IDI_APPLICATION = 32512
IMAGE_ICON = 1
LR_LOADFROMFILE = 0x00000010
LR_DEFAULTSIZE = 0x00000040
NIF_MESSAGE = 0x00000001
NIF_ICON = 0x00000002
NIF_TIP = 0x00000004
NIM_ADD = 0x00000000
NIM_MODIFY = 0x00000001
NIM_DELETE = 0x00000002
NIM_SETVERSION = 0x00000004
NOTIFYICON_VERSION_4 = 4
MF_STRING = 0x00000000
MF_GRAYED = 0x00000001
MF_CHECKED = 0x00000008
MF_SEPARATOR = 0x00000800
TPM_RIGHTBUTTON = 0x0002
TPM_NONOTIFY = 0x0080
TPM_RETURNCMD = 0x0100
GWLP_WNDPROC = -4
STARTUP_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_VALUE_NAME = "ItsumonoKaigyoForExcel"
START_MINIMIZED_ARG = "--start-minimized"
DEVELOPER_WEBSITE_URL = "https://bunjicompany.com/"
MUTEX_NAME = "Local\\ItsumonoKaigyoForExcel.SingleInstance"
ERROR_ALREADY_EXISTS = 183
MENU_STARTUP_ADD = 1001
MENU_STARTUP_REMOVE = 1002
MENU_ABOUT = 1003
MENU_EXIT = 1004
MENU_SHOW_DIALOG = 1005
MENU_PAUSE_TOGGLE = 1006
MENU_LANGUAGE_JA = 1007
MENU_LANGUAGE_EN = 1008
MENU_DEVELOPER_WEBSITE = 1009
CONTROL_RADIO_ENTER = 2001
CONTROL_RADIO_SHIFT_ENTER = 2002
CONTROL_BUTTON_MINIMIZE = 2003
CONTROL_BUTTON_EXIT = 2004
CONTROL_BUTTON_PAUSE = 2005
CONTROL_BUTTON_LANGUAGE = 2006
STATUS_TIMER_ID = 3001
CW_USEDEFAULT = -2147483648
SW_HIDE = 0
SW_SHOWNORMAL = 1
SW_SHOW = 5
WS_OVERLAPPED = 0x00000000
WS_CAPTION = 0x00C00000
WS_SYSMENU = 0x00080000
WS_MINIMIZEBOX = 0x00020000
WS_VISIBLE = 0x10000000
WS_CHILD = 0x40000000
WS_GROUP = 0x00020000
WS_TABSTOP = 0x00010000
WS_BORDER = 0x00800000
BS_AUTORADIOBUTTON = 0x00000009
BS_GROUPBOX = 0x00000007
BS_PUSHBUTTON = 0x00000000
SS_LEFT = 0x00000000
SS_CENTERIMAGE = 0x00000200
BM_SETCHECK = 0x00F1
WM_SETFONT = 0x0030
BST_CHECKED = 1
COLOR_WINDOW = 5
COLOR_BTNFACE = 15
FW_NORMAL = 400
FW_BOLD = 700
SCAN_ENTER = 0x1C
SCAN_ALT = 0x38

TRIGGERS = {
    "Enter": {"key": VK_RETURN, "ctrl": False, "shift": False},
    "Shift + Enter": {"key": VK_RETURN, "ctrl": False, "shift": True},
}
LANGUAGES = {"ja", "en"}
TEXTS = {
    "ja": {
        "app_name": "いつもの改行 for Excel",
        "subtitle": "Enter または Shift + Enter でセル内改行します。",
        "line_break_key": "セル内改行キー",
        "status_prefix": "ステータス：",
        "status_initial": "判定中",
        "status_paused": "一時停止中",
        "status_editing": "セル内入力中",
        "status_not_editing": "セル内入力中ではありません",
        "status_unknown": "セル内入力中を確認できません",
        "button_exit": "終了",
        "button_pause": "一時停止",
        "button_resume": "再開",
        "button_minimize": "最小化",
        "button_language": "English",
        "menu_open": "ダイアログを開く",
        "menu_startup_add": "Windows起動時に実行する",
        "menu_startup_remove": "Windows起動時の登録を解除する",
        "menu_language_ja": "日本語",
        "menu_language_en": "English",
        "menu_developer_website": "開発元Webサイト",
        "menu_about": "バージョン情報",
        "menu_exit": "終了",
        "about_title": "{app_name} - バージョン情報",
        "about_body": "{app_name}\nDeveloped by ぶんじカンパニー\n\nバージョン: {version}\nビルド日時: {build_datetime}",
        "error_hook_start": "キーボードフックの開始に失敗しました。",
        "error_send_break": "改行の送信に失敗しました。",
        "error_single_instance": "アプリの起動確認に失敗しました。",
        "already_running": "すでに起動しています。タスクトレイのアイコンから操作してください。",
    },
    "en": {
        "app_name": "LineBuddy for Excel",
        "subtitle": "Insert line breaks in Excel cells with Enter or Shift + Enter.",
        "line_break_key": "Cell line break key",
        "status_prefix": "Status: ",
        "status_initial": "Checking",
        "status_paused": "Paused",
        "status_editing": "Editing an Excel cell",
        "status_not_editing": "Not editing an Excel cell",
        "status_unknown": "Could not confirm cell editing",
        "button_exit": "Exit",
        "button_pause": "Pause",
        "button_resume": "Resume",
        "button_minimize": "Minimize",
        "button_language": "日本語",
        "menu_open": "Open dialog",
        "menu_startup_add": "Run at Windows startup",
        "menu_startup_remove": "Remove from Windows startup",
        "menu_language_ja": "日本語",
        "menu_language_en": "English",
        "menu_developer_website": "Developer website",
        "menu_about": "About",
        "menu_exit": "Exit",
        "about_title": "{app_name} - About",
        "about_body": "{app_name}\nDeveloped by Bunji Company\n\nVersion: {version}\nBuild date: {build_datetime}",
        "error_hook_start": "Failed to start the keyboard hook.",
        "error_send_break": "Failed to send the line break.",
        "error_single_instance": "Failed to check whether the app is already running.",
        "already_running": "The app is already running. Use the task tray icon to control it.",
    },
}
STATUS_REASON_KEYS = {
    "セル内入力中": "status_editing",
    "セル内入力中ではありません": "status_not_editing",
    "セル内入力中を確認できません": "status_unknown",
}


def default_language():
    try:
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        if lang_id & 0x03FF == 0x11:
            return "ja"
    except Exception:
        pass
    return "en"


def text_for(language, key):
    language = language if language in TEXTS else "en"
    return TEXTS[language].get(key, TEXTS["en"].get(key, key))

DEFAULT_CONFIG = {
    "trigger": "Enter",
    "excel_only": True,
    "edit_only": True,
    "enabled": True,
    "language": default_language(),
}


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", INPUT_UNION)]


class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("hwndActive", wintypes.HWND),
        ("hwndFocus", wintypes.HWND),
        ("hwndCapture", wintypes.HWND),
        ("hwndMenuOwner", wintypes.HWND),
        ("hwndMoveSize", wintypes.HWND),
        ("hwndCaret", wintypes.HWND),
        ("rcCaret", wintypes.RECT),
    ]


LowLevelKeyboardProc = ctypes.WINFUNCTYPE(
    ctypes.c_long,
    ctypes.c_int,
    wintypes.WPARAM,
    wintypes.LPARAM,
)
EnumChildProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
WindowProc = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32
kernel32 = ctypes.windll.kernel32
imm32 = ctypes.windll.imm32
ole32 = ctypes.windll.ole32
oleaut32 = ctypes.windll.oleaut32
oleacc = ctypes.windll.oleacc
gdi32 = ctypes.windll.gdi32

user32.SetWindowsHookExW.argtypes = [
    ctypes.c_int,
    LowLevelKeyboardProc,
    wintypes.HINSTANCE,
    wintypes.DWORD,
]
user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.CallWindowProcW.argtypes = [ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.CallWindowProcW.restype = ctypes.c_long
user32.CallNextHookEx.argtypes = [
    wintypes.HHOOK,
    ctypes.c_int,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.CallNextHookEx.restype = ctypes.c_long
user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL
user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT
user32.LoadIconW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR]
user32.LoadIconW.restype = wintypes.HICON
user32.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT, ctypes.c_int, ctypes.c_int, wintypes.UINT]
user32.LoadImageW.restype = wintypes.HANDLE
user32.CreateIcon.argtypes = [
    wintypes.HINSTANCE,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_byte,
    ctypes.c_byte,
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.POINTER(ctypes.c_ubyte),
]
user32.CreateIcon.restype = wintypes.HICON
user32.DestroyIcon.argtypes = [wintypes.HICON]
user32.DestroyIcon.restype = wintypes.BOOL
user32.CreatePopupMenu.restype = wintypes.HMENU
user32.DestroyMenu.argtypes = [wintypes.HMENU]
user32.DestroyMenu.restype = wintypes.BOOL
user32.AppendMenuW.argtypes = [wintypes.HMENU, wintypes.UINT, ULONG_PTR, wintypes.LPCWSTR]
user32.AppendMenuW.restype = wintypes.BOOL
user32.TrackPopupMenu.argtypes = [
    wintypes.HMENU,
    wintypes.UINT,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    ctypes.c_void_p,
]
user32.TrackPopupMenu.restype = wintypes.UINT
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
user32.GetCursorPos.restype = wintypes.BOOL
if ctypes.sizeof(ctypes.c_void_p) == 8:
    user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
    user32.SetWindowLongPtrW.restype = ctypes.c_void_p
else:
    user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
    user32.SetWindowLongW.restype = ctypes.c_void_p
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = wintypes.SHORT
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetParent.argtypes = [wintypes.HWND]
user32.GetParent.restype = wintypes.HWND
user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
user32.GetAncestor.restype = wintypes.HWND
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetWindowRect.restype = wintypes.BOOL
user32.GetDC.argtypes = [wintypes.HWND]
user32.GetDC.restype = wintypes.HDC
user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
user32.ReleaseDC.restype = ctypes.c_int
user32.EnumChildWindows.argtypes = [wintypes.HWND, EnumChildProc, wintypes.LPARAM]
user32.EnumChildWindows.restype = wintypes.BOOL
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetGUIThreadInfo.argtypes = [wintypes.DWORD, ctypes.POINTER(GUITHREADINFO)]
user32.GetGUIThreadInfo.restype = wintypes.BOOL
user32.PostThreadMessageW.argtypes = [
    wintypes.DWORD,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.PostThreadMessageW.restype = wintypes.BOOL

imm32.ImmGetContext.argtypes = [wintypes.HWND]
imm32.ImmGetContext.restype = wintypes.HANDLE
imm32.ImmReleaseContext.argtypes = [wintypes.HWND, wintypes.HANDLE]
imm32.ImmReleaseContext.restype = wintypes.BOOL
imm32.ImmGetOpenStatus.argtypes = [wintypes.HANDLE]
imm32.ImmGetOpenStatus.restype = wintypes.BOOL
imm32.ImmGetDefaultIMEWnd.argtypes = [wintypes.HWND]
imm32.ImmGetDefaultIMEWnd.restype = wintypes.HWND
imm32.ImmGetCompositionStringW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPVOID,
    wintypes.DWORD,
]
imm32.ImmGetCompositionStringW.restype = wintypes.LONG

kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetCurrentThreadId.restype = wintypes.DWORD
kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.GetLastError.restype = wintypes.DWORD
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPWSTR,
    ctypes.POINTER(wintypes.DWORD),
]
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
GCS_COMPSTR = 0x0008
IMC_GETOPENSTATUS = 0x0005
S_OK = 0
S_FALSE = 1
DISPATCH_METHOD = 0x1
DISPATCH_PROPERTYGET = 0x2
VT_I4 = 3
VT_BOOL = 11
VT_DISPATCH = 9
DISPID_PROPERTYPUT = -3
CO_E_NOTINITIALIZED = 0x800401F0
RPC_E_CHANGED_MODE = 0x80010106
EXCEL_COM_BUSY = 0x800AC472
OBJID_NATIVEOM = -16
RANGE_CACHE_SECONDS = 15.0
GA_ROOT = 2
last_range_seen_at = 0.0
last_non_range_seen_at = 0.0
last_dispatch_hresult = S_OK


class EditState(Enum):
    CELL_EDITING = 1
    OBJECT_EDITING = 2
    NOT_EDITING = 3
    UNKNOWN = 4


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]


class DISPPARAMS(ctypes.Structure):
    _fields_ = [
        ("rgvarg", ctypes.c_void_p),
        ("rgdispidNamedArgs", ctypes.c_void_p),
        ("cArgs", wintypes.UINT),
        ("cNamedArgs", wintypes.UINT),
    ]


class EXCEPINFO(ctypes.Structure):
    _fields_ = [
        ("wCode", wintypes.WORD),
        ("wReserved", wintypes.WORD),
        ("bstrSource", ctypes.c_void_p),
        ("bstrDescription", ctypes.c_void_p),
        ("bstrHelpFile", ctypes.c_void_p),
        ("dwHelpContext", wintypes.DWORD),
        ("pvReserved", ctypes.c_void_p),
        ("pfnDeferredFillIn", ctypes.c_void_p),
        ("scode", ctypes.c_long),
    ]


class VARIANT_VALUE(ctypes.Union):
    _fields_ = [
        ("llVal", ctypes.c_longlong),
        ("lVal", ctypes.c_long),
        ("boolVal", wintypes.VARIANT_BOOL),
        ("bstrVal", ctypes.c_void_p),
        ("punkVal", ctypes.c_void_p),
        ("pdispVal", ctypes.c_void_p),
    ]


class VARIANT(ctypes.Structure):
    _anonymous_ = ("value",)
    _fields_ = [
        ("vt", wintypes.WORD),
        ("wReserved1", wintypes.WORD),
        ("wReserved2", wintypes.WORD),
        ("wReserved3", wintypes.WORD),
        ("value", VARIANT_VALUE),
    ]


IID_NULL = GUID(0, 0, 0, (ctypes.c_ubyte * 8)(0, 0, 0, 0, 0, 0, 0, 0))
IID_IDISPATCH = GUID(
    0x00020400,
    0x0000,
    0x0000,
    (ctypes.c_ubyte * 8)(0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46),
)
IID_IACCESSIBLE = GUID(
    0x618736E0,
    0x3C3D,
    0x11CF,
    (ctypes.c_ubyte * 8)(0x81, 0x0C, 0x00, 0xAA, 0x00, 0x38, 0x9B, 0x71),
)

ole32.CoInitialize.argtypes = [ctypes.c_void_p]
ole32.CoInitialize.restype = ctypes.c_long
ole32.CLSIDFromProgID.argtypes = [wintypes.LPCOLESTR, ctypes.POINTER(GUID)]
ole32.CLSIDFromProgID.restype = ctypes.c_long
oleaut32.GetActiveObject.argtypes = [ctypes.POINTER(GUID), ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
oleaut32.GetActiveObject.restype = ctypes.c_long
oleaut32.VariantClear.argtypes = [ctypes.POINTER(VARIANT)]
oleaut32.VariantClear.restype = ctypes.c_long
oleaut32.SysFreeString.argtypes = [ctypes.c_void_p]
oleaut32.SysFreeString.restype = None
oleacc.AccessibleObjectFromWindow.argtypes = [
    wintypes.HWND,
    ctypes.c_long,
    ctypes.POINTER(GUID),
    ctypes.POINTER(ctypes.c_void_p),
]
oleacc.AccessibleObjectFromWindow.restype = ctypes.c_long
oleacc.AccessibleChildren.argtypes = [
    ctypes.c_void_p,
    ctypes.c_long,
    ctypes.c_long,
    ctypes.POINTER(VARIANT),
    ctypes.POINTER(ctypes.c_long),
]
oleacc.AccessibleChildren.restype = ctypes.c_long
gdi32.GetPixel.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
gdi32.GetPixel.restype = wintypes.COLORREF
gdi32.CreateFontW.argtypes = [
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.LPCWSTR,
]
gdi32.CreateFontW.restype = wintypes.HFONT


class NOTIFYICONDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT),
        ("uCallbackMessage", wintypes.UINT),
        ("hIcon", wintypes.HICON),
        ("szTip", wintypes.WCHAR * 128),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256),
        ("uVersion", wintypes.UINT),
        ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD),
        ("guidItem", ctypes.c_byte * 16),
        ("hBalloonIcon", wintypes.HICON),
    ]


class WNDCLASS(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", WindowProc),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HANDLE),
        ("hbrBackground", wintypes.HANDLE),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]


shell32.Shell_NotifyIconW.argtypes = [wintypes.DWORD, ctypes.POINTER(NOTIFYICONDATA)]
shell32.Shell_NotifyIconW.restype = wintypes.BOOL
shell32.ShellExecuteW.argtypes = [
    wintypes.HWND,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    ctypes.c_int,
]
shell32.ShellExecuteW.restype = wintypes.HINSTANCE
user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASS)]
user32.RegisterClassW.restype = wintypes.ATOM
user32.CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.HINSTANCE,
    ctypes.c_void_p,
]
user32.CreateWindowExW.restype = wintypes.HWND
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = ctypes.c_long
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL
user32.UpdateWindow.argtypes = [wintypes.HWND]
user32.UpdateWindow.restype = wintypes.BOOL
user32.SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
user32.SetWindowTextW.restype = wintypes.BOOL
user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = ctypes.c_long
user32.SetTimer.argtypes = [wintypes.HWND, wintypes.UINT_PTR if hasattr(wintypes, "UINT_PTR") else ULONG_PTR, wintypes.UINT, ctypes.c_void_p]
user32.SetTimer.restype = wintypes.UINT_PTR if hasattr(wintypes, "UINT_PTR") else ULONG_PTR
user32.KillTimer.argtypes = [wintypes.HWND, wintypes.UINT_PTR if hasattr(wintypes, "UINT_PTR") else ULONG_PTR]
user32.KillTimer.restype = wintypes.BOOL
user32.MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
user32.MessageBoxW.restype = ctypes.c_int
user32.PostQuitMessage.argtypes = [ctypes.c_int]
user32.PostQuitMessage.restype = None
user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL
user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.TranslateMessage.restype = wintypes.BOOL
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.restype = ctypes.c_long


def load_config():
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()
    try:
        loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_CONFIG.copy()
    config = DEFAULT_CONFIG.copy()
    config.update({k: v for k, v in loaded.items() if k in config})
    if config["trigger"] not in TRIGGERS:
        config["trigger"] = DEFAULT_CONFIG["trigger"]
    if config["language"] not in LANGUAGES:
        config["language"] = default_language()
    config["excel_only"] = True
    config["edit_only"] = True
    config["enabled"] = True
    return config


def save_config(config):
    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def app_base_dir():
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent


def resource_path(name):
    return app_base_dir() / name


def load_app_icon(size=0):
    icon_path = resource_path("app_icon.ico")
    if icon_path.exists():
        icon = user32.LoadImageW(
            None,
            str(icon_path),
            IMAGE_ICON,
            size,
            size,
            LR_LOADFROMFILE | (LR_DEFAULTSIZE if size == 0 else 0),
        )
        if icon:
            return icon
    return user32.LoadIconW(None, ctypes.cast(ctypes.c_void_p(IDI_APPLICATION), wintypes.LPCWSTR))


def create_paused_tray_icon(size=32):
    width = height = size
    xor = bytearray(width * height * 4)
    # 1 bit per pixel AND mask. All zero means fully opaque.
    and_row_bytes = ((width + 31) // 32) * 4
    and_mask = bytearray(and_row_bytes * height)

    def put_pixel(x, y, red, green, blue, alpha=255):
        if not (0 <= x < width and 0 <= y < height):
            return
        row = height - 1 - y
        offset = (row * width + x) * 4
        xor[offset : offset + 4] = bytes((blue, green, red, alpha))

    for y in range(height):
        for x in range(width):
            edge = x in (0, width - 1) or y in (0, height - 1)
            grid = x in (8, 16, 24) or y in (8, 16, 24)
            if edge:
                shade = 92
            elif grid:
                shade = 146
            else:
                shade = 190
            put_pixel(x, y, shade, shade, shade)

    for x in range(11, 15):
        for y in range(9, 23):
            put_pixel(x, y, 56, 56, 56)
    for x in range(18, 22):
        for y in range(9, 23):
            put_pixel(x, y, 56, 56, 56)

    xor_bits = (ctypes.c_ubyte * len(xor)).from_buffer_copy(xor)
    and_bits = (ctypes.c_ubyte * len(and_mask)).from_buffer_copy(and_mask)
    icon = user32.CreateIcon(None, width, height, 1, 32, and_bits, xor_bits)
    return icon or load_app_icon()


def create_font(point_size, weight=FW_NORMAL):
    return gdi32.CreateFontW(
        -point_size,
        0,
        0,
        0,
        weight,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        "Segoe UI",
    )


def startup_command():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}" {START_MINIMIZED_ARG}'

    executable = Path(sys.executable)
    pythonw = executable.with_name("pythonw.exe")
    if pythonw.exists():
        executable = pythonw
    return f'"{executable}" "{Path(__file__).resolve()}" {START_MINIMIZED_ARG}'


def is_startup_registered():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_RUN_KEY, 0, winreg.KEY_READ) as key:
            value, _kind = winreg.QueryValueEx(key, STARTUP_VALUE_NAME)
            return value == startup_command()
    except FileNotFoundError:
        return False
    except OSError:
        return False


def register_startup():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, STARTUP_VALUE_NAME, 0, winreg.REG_SZ, startup_command())


def unregister_startup():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, STARTUP_VALUE_NAME)
    except FileNotFoundError:
        pass
    except OSError:
        pass


def open_developer_website(hwnd=None):
    result = shell32.ShellExecuteW(hwnd, "open", DEVELOPER_WEBSITE_URL, None, None, SW_SHOWNORMAL)
    value = result if isinstance(result, int) else (result.value if result is not None else 0)
    return bool(value and value > 32)


def is_key_down(vk_code):
    return bool(user32.GetAsyncKeyState(vk_code) & 0x8000)


def send_input(item):
    return user32.SendInput(1, ctypes.byref(item), ctypes.sizeof(INPUT)) == 1


def send_key(vk_code, key_up=False):
    flags = KEYEVENTF_KEYUP if key_up else 0
    item = INPUT(
        type=1,
        ki=KEYBDINPUT(
            wVk=vk_code,
            wScan=0,
            dwFlags=flags,
            time=0,
            dwExtraInfo=0,
        ),
    )
    return send_input(item)


def send_scan_key(scan_code, key_up=False):
    flags = KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if key_up else 0)
    item = INPUT(
        type=1,
        ki=KEYBDINPUT(
            wVk=0,
            wScan=scan_code,
            dwFlags=flags,
            time=0,
            dwExtraInfo=0,
        ),
    )
    return send_input(item)


def send_alt_enter():
    ctrl_down = is_key_down(VK_CONTROL)
    shift_down = is_key_down(VK_SHIFT)
    enter_down = is_key_down(VK_RETURN)

    if enter_down:
        send_key(VK_RETURN, key_up=True)
    if ctrl_down:
        send_key(VK_CONTROL, key_up=True)
    if shift_down:
        send_key(VK_SHIFT, key_up=True)

    ok = True
    time.sleep(0.03)
    ok = send_scan_key(SCAN_ALT) and ok
    time.sleep(0.03)
    ok = send_scan_key(SCAN_ENTER) and ok
    time.sleep(0.01)
    ok = send_scan_key(SCAN_ENTER, key_up=True) and ok
    time.sleep(0.03)
    ok = send_scan_key(SCAN_ALT, key_up=True) and ok

    if shift_down:
        send_key(VK_SHIFT)
    if ctrl_down:
        send_key(VK_CONTROL)

    return ok


def send_excel_line_break():
    return send_alt_enter()


def process_name_from_pid(pid):
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not handle:
        return ""

    try:
        buffer_len = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(buffer_len.value)
        ok = kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(buffer_len))
        if not ok:
            return ""
        return Path(buffer.value).name.lower()
    finally:
        kernel32.CloseHandle(handle)


def foreground_window_info():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None, 0, wintypes.DWORD()

    pid = wintypes.DWORD()
    thread_id = user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value or not thread_id:
        return hwnd, 0, pid
    return hwnd, thread_id, pid


def foreground_process_name():
    _hwnd, _thread_id, pid = foreground_window_info()
    if not pid.value:
        return ""
    return process_name_from_pid(pid)


def is_excel_foreground():
    return foreground_process_name() == "excel.exe"


def window_text(hwnd):
    if not hwnd:
        return ""
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def window_class(hwnd):
    if not hwnd:
        return ""
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buffer, 256)
    return buffer.value


def find_child_window_by_class(root_hwnd, class_name):
    if not root_hwnd:
        return None

    found = {"hwnd": None}

    @EnumChildProc
    def enum_child(child_hwnd, _lparam):
        if window_class(child_hwnd) == class_name:
            found["hwnd"] = child_hwnd
            return False
        nested = find_child_window_by_class(child_hwnd, class_name)
        if nested:
            found["hwnd"] = nested
            return False
        return True

    user32.EnumChildWindows(root_hwnd, enum_child, 0)
    return found["hwnd"]


def has_drawing_tools_orange_tab(hwnd):
    if not hwnd:
        return False

    root_hwnd = user32.GetAncestor(hwnd, GA_ROOT) or hwnd
    rect = wintypes.RECT()
    if not user32.GetWindowRect(root_hwnd, ctypes.byref(rect)):
        return False

    width = max(0, rect.right - rect.left)
    height = max(0, rect.bottom - rect.top)
    if width < 200 or height < 80:
        return False

    dc = user32.GetDC(None)
    if not dc:
        return False

    try:
        orange_pixels = 0
        # Excel 2010 context tabs appear in the top ribbon/title area.
        max_y = min(95, height)
        for y in range(0, max_y, 4):
            screen_y = rect.top + y
            for x in range(0, width, 4):
                color = gdi32.GetPixel(dc, rect.left + x, screen_y)
                if color == 0xFFFFFFFF:
                    continue
                red = color & 0xFF
                green = (color >> 8) & 0xFF
                blue = (color >> 16) & 0xFF
                if red >= 215 and 90 <= green <= 185 and blue <= 90:
                    orange_pixels += 1
                    if orange_pixels >= 18:
                        return True
        return False
    finally:
        user32.ReleaseDC(None, dc)


def excel_ui_is_textbox_context(hwnd):
    found = {"value": False}
    roots = [hwnd]
    root_hwnd = user32.GetAncestor(hwnd, GA_ROOT) if hwnd else None
    if root_hwnd and root_hwnd not in roots:
        roots.append(root_hwnd)

    @EnumChildProc
    def enum_child(child_hwnd, _lparam):
        text = window_text(child_hwnd)
        drawing_tools_visible = "描画ツール" in text or "Drawing Tools" in text
        if is_textbox_object_name(text) or drawing_tools_visible:
            found["value"] = True
            return False
        return True

    for root in roots:
        text = window_text(root)
        if is_textbox_object_name(text) or "描画ツール" in text or "Drawing Tools" in text:
            return True
        user32.EnumChildWindows(root, enum_child, 0)
        if found["value"]:
            return True
    return found["value"]


def is_textbox_object_name(text):
    if not text:
        return False
    patterns = (
        r"テキスト\s*ボックス\s*\d+",
        r"テキストボックス\s*\d+",
        r"Text\s*Box\s*\d+",
        r"TextBox\s*\d+",
    )
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def make_child_variant(child_id=0):
    variant = VARIANT()
    variant.vt = 3
    variant.lVal = child_id
    return variant


def accessible_string(accessible, child_id, method_index):
    if not accessible:
        return ""
    try:
        vtable = ctypes.cast(accessible, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        getter = ctypes.WINFUNCTYPE(
            ctypes.c_long,
            ctypes.c_void_p,
            VARIANT,
            ctypes.POINTER(ctypes.c_void_p),
        )(vtable[method_index])
        bstr = ctypes.c_void_p()
        if getter(accessible, make_child_variant(child_id), ctypes.byref(bstr)) != S_OK or not bstr:
            return ""
        try:
            return ctypes.wstring_at(bstr)
        finally:
            oleaut32.SysFreeString(bstr)
    except (OSError, ValueError):
        return ""


def accessible_child_count(accessible):
    if not accessible:
        return 0
    try:
        vtable = ctypes.cast(accessible, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        getter = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_long))(vtable[8])
        count = ctypes.c_long()
        if getter(accessible, ctypes.byref(count)) != S_OK:
            return 0
        return max(0, count.value)
    except (OSError, ValueError):
        return 0


def accessible_text_matches(accessible, child_id):
    name = accessible_string(accessible, child_id, 10)
    value = accessible_string(accessible, child_id, 11)
    text = f"{name}\n{value}"
    return is_textbox_object_name(text)


def accessible_tree_has_textbox_marker(hwnd):
    if not hwnd or not ensure_com_initialized():
        return False

    root = ctypes.c_void_p()
    if oleacc.AccessibleObjectFromWindow(hwnd, 0, ctypes.byref(IID_IACCESSIBLE), ctypes.byref(root)) != S_OK or not root:
        return False

    visited = {"count": 0}

    def scan(accessible, depth=0):
        if not accessible or depth > 4 or visited["count"] > 180:
            return False
        visited["count"] += 1
        if accessible_text_matches(accessible, 0):
            return True

        count = min(accessible_child_count(accessible), 80)
        if count <= 0:
            return False

        children = (VARIANT * count)()
        obtained = ctypes.c_long()
        if oleacc.AccessibleChildren(accessible, 0, count, children, ctypes.byref(obtained)) != S_OK:
            return False

        for index in range(obtained.value):
            child = children[index]
            if child.vt == VT_DISPATCH and child.pdispVal:
                child_dispatch = ctypes.c_void_p(child.pdispVal)
                try:
                    if scan(child_dispatch, depth + 1):
                        return True
                finally:
                    release_com_object(child_dispatch)
            elif child.vt == 3 and child.lVal:
                if accessible_text_matches(accessible, child.lVal):
                    return True
        return False

    try:
        return scan(root)
    finally:
        release_com_object(root)


def release_com_object(dispatch):
    if not dispatch:
        return
    vtable = ctypes.cast(dispatch, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    release = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vtable[2])
    release(dispatch)


def ensure_com_initialized():
    result = ole32.CoInitialize(None)
    normalized = result & 0xFFFFFFFF
    return result in (S_OK, S_FALSE) or normalized == RPC_E_CHANGED_MODE


def normalize_hresult(value):
    return value & 0xFFFFFFFF


def get_dispatch_property(dispatch, name):
    global last_dispatch_hresult
    last_dispatch_hresult = S_OK

    if not dispatch:
        return None

    vtable = ctypes.cast(dispatch, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    get_ids = ctypes.WINFUNCTYPE(
        ctypes.c_long,
        ctypes.c_void_p,
        ctypes.POINTER(GUID),
        ctypes.POINTER(ctypes.c_wchar_p),
        wintypes.UINT,
        wintypes.DWORD,
        ctypes.POINTER(ctypes.c_long),
    )(vtable[5])
    invoke = ctypes.WINFUNCTYPE(
        ctypes.c_long,
        ctypes.c_void_p,
        ctypes.c_long,
        ctypes.POINTER(GUID),
        wintypes.DWORD,
        wintypes.WORD,
        ctypes.POINTER(DISPPARAMS),
        ctypes.POINTER(VARIANT),
        ctypes.POINTER(EXCEPINFO),
        ctypes.POINTER(wintypes.UINT),
    )(vtable[6])

    dispid = ctypes.c_long()
    name_arg = ctypes.c_wchar_p(name)
    hr = get_ids(dispatch, ctypes.byref(IID_NULL), ctypes.byref(name_arg), 1, 0, ctypes.byref(dispid))
    last_dispatch_hresult = normalize_hresult(hr)
    if hr != S_OK:
        return None

    params = DISPPARAMS(None, None, 0, 0)
    result = VARIANT()
    exception = EXCEPINFO()
    arg_error = wintypes.UINT()
    hr = invoke(
        dispatch,
        dispid.value,
        ctypes.byref(IID_NULL),
        0,
        DISPATCH_PROPERTYGET,
        ctypes.byref(params),
        ctypes.byref(result),
        ctypes.byref(exception),
        ctypes.byref(arg_error),
    )
    last_dispatch_hresult = normalize_hresult(hr)
    if hr != S_OK:
        return None
    return result


def invoke_dispatch_method_named_i4(dispatch, method_name, arg_name, arg_value):
    if not dispatch:
        return None

    vtable = ctypes.cast(dispatch, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    get_ids = ctypes.WINFUNCTYPE(
        ctypes.c_long,
        ctypes.c_void_p,
        ctypes.POINTER(GUID),
        ctypes.POINTER(ctypes.c_wchar_p),
        wintypes.UINT,
        wintypes.DWORD,
        ctypes.POINTER(ctypes.c_long),
    )(vtable[5])
    invoke = ctypes.WINFUNCTYPE(
        ctypes.c_long,
        ctypes.c_void_p,
        ctypes.c_long,
        ctypes.POINTER(GUID),
        wintypes.DWORD,
        wintypes.WORD,
        ctypes.POINTER(DISPPARAMS),
        ctypes.POINTER(VARIANT),
        ctypes.POINTER(EXCEPINFO),
        ctypes.POINTER(wintypes.UINT),
    )(vtable[6])

    names = (ctypes.c_wchar_p * 2)(method_name, arg_name)
    dispids = (ctypes.c_long * 2)()
    hr = get_ids(dispatch, ctypes.byref(IID_NULL), names, 2, 0, dispids)
    if hr != S_OK:
        return None

    args = (VARIANT * 1)()
    args[0].vt = VT_I4
    args[0].lVal = arg_value
    named_args = (ctypes.c_long * 1)(dispids[1])
    params = DISPPARAMS(
        ctypes.cast(args, ctypes.c_void_p),
        ctypes.cast(named_args, ctypes.c_void_p),
        1,
        1,
    )
    result = VARIANT()
    exception = EXCEPINFO()
    arg_error = wintypes.UINT()
    hr = invoke(
        dispatch,
        dispids[0],
        ctypes.byref(IID_NULL),
        0,
        DISPATCH_METHOD,
        ctypes.byref(params),
        ctypes.byref(result),
        ctypes.byref(exception),
        ctypes.byref(arg_error),
    )
    if hr != S_OK:
        return None
    return result


def get_dispatch_property_dispatch(dispatch, name):
    result = get_dispatch_property(dispatch, name)
    if not result:
        return None
    try:
        if result.vt == VT_DISPATCH and result.pdispVal:
            dispatch_value = ctypes.c_void_p(result.pdispVal)
            result.pdispVal = None
            return dispatch_value
        return None
    finally:
        oleaut32.VariantClear(ctypes.byref(result))


def get_excel_dispatch_from_window():
    hwnd, _thread_id, pid = foreground_window_info()
    if not hwnd or not pid.value:
        return None
    if process_name_from_pid(pid) != "excel.exe":
        return None
    if not ensure_com_initialized():
        return None

    native_hwnd = find_child_window_by_class(hwnd, "EXCEL7") or hwnd
    native = ctypes.c_void_p()
    hr = oleacc.AccessibleObjectFromWindow(
        native_hwnd,
        OBJID_NATIVEOM,
        ctypes.byref(IID_IDISPATCH),
        ctypes.byref(native),
    )
    if hr != S_OK or not native:
        return None

    app = get_dispatch_property_dispatch(native, "Application")
    if app:
        release_com_object(native)
        return app

    return native


def get_active_excel_dispatch():
    if not ensure_com_initialized():
        return None

    clsid = GUID()
    if ole32.CLSIDFromProgID("Excel.Application", ctypes.byref(clsid)) != S_OK:
        return None

    unknown = ctypes.c_void_p()
    if oleaut32.GetActiveObject(ctypes.byref(clsid), None, ctypes.byref(unknown)) != S_OK:
        return None

    try:
        vtable = ctypes.cast(unknown, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        query_interface = ctypes.WINFUNCTYPE(
            ctypes.c_long,
            ctypes.c_void_p,
            ctypes.POINTER(GUID),
            ctypes.POINTER(ctypes.c_void_p),
        )(vtable[0])
        dispatch = ctypes.c_void_p()
        if query_interface(unknown, ctypes.byref(IID_IDISPATCH), ctypes.byref(dispatch)) != S_OK:
            return None
        return dispatch
    finally:
        release_com_object(unknown)


def is_excel_selection_range():
    excel = get_active_excel_dispatch()
    if not excel:
        return None

    selection = None
    shape_range = None
    address = None
    try:
        selection = get_dispatch_property(excel, "Selection")
        if not selection or selection.vt != VT_DISPATCH or not selection.pdispVal:
            if last_dispatch_hresult == EXCEL_COM_BUSY:
                return "busy"
            return None

        shape_range = get_dispatch_property(selection.pdispVal, "ShapeRange")
        if shape_range and shape_range.vt:
            return False

        address = get_dispatch_property(selection.pdispVal, "Address")
        return bool(address and address.vt)
    finally:
        if shape_range:
            oleaut32.VariantClear(ctypes.byref(shape_range))
        if address:
            oleaut32.VariantClear(ctypes.byref(address))
        if selection:
            oleaut32.VariantClear(ctypes.byref(selection))
        release_com_object(excel)


def is_excel_cell_edit_mode_by_commandbars():
    excel = get_active_excel_dispatch()
    if not excel:
        return None

    command_bars = None
    control = None
    enabled = None
    try:
        command_bars = get_dispatch_property_dispatch(excel, "CommandBars")
        if not command_bars:
            return None

        control = invoke_dispatch_method_named_i4(command_bars, "FindControl", "Id", 23)
        if not control or control.vt != VT_DISPATCH or not control.pdispVal:
            return None

        enabled = get_dispatch_property(control.pdispVal, "Enabled")
        if not enabled or enabled.vt != VT_BOOL:
            return None

        return not bool(enabled.boolVal)
    finally:
        if enabled:
            oleaut32.VariantClear(ctypes.byref(enabled))
        if control:
            oleaut32.VariantClear(ctypes.byref(control))
        if command_bars:
            release_com_object(command_bars)
        release_com_object(excel)


def is_excel_selection_range_cached():
    global last_range_seen_at, last_non_range_seen_at

    now = time.time()
    selection_is_range = is_excel_selection_range()
    if selection_is_range is True:
        last_range_seen_at = now
        return True
    if selection_is_range is False:
        last_non_range_seen_at = now
        return False

    recently_range = now - last_range_seen_at <= RANGE_CACHE_SECONDS
    range_is_newer = last_range_seen_at > last_non_range_seen_at
    return recently_range and range_is_newer


def excel_caret_status(require_blink=False):
    _hwnd, thread_id, pid = foreground_window_info()
    if not pid.value or not thread_id:
        return False
    if process_name_from_pid(pid) != "excel.exe":
        return False

    info = GUITHREADINFO()
    info.cbSize = ctypes.sizeof(GUITHREADINFO)
    if not user32.GetGUIThreadInfo(thread_id, ctypes.byref(info)):
        return False

    caret_rect = info.rcCaret
    has_caret_rect = caret_rect.left != caret_rect.right or caret_rect.top != caret_rect.bottom
    if not bool(info.hwndCaret) or not has_caret_rect:
        return False
    if require_blink and not bool(info.flags & GUI_CARETBLINKING):
        return False
    return True


def excel_cell_editing_status():
    state, reason = get_strong_edit_state()
    return state == EditState.CELL_EDITING, reason


def get_strong_edit_state():
    hwnd, _thread_id, pid = foreground_window_info()
    if not pid.value or process_name_from_pid(pid) != "excel.exe":
        return EditState.NOT_EDITING, "セル内入力中ではありません"

    if excel_ui_is_textbox_context(hwnd):
        return EditState.OBJECT_EDITING, "セル内入力中ではありません"

    selection_is_range = is_excel_selection_range()
    if selection_is_range is False:
        return EditState.OBJECT_EDITING, "セル内入力中ではありません"
    if selection_is_range == "busy":
        return EditState.CELL_EDITING, "セル内入力中"

    commandbars_editing = is_excel_cell_edit_mode_by_commandbars()
    if commandbars_editing is True:
        return EditState.CELL_EDITING, "セル内入力中"
    if commandbars_editing is False:
        return EditState.NOT_EDITING, "セル内入力中ではありません"

    if selection_is_range is True and excel_caret_status(require_blink=True):
        return EditState.CELL_EDITING, "セル内入力中"

    if selection_is_range is True:
        return EditState.UNKNOWN, "セル内入力中を確認できません"

    if excel_caret_status(require_blink=True):
        return EditState.UNKNOWN, "セル内入力中を確認できません"

    return EditState.UNKNOWN, "セル内入力中を確認できません"


def is_excel_editing_cell():
    active, _reason = excel_cell_editing_status()
    return active


def current_activation_status():
    if not is_excel_foreground():
        return False, "セル内入力中ではありません"

    return excel_cell_editing_status()


def foreground_gui_thread_info():
    _hwnd, thread_id, pid = foreground_window_info()
    if not pid.value or not thread_id:
        return None

    info = GUITHREADINFO()
    info.cbSize = ctypes.sizeof(GUITHREADINFO)
    if not user32.GetGUIThreadInfo(thread_id, ctypes.byref(info)):
        return None
    return info


def foreground_ime_target_hwnds():
    info = foreground_gui_thread_info()
    if not info:
        return []

    hwnds = []
    for hwnd in (info.hwndFocus, info.hwndCaret, info.hwndActive):
        if hwnd and hwnd not in hwnds:
            hwnds.append(hwnd)
    return hwnds


def is_ime_composing():
    for hwnd in foreground_ime_target_hwnds():
        ime_context = imm32.ImmGetContext(hwnd)
        if not ime_context:
            continue

        try:
            length = imm32.ImmGetCompositionStringW(ime_context, GCS_COMPSTR, None, 0)
            if length > 0:
                return True
        finally:
            imm32.ImmReleaseContext(hwnd, ime_context)
    return False


def is_ime_open():
    for hwnd in foreground_ime_target_hwnds():
        ime_context = imm32.ImmGetContext(hwnd)
        if ime_context:
            try:
                if imm32.ImmGetOpenStatus(ime_context):
                    return True
            finally:
                imm32.ImmReleaseContext(hwnd, ime_context)

        ime_hwnd = imm32.ImmGetDefaultIMEWnd(hwnd)
        if ime_hwnd and user32.SendMessageW(ime_hwnd, WM_IME_CONTROL, IMC_GETOPENSTATUS, 0):
            return True
    return False


def is_ime_related_key(vk_code):
    if 0x30 <= vk_code <= 0x5A:
        return True
    if 0xBA <= vk_code <= 0xE2:
        return True
    return vk_code in {
        VK_BACK,
        VK_SPACE,
        VK_PRIOR,
        VK_NEXT,
        VK_END,
        VK_HOME,
        VK_LEFT,
        VK_UP,
        VK_RIGHT,
        VK_DOWN,
        VK_DELETE,
        VK_PROCESSKEY,
    }


def is_text_entry_key(vk_code):
    if 0x30 <= vk_code <= 0x5A:
        return True
    if 0x60 <= vk_code <= 0x6F:
        return True
    if 0xBA <= vk_code <= 0xE2:
        return True
    return vk_code in {VK_SPACE, VK_PROCESSKEY}


class KeyboardHook:
    def __init__(self, config_provider, event_queue):
        self.config_provider = config_provider
        self.event_queue = event_queue
        self.hook = None
        self.callback = LowLevelKeyboardProc(self._callback)
        self.thread = None
        self.thread_id = None
        self.running = threading.Event()
        self.last_log = 0.0
        self.pending_conversion_key = None
        self.pending_conversion_modifiers = {"ctrl": False, "shift": False}
        self.ime_confirm_pending = False
        self.inferred_cell_editing = False
        self.inferred_until = 0.0
        self.last_selection_is_range = None
        self.last_selection_seen_at = 0.0
        self.last_non_editing_confirmed_at = 0.0

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.pending_conversion_key = None
        self.running.set()
        self.thread = threading.Thread(target=self._run, name="keyboard-hook", daemon=True)
        self.thread.start()

    def stop(self):
        self.running.clear()
        self.pending_conversion_key = None
        self.ime_confirm_pending = False
        self.inferred_cell_editing = False
        self.inferred_until = 0.0
        self.last_selection_is_range = None
        self.last_selection_seen_at = 0.0
        self.last_non_editing_confirmed_at = 0.0
        if self.thread_id:
            user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.5)
        self.thread_id = None

    def _run(self):
        self.thread_id = kernel32.GetCurrentThreadId()
        module = kernel32.GetModuleHandleW(None)
        self.hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self.callback, module, 0)
        if not self.hook:
            self.event_queue.put(("error", "error_hook_start"))
            return

        self.event_queue.put(("status", "監視中"))
        msg = wintypes.MSG()
        while self.running.is_set() and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        if self.hook:
            user32.UnhookWindowsHookEx(self.hook)
            self.hook = None
        self.event_queue.put(("status", "停止中"))

    def _callback(self, n_code, w_param, l_param):
        if n_code < 0:
            return user32.CallNextHookEx(self.hook, n_code, w_param, l_param)

        info = ctypes.cast(l_param, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        if info.flags & LLKHF_INJECTED:
            return user32.CallNextHookEx(self.hook, n_code, w_param, l_param)

        if w_param in (WM_KEYDOWN, WM_SYSKEYDOWN):
            self._track_editing_context(info.vkCode)
            self._track_ime_activity(info.vkCode)
            if self.pending_conversion_key == info.vkCode:
                return 1
            if self._should_convert(info.vkCode):
                self.pending_conversion_key = info.vkCode
                self.pending_conversion_modifiers = self._current_trigger_modifiers()
                return 1

        if w_param in (WM_KEYUP, WM_SYSKEYUP) and self.pending_conversion_key == info.vkCode:
            self.pending_conversion_key = None
            modifiers = self.pending_conversion_modifiers.copy()
            threading.Timer(0.02, self._send_conversion, args=(modifiers,)).start()
            return 1

        return user32.CallNextHookEx(self.hook, n_code, w_param, l_param)

    def _send_conversion(self, modifiers):
        self._wait_for_modifiers_released(modifiers)
        if send_excel_line_break():
            self._log_conversion()
        else:
            self.event_queue.put(("error", "error_send_break"))

    def _current_trigger_modifiers(self):
        config = self.config_provider()
        trigger = TRIGGERS.get(config["trigger"], TRIGGERS[DEFAULT_CONFIG["trigger"]])
        return {"ctrl": trigger["ctrl"], "shift": trigger["shift"]}

    def _wait_for_modifiers_released(self, modifiers):
        deadline = time.time() + 0.7
        while time.time() < deadline:
            ctrl_still_down = modifiers["ctrl"] and is_key_down(VK_CONTROL)
            shift_still_down = modifiers["shift"] and is_key_down(VK_SHIFT)
            if not ctrl_still_down and not shift_still_down:
                return
            time.sleep(0.01)

    def _track_ime_activity(self, vk_code):
        if vk_code == VK_RETURN:
            return
        if not is_ime_related_key(vk_code):
            return
        config = self.config_provider()
        ime_is_active = is_ime_open() or is_ime_composing() or vk_code == VK_PROCESSKEY
        active, _reason = excel_cell_editing_status()
        if not active:
            if ime_is_active:
                self.ime_confirm_pending = True
            return
        if ime_is_active or (config["trigger"] == "Enter" and vk_code == VK_SPACE):
            self.ime_confirm_pending = True
        else:
            self.ime_confirm_pending = False

    def _should_convert(self, vk_code):
        config = self.config_provider()
        if not config["enabled"]:
            return False
        if config["excel_only"] and not is_excel_foreground():
            self._clear_inferred_editing()
            return False

        trigger = TRIGGERS[config["trigger"]]
        if vk_code != trigger["key"]:
            return False

        ctrl = is_key_down(VK_CONTROL)
        shift = is_key_down(VK_SHIFT)
        if ctrl != trigger["ctrl"] or shift != trigger["shift"]:
            return False

        if config["edit_only"] and not self._trigger_allows_conversion(config["trigger"]):
            return False

        if config["trigger"] == "Enter" and is_ime_composing():
            return False
        if config["trigger"] == "Enter" and self.ime_confirm_pending:
            self.ime_confirm_pending = False
            return False

        if config["trigger"] == "Enter" and self.recently_confirmed_not_editing():
            self._clear_inferred_editing()
            return False

        return True

    def _trigger_allows_conversion(self, trigger_name):
        state, _reason = self.get_edit_state()
        if trigger_name == "Shift + Enter":
            if state == EditState.OBJECT_EDITING:
                return False
            if state in (EditState.CELL_EDITING, EditState.NOT_EDITING):
                return True
            selection_is_range = is_excel_selection_range()
            if selection_is_range is True:
                self.update_selection_context(selection_is_range)
                return True
            if selection_is_range is False:
                self.update_selection_context(selection_is_range)
                return False
            if selection_is_range == "busy":
                return True
            cached_selection_is_range = self.cached_selection_is_range()
            if cached_selection_is_range is True:
                return True
            if cached_selection_is_range is False:
                return False
            hwnd, _thread_id, _pid = foreground_window_info()
            return is_excel_foreground() and not excel_ui_is_textbox_context(hwnd)

        return state == EditState.CELL_EDITING

    def refresh_non_editing_guard(self):
        selection_is_range = is_excel_selection_range()
        if selection_is_range is True:
            self.update_selection_context(selection_is_range)
            commandbars_editing = is_excel_cell_edit_mode_by_commandbars()
            if commandbars_editing is False:
                self.last_non_editing_confirmed_at = time.time()
                self._clear_inferred_editing()
                return True
        elif selection_is_range is False:
            self.update_selection_context(selection_is_range)

        return False

    def recently_confirmed_not_editing(self):
        return time.time() - self.last_non_editing_confirmed_at <= 1.0


    def _log_conversion(self):
        now = time.time()
        if now - self.last_log > 0.2:
            self.last_log = now
            self.event_queue.put(("converted", time.strftime("%H:%M:%S")))

    def is_inferred_editing(self):
        if self.inferred_cell_editing and time.time() <= self.inferred_until:
            return True
        self.inferred_cell_editing = False
        return False

    def get_edit_state(self):
        state, reason = get_strong_edit_state()
        if state == EditState.OBJECT_EDITING:
            self._clear_inferred_editing()
            return state, reason
        if state == EditState.CELL_EDITING:
            return state, reason
        if self.is_inferred_editing():
            return EditState.CELL_EDITING, self.inferred_reason()
        if state == EditState.NOT_EDITING:
            self._clear_inferred_editing()
            return state, reason
        return EditState.UNKNOWN, reason

    def _clear_inferred_editing(self):
        self.inferred_cell_editing = False
        self.inferred_until = 0.0

    def update_selection_context(self, selection_is_range=None):
        if selection_is_range is None:
            selection_is_range = is_excel_selection_range()
        if selection_is_range is True:
            self.last_selection_is_range = True
            self.last_selection_seen_at = time.time()
        elif selection_is_range is False:
            self.last_selection_is_range = False
            self.last_selection_seen_at = time.time()

    def cached_selection_is_range(self):
        if time.time() - self.last_selection_seen_at > 30.0:
            return None
        return self.last_selection_is_range

    def _track_editing_context(self, vk_code):
        if not is_excel_foreground():
            self._clear_inferred_editing()
            return

        hwnd, _thread_id, _pid = foreground_window_info()
        if excel_ui_is_textbox_context(hwnd):
            self._clear_inferred_editing()
            return

        if vk_code in {VK_ESCAPE, VK_TAB}:
            self._clear_inferred_editing()
            return

        if vk_code == VK_RETURN and is_key_down(VK_CONTROL):
            self._clear_inferred_editing()
            return

        if vk_code == VK_RETURN and self.inferred_cell_editing:
            selection_is_range = is_excel_selection_range()
            if selection_is_range is False and self.cached_selection_is_range() is False:
                self.update_selection_context(selection_is_range)
                self._clear_inferred_editing()
            return

        starts_editing = vk_code == VK_F2 or (
            is_text_entry_key(vk_code)
            and not is_key_down(VK_CONTROL)
            and not is_key_down(VK_MENU)
        )
        if starts_editing and self.is_inferred_editing():
            self.last_non_editing_confirmed_at = 0.0
            self.inferred_until = time.time() + 60.0
            return

        if starts_editing:
            selection_is_range = is_excel_selection_range()
            cached_selection_is_range = self.cached_selection_is_range()
            if selection_is_range is None:
                selection_is_range = cached_selection_is_range
            if selection_is_range in (True, "busy"):
                self.inferred_cell_editing = True
                self.inferred_until = time.time() + 60.0
                self.last_non_editing_confirmed_at = 0.0
                self.update_selection_context(True)
            elif selection_is_range is None and cached_selection_is_range is not False:
                self.inferred_cell_editing = True
                self.inferred_until = time.time() + 8.0
                self.last_non_editing_confirmed_at = 0.0
            else:
                self.update_selection_context(selection_is_range)
                self._clear_inferred_editing()

    def inferred_reason(self):
        if self.is_inferred_editing():
            return "セル内入力中"
        return None


def set_window_proc(hwnd, proc):
    proc_ptr = ctypes.cast(proc, ctypes.c_void_p)
    if ctypes.sizeof(ctypes.c_void_p) == 8:
        return user32.SetWindowLongPtrW(hwnd, GWLP_WNDPROC, proc_ptr)
    return user32.SetWindowLongW(hwnd, GWLP_WNDPROC, proc_ptr)


class TrayIcon:
    def __init__(self, app):
        self.app = app
        self.hwnd = app.hwnd
        self.icon_added = False
        self.old_wndproc = None
        self.wndproc = WindowProc(self._wndproc)
        self.normal_icon = load_app_icon()
        self.paused_icon = create_paused_tray_icon()

    def install(self):
        self.old_wndproc = set_window_proc(self.hwnd, self.wndproc)
        self._add_icon()

    def remove(self):
        if self.icon_added:
            shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(self._notify_data()))
            self.icon_added = False
        if self.old_wndproc:
            if ctypes.sizeof(ctypes.c_void_p) == 8:
                user32.SetWindowLongPtrW(self.hwnd, GWLP_WNDPROC, self.old_wndproc)
            else:
                user32.SetWindowLongW(self.hwnd, GWLP_WNDPROC, self.old_wndproc)
            self.old_wndproc = None

    def _notify_data(self):
        data = NOTIFYICONDATA()
        data.cbSize = ctypes.sizeof(NOTIFYICONDATA)
        data.hWnd = self.hwnd
        data.uID = 1
        data.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
        data.uCallbackMessage = WM_TRAYICON
        data.hIcon = self.paused_icon if self.app.paused else self.normal_icon
        data.szTip = self.app.t("app_name")
        data.uVersion = NOTIFYICON_VERSION_4
        return data

    def _add_icon(self):
        data = self._notify_data()
        if shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(data)):
            self.icon_added = True
            shell32.Shell_NotifyIconW(NIM_SETVERSION, ctypes.byref(data))

    def update_icon(self):
        if self.icon_added:
            shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(self._notify_data()))

    def _wndproc(self, hwnd, msg, w_param, l_param):
        if msg == WM_TRAYICON:
            event = int(l_param) & 0xFFFF
            if event == WM_RBUTTONUP:
                self._show_menu()
                return 0
            if event == WM_LBUTTONDBLCLK:
                self.app.show_dialog()
                return 0
        if self.old_wndproc:
            return user32.CallWindowProcW(self.old_wndproc, hwnd, msg, w_param, l_param)
        return 0

    def _show_menu(self):
        menu = user32.CreatePopupMenu()
        if not menu:
            return

        try:
            startup_registered = is_startup_registered()
            user32.AppendMenuW(menu, MF_STRING, MENU_SHOW_DIALOG, self.app.t("menu_open"))
            pause_label = self.app.t("button_resume") if self.app.paused else self.app.t("button_pause")
            user32.AppendMenuW(menu, MF_STRING, MENU_PAUSE_TOGGLE, pause_label)
            user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
            add_flags = MF_STRING | (MF_GRAYED if startup_registered else 0)
            remove_flags = MF_STRING | (0 if startup_registered else MF_GRAYED)
            user32.AppendMenuW(menu, add_flags, MENU_STARTUP_ADD, self.app.t("menu_startup_add"))
            user32.AppendMenuW(menu, remove_flags, MENU_STARTUP_REMOVE, self.app.t("menu_startup_remove"))
            user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
            ja_flags = MF_STRING | (MF_CHECKED if self.app.language == "ja" else 0)
            en_flags = MF_STRING | (MF_CHECKED if self.app.language == "en" else 0)
            user32.AppendMenuW(menu, ja_flags, MENU_LANGUAGE_JA, self.app.t("menu_language_ja"))
            user32.AppendMenuW(menu, en_flags, MENU_LANGUAGE_EN, self.app.t("menu_language_en"))
            user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
            user32.AppendMenuW(menu, MF_STRING, MENU_DEVELOPER_WEBSITE, self.app.t("menu_developer_website"))
            user32.AppendMenuW(menu, MF_STRING, MENU_ABOUT, self.app.t("menu_about"))
            user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
            user32.AppendMenuW(menu, MF_STRING, MENU_EXIT, self.app.t("menu_exit"))

            point = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(point))
            user32.SetForegroundWindow(self.hwnd)
            command = user32.TrackPopupMenu(
                menu,
                TPM_RIGHTBUTTON | TPM_RETURNCMD | TPM_NONOTIFY,
                point.x,
                point.y,
                0,
                self.hwnd,
                None,
            )
            self._handle_menu_command(command)
        finally:
            user32.DestroyMenu(menu)

    def _handle_menu_command(self, command):
        if command == MENU_SHOW_DIALOG:
            self.app.show_dialog()
        elif command == MENU_PAUSE_TOGGLE:
            self.app._set_paused(not self.app.paused)
            self.app._refresh_active_status()
        elif command == MENU_STARTUP_ADD:
            register_startup()
        elif command == MENU_STARTUP_REMOVE:
            unregister_startup()
        elif command == MENU_LANGUAGE_JA:
            self.app._set_language("ja")
        elif command == MENU_LANGUAGE_EN:
            self.app._set_language("en")
        elif command == MENU_DEVELOPER_WEBSITE:
            open_developer_website(self.hwnd)
        elif command == MENU_ABOUT:
            app_name = self.app.t("app_name")
            user32.MessageBoxW(
                self.hwnd,
                self.app.t("about_body").format(
                    app_name=app_name,
                    version=APP_VERSION,
                    build_datetime=APP_BUILD_DATETIME,
                ),
                self.app.t("about_title").format(app_name=app_name),
                0,
            )
        elif command == MENU_EXIT:
            self.app.quit_app()


class App:
    CLASS_NAME = "ItsumonoKaigyoForExcelWindow"

    def __init__(self, start_minimized=False):
        self.start_minimized = start_minimized
        self.config_data = load_config()
        self.language = self.config_data["language"]
        self.paused = False
        self.events = queue.Queue()
        self.hook = KeyboardHook(lambda: self.config_data.copy(), self.events)
        self.tray = None
        self.hwnd = None
        self.wndproc = WindowProc(self._wndproc)
        self.controls = {}
        self.control_text = {}
        self.fonts = {
            "title": create_font(24, FW_BOLD),
            "body": create_font(16, FW_NORMAL),
            "body_bold": create_font(16, FW_BOLD),
        }
        self._register_class()
        self._create_window()
        self._create_controls()
        self._apply_config_to_controls()
        self.tray = TrayIcon(self)
        self.tray.install()
        user32.SetTimer(self.hwnd, STATUS_TIMER_ID, 250, None)

    def _register_class(self):
        instance = kernel32.GetModuleHandleW(None)
        wndclass = WNDCLASS()
        wndclass.lpfnWndProc = self.wndproc
        wndclass.hInstance = instance
        wndclass.hIcon = load_app_icon()
        wndclass.hbrBackground = ctypes.c_void_p(COLOR_BTNFACE + 1)
        wndclass.lpszClassName = self.CLASS_NAME
        user32.RegisterClassW(ctypes.byref(wndclass))

    def _create_window(self):
        self.hwnd = user32.CreateWindowExW(
            0,
            self.CLASS_NAME,
            self.t("app_name"),
            WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
            CW_USEDEFAULT,
            CW_USEDEFAULT,
            500,
            335,
            None,
            None,
            kernel32.GetModuleHandleW(None),
            None,
        )
        user32.ShowWindow(self.hwnd, SW_HIDE if self.start_minimized else SW_SHOWNORMAL)
        user32.UpdateWindow(self.hwnd)

    def _create_control(self, class_name, text, style, x, y, w, h, control_id=0):
        hwnd = user32.CreateWindowExW(
            0,
            class_name,
            text,
            WS_CHILD | WS_VISIBLE | style,
            x,
            y,
            w,
            h,
            self.hwnd,
            control_id,
            kernel32.GetModuleHandleW(None),
            None,
        )
        return hwnd

    def _set_font(self, hwnd, font_key):
        user32.SendMessageW(hwnd, WM_SETFONT, self.fonts[font_key], True)

    def _create_controls(self):
        self.controls["title"] = self._create_control("STATIC", self.t("app_name"), SS_LEFT, 24, 22, 340, 32)
        self.controls["language"] = self._create_control("BUTTON", self.t("button_language"), BS_PUSHBUTTON, 382, 24, 72, 28, CONTROL_BUTTON_LANGUAGE)
        self.controls["subtitle"] = self._create_control(
            "STATIC",
            self.t("subtitle"),
            SS_LEFT,
            24,
            62,
            430,
            42,
        )
        self.controls["group"] = self._create_control("BUTTON", self.t("line_break_key"), BS_GROUPBOX, 24, 112, 430, 66)
        self.controls["radio_enter"] = self._create_control(
            "BUTTON",
            "Enter",
            BS_AUTORADIOBUTTON | WS_GROUP | WS_TABSTOP,
            50,
            140,
            160,
            24,
            CONTROL_RADIO_ENTER,
        )
        self.controls["radio_shift_enter"] = self._create_control(
            "BUTTON",
            "Shift + Enter",
            BS_AUTORADIOBUTTON | WS_TABSTOP,
            248,
            140,
            180,
            24,
            CONTROL_RADIO_SHIFT_ENTER,
        )
        self.controls["active"] = self._create_control("STATIC", self.status_text("status_initial"), SS_LEFT, 24, 200, 430, 24)
        self.controls["exit"] = self._create_control("BUTTON", self.t("button_exit"), BS_PUSHBUTTON, 180, 238, 82, 32, CONTROL_BUTTON_EXIT)
        self.controls["pause"] = self._create_control("BUTTON", self.t("button_pause"), BS_PUSHBUTTON, 272, 238, 90, 32, CONTROL_BUTTON_PAUSE)
        self.controls["minimize"] = self._create_control("BUTTON", self.t("button_minimize"), BS_PUSHBUTTON, 372, 238, 82, 32, CONTROL_BUTTON_MINIMIZE)
        self._apply_fonts()

    def t(self, key):
        return text_for(self.language, key)

    def translated_reason(self, reason):
        return self.t(STATUS_REASON_KEYS.get(reason, reason))

    def status_text(self, reason_or_key):
        reason = self.t(reason_or_key) if reason_or_key in TEXTS[self.language] else self.translated_reason(reason_or_key)
        return f"{self.t('status_prefix')}{reason}"

    def _apply_language_to_controls(self):
        user32.SetWindowTextW(self.hwnd, self.t("app_name"))
        self._set_text("title", self.t("app_name"))
        self._set_text("subtitle", self.t("subtitle"))
        self._set_text("group", self.t("line_break_key"))
        self._set_text("exit", self.t("button_exit"))
        self._set_text("minimize", self.t("button_minimize"))
        self._set_text("pause", self.t("button_resume") if self.paused else self.t("button_pause"))
        self._set_text("language", self.t("button_language"))
        if self.tray:
            self.tray.update_icon()
        self._refresh_active_status()

    def _apply_fonts(self):
        for key, hwnd in self.controls.items():
            if key == "title":
                self._set_font(hwnd, "title")
            else:
                self._set_font(hwnd, "body")

    def _apply_config_to_controls(self):
        enter_checked = BST_CHECKED if self.config_data["trigger"] == "Enter" else 0
        shift_checked = BST_CHECKED if self.config_data["trigger"] == "Shift + Enter" else 0
        user32.SendMessageW(self.controls["radio_enter"], BM_SETCHECK, enter_checked, 0)
        user32.SendMessageW(self.controls["radio_shift_enter"], BM_SETCHECK, shift_checked, 0)
        self._set_status(f"状態: 一時停止中 / キー: {self.config_data['trigger']}")

    def _set_trigger(self, trigger):
        self.config_data["trigger"] = trigger
        self.config_data["excel_only"] = True
        self.config_data["edit_only"] = True
        self.config_data["enabled"] = True
        save_config(self.config_data)
        self._apply_config_to_controls()

    def _set_language(self, language):
        if language not in LANGUAGES or language == self.language:
            return
        self.language = language
        self.config_data["language"] = language
        save_config(self.config_data)
        self._apply_language_to_controls()

    def _set_text(self, key, text):
        if self.control_text.get(key) == text:
            return
        user32.SetWindowTextW(self.controls[key], text)
        self.control_text[key] = text

    def _set_status(self, text):
        if "status" in self.controls:
            self._set_text("status", text)

    def _set_paused(self, paused):
        self.paused = paused
        self._set_text("pause", self.t("button_resume") if self.paused else self.t("button_pause"))
        if self.tray:
            self.tray.update_icon()
        if self.paused:
            self.hook.stop()

    def _poll_events(self):
        while True:
            try:
                event, value = self.events.get_nowait()
            except queue.Empty:
                break
            if event == "error":
                user32.MessageBoxW(self.hwnd, self.t(value), self.t("app_name"), 0)
                self._set_status("状態: エラー")
            elif event == "converted":
                pass

    def _refresh_active_status(self):
        if self.paused:
            self.hook.stop()
            self._set_text("active", self.status_text("status_paused"))
            self._set_status(f"状態: 一時停止中 / キー: {self.config_data['trigger']}")
            return

        if is_excel_foreground():
            self.hook.start()
            self.hook.refresh_non_editing_guard()
            if not self.hook.is_inferred_editing():
                self.hook.update_selection_context()
            state, reason = self.hook.get_edit_state()
        else:
            self.hook.stop()
            state, reason = EditState.NOT_EDITING, "セル内入力中ではありません"

        active = state == EditState.CELL_EDITING
        self._set_text("active", self.status_text(reason))

        if is_excel_foreground():
            if active:
                self._set_status(f"状態: 監視中 / キー: {self.config_data['trigger']}")
            else:
                self._set_status(f"状態: 待機中 / キー: {self.config_data['trigger']}")
        else:
            self._set_status(f"状態: 一時停止中 / キー: {self.config_data['trigger']}")


    def _wndproc(self, hwnd, msg, w_param, l_param):
        if msg == WM_COMMAND:
            control_id = int(w_param) & 0xFFFF
            if control_id == CONTROL_RADIO_ENTER:
                self._set_trigger("Enter")
                return 0
            if control_id == CONTROL_RADIO_SHIFT_ENTER:
                self._set_trigger("Shift + Enter")
                return 0
            if control_id == CONTROL_BUTTON_MINIMIZE:
                self.hide_dialog()
                return 0
            if control_id == CONTROL_BUTTON_PAUSE:
                self._set_paused(not self.paused)
                self._refresh_active_status()
                return 0
            if control_id == CONTROL_BUTTON_LANGUAGE:
                self._set_language("en" if self.language == "ja" else "ja")
                return 0
            if control_id == CONTROL_BUTTON_EXIT:
                self.quit_app()
                return 0
        elif msg == WM_TIMER:
            self._poll_events()
            self._refresh_active_status()
            return 0
        elif msg == WM_CLOSE:
            self.hide_dialog()
            return 0
        elif msg == WM_DESTROY:
            user32.PostQuitMessage(0)
            return 0
        return user32.DefWindowProcW(hwnd, msg, w_param, l_param)

    def show_dialog(self):
        user32.ShowWindow(self.hwnd, SW_SHOW)
        user32.SetForegroundWindow(self.hwnd)

    def hide_dialog(self):
        user32.ShowWindow(self.hwnd, SW_HIDE)

    def quit_app(self):
        user32.KillTimer(self.hwnd, STATUS_TIMER_ID)
        self.hook.stop()
        if self.tray:
            self.tray.remove()
            self.tray = None
        user32.PostQuitMessage(0)

    def run(self):
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))


def main():
    if sys.platform != "win32":
        print("This app only runs on Windows.")
        return 1
    startup_language = load_config()["language"]
    startup_app_name = text_for(startup_language, "app_name")
    mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if not mutex:
        user32.MessageBoxW(None, text_for(startup_language, "error_single_instance"), startup_app_name, 0)
        return 1
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        user32.MessageBoxW(None, text_for(startup_language, "already_running"), startup_app_name, 0)
        kernel32.CloseHandle(mutex)
        return 0

    try:
        app = App(start_minimized=START_MINIMIZED_ARG in sys.argv[1:])
        app.run()
        return 0
    finally:
        kernel32.CloseHandle(mutex)


if __name__ == "__main__":
    raise SystemExit(main())
