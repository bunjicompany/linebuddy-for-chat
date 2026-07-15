import ctypes
import copy
import json
import os
import queue
import re
import sys
import threading
import time
import winreg
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path


APP_NAME = "いつもの改行 for Chat"
APP_NAME_EN = "LineBuddy for Chat"
APP_VERSION = "v1.1.1"
DEVELOPER_NAME = "ぶんじカンパニー"
DEVELOPER_NAME_EN = "Bunji Company"
DEVELOPER_URL = "https://bunjicompany.com/"
CONFIG_PATH = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
) / "ItsumonoKaigyoForChat_settings.json"
DEBUG_LOG_PATH = CONFIG_PATH.with_name("debug.log")
DEBUG_LOG_MAX_BYTES = 512 * 1024
DEBUG_LOG_ENABLED = False
IME_CANDIDATE_CACHE_SECONDS = 0.1
_ime_candidate_cache = {
    "key": None,
    "timestamp": 0.0,
    "value": False,
}

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong
LRESULT = ctypes.c_ssize_t

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_KEYUP = 0x0101
WM_SYSKEYUP = 0x0105
WM_QUIT = 0x0012
WM_COMMAND = 0x0111
WM_CLOSE = 0x0010
WM_DESTROY = 0x0002
WM_DRAWITEM = 0x002B
WM_SETCURSOR = 0x0020
WM_SETICON = 0x0080
ICON_SMALL = 0
ICON_BIG = 1
SM_CXSMICON = 49
SM_CYSMICON = 50
SM_CXICON = 11
SM_CYICON = 12
WM_NOTIFY = 0x004E
WM_TIMER = 0x0113
WM_SETFONT = 0x0030
WM_VSCROLL = 0x0115
WM_MOUSEWHEEL = 0x020A
WM_IME_CONTROL = 0x0283
WM_RBUTTONUP = 0x0205
WM_LBUTTONDBLCLK = 0x0203
WM_TRAYICON = 0x0400 + 77

VK_RETURN = 0x0D
VK_MENU = 0x12
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_SPACE = 0x20
VK_ESCAPE = 0x1B
VK_TAB = 0x09
VK_BACK = 0x08
VK_DELETE = 0x2E
VK_F2 = 0x71
VK_PROCESSKEY = 0xE5

GCS_COMPSTR = 0x0008
GCS_COMPATTR = 0x0010
GCS_COMPCLAUSE = 0x0020
IMM_ERROR_NODATA = -1
IMM_ERROR_GENERAL = -2
IME_RECENT_INPUT_SECONDS = 8.0
ENTER_SUPPRESS_AFTER_CONVERSION_SECONDS = 0.18
WRAP_SHIFT_HOLD_SECONDS = 0.3
WRAP_SHIFT_KEYUP_LINGER_SECONDS = 0.12
WRAP_SHIFT_MAX_HOLD_SECONDS = 2.0
WRAP_RESIDUAL_SHIFT_SECONDS = 0.5
SEND_EXTRA_INFO = 0x49544B47
IMC_GETOPENSTATUS = 0x0005
IMC_GETCONVERSIONMODE = 0x0001
IME_CMODE_NATIVE = 0x0001

LLKHF_INJECTED = 0x10
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
GUI_CARETBLINKING = 0x0001
SCAN_ENTER = 0x1C
SCAN_SHIFT = 0x2A

SW_HIDE = 0
SW_SHOWMINIMIZED = 2
SW_SHOW = 5
SW_SHOWNORMAL = 1
CW_USEDEFAULT = -2147483648

WS_OVERLAPPED = 0x00000000
WS_CAPTION = 0x00C00000
WS_SYSMENU = 0x00080000
WS_MINIMIZEBOX = 0x00020000
WS_VISIBLE = 0x10000000
WS_CHILD = 0x40000000
WS_TABSTOP = 0x00010000
WS_GROUP = 0x00020000
WS_VSCROLL = 0x00200000
WS_BORDER = 0x00800000

ES_AUTOHSCROLL = 0x0080
BS_PUSHBUTTON = 0x00000000
BS_DEFPUSHBUTTON = 0x00000001
BS_AUTOCHECKBOX = 0x00000003
BS_RADIOBUTTON = 0x00000004
BS_AUTORADIOBUTTON = 0x00000009
BS_OWNERDRAW = 0x0000000B
BS_FLAT = 0x00008000
BS_PUSHLIKE = 0x00001000
SS_LEFT = 0x00000000
SS_CENTERIMAGE = 0x00000200
ICC_TAB_CLASSES = 0x00000008
TCM_FIRST = 0x1300
TCM_GETCURSEL = TCM_FIRST + 11
TCM_SETCURSEL = TCM_FIRST + 12
TCM_INSERTITEMW = TCM_FIRST + 62
TCIF_TEXT = 0x0001
TCN_FIRST = -550
TCN_SELCHANGE = TCN_FIRST - 1
CBS_DROPDOWNLIST = 0x0003
CBS_HASSTRINGS = 0x0200

BM_SETCHECK = 0x00F1
BM_GETCHECK = 0x00F0
BST_CHECKED = 1
CB_ADDSTRING = 0x0143
CB_RESETCONTENT = 0x014B
CB_SETCURSEL = 0x014E
CB_GETCURSEL = 0x0147
CBN_SELCHANGE = 1
SB_CTL = 2
SB_LINEUP = 0
SB_LINEDOWN = 1
SB_PAGEUP = 2
SB_PAGEDOWN = 3
SB_THUMBPOSITION = 4
SB_THUMBTRACK = 5
SBS_VERT = 0x0001
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010

COLOR_WINDOW = 5
COLOR_BTNFACE = 15
COLOR_BTNTEXT = 18
FW_NORMAL = 400
FW_BOLD = 700
DEFAULT_CHARSET = 1
OUT_DEFAULT_PRECIS = 0
CLIP_DEFAULT_PRECIS = 0
DEFAULT_QUALITY = 0
DEFAULT_PITCH = 0
IMAGE_ICON = 1
LR_LOADFROMFILE = 0x00000010
LR_DEFAULTSIZE = 0x00000040
IDI_APPLICATION = 32512
MF_STRING = 0x00000000
MF_SEPARATOR = 0x00000800
MF_CHECKED = 0x00000008
MF_GRAYED = 0x00000001
MB_OK = 0x00000000
MB_OKCANCEL = 0x00000001
IDOK = 1
TPM_RIGHTBUTTON = 0x0002
TPM_RETURNCMD = 0x0100
TPM_NONOTIFY = 0x0080
NIF_MESSAGE = 0x00000001
NIF_ICON = 0x00000002
NIF_TIP = 0x00000004
NIM_ADD = 0x00000000
NIM_MODIFY = 0x00000001
NIM_DELETE = 0x00000002
NIM_SETVERSION = 0x00000004
NOTIFYICON_VERSION_4 = 4
EDGE_RAISED = 0x0005
EDGE_SUNKEN = 0x000A
BF_RECT = 0x000F
ODS_SELECTED = 0x0001
ODS_HOTLIGHT = 0x0040
PS_SOLID = 0
TRANSPARENT = 1
DT_LEFT = 0x00000000
DT_CENTER = 0x00000001
DT_VCENTER = 0x00000004
DT_SINGLELINE = 0x00000020

ERROR_ALREADY_EXISTS = 183
MUTEX_NAME = "Local\\ItsumonoKaigyoForWindows.SingleInstance"
START_MINIMIZED_ARG = "--start-minimized"
STARTUP_RUN_NAME = "ItsumonoKaigyoForChat"
LANG_JA = "ja"
LANG_EN = "en"

MODE_ENTER = "enter"
MODE_SHIFT_ENTER = "shift_enter"
MODE_OFF = "off"
CONFIG_MODE_ON = "on"
MODE_ORDER = [MODE_ENTER, MODE_SHIFT_ENTER, MODE_OFF]
AI_SNS_MODE_ORDER = [MODE_ENTER, MODE_OFF]
MODE_LABELS = {
    MODE_ENTER: "Enterで改行",
    MODE_SHIFT_ENTER: "Shift+Enterで改行",
    MODE_OFF: "オフ",
}
AI_SNS_MODE_LABELS = {
    MODE_ENTER: "オン",
    MODE_OFF: "オフ",
}
ACTION_SHIFT_ENTER = "shift_enter"

DEFAULT_BROWSER_PROCESSES = (
    "chrome.exe",
    "msedge.exe",
    "firefox.exe",
    "brave.exe",
    "opera.exe",
    "vivaldi.exe",
    "sleipnir.exe",
)
DEFAULT_CHROMIUM_BROWSER_PROCESSES = (
    "chrome.exe",
    "msedge.exe",
    "brave.exe",
    "opera.exe",
    "vivaldi.exe",
    "sleipnir.exe",
)
DEFAULT_SHIFT_ENTER_WRAP_PROCESSES = (
    "sleipnir.exe",
)
BROWSER_PROCESSES = set(DEFAULT_BROWSER_PROCESSES)
CHROMIUM_BROWSER_PROCESSES = set(DEFAULT_CHROMIUM_BROWSER_PROCESSES)
CHROMIUM_PAGE_FOCUS_CLASSES = {
    "Chrome_RenderWidgetHostHWND",
}
UIA_URL_FIELD_KEYWORDS = (
    "address",
    "search or enter web address",
    "アドレス",
    "検索語句または URL",
    "検索または URL",
)

CLSCTX_INPROC_SERVER = 0x1
UIA_CONTROL_TYPE_EDIT = 50004
UIA_VALUE_PATTERN_ID = 10002
TREE_SCOPE_DESCENDANTS = 0x00000004
MAX_UIA_URL_ELEMENTS = 120

CONTROL_MAIN_PAUSE = 1001
CONTROL_MAIN_SETTINGS = 1002
CONTROL_MAIN_MINIMIZE = 1003
CONTROL_MAIN_EXIT = 1004
CONTROL_MAIN_LANGUAGE = 1005
CONTROL_SETTINGS_SAVE = 2003
CONTROL_SETTINGS_CANCEL = 2004
CONTROL_SETTINGS_SCROLLBAR = 2005
CONTROL_SETTINGS_CUSTOM_EDIT = 2006
CONTROL_SETTINGS_RESET_DEFAULTS = 2007
CONTROL_SETTINGS_TAB_BASE = 2100
CONTROL_SETTINGS_CHECK_BASE = 3000
CONTROL_CUSTOM_TARGET_SELECT = 7001
CONTROL_CUSTOM_LABEL = 7002
CONTROL_CUSTOM_SURFACE = 7003
CONTROL_CUSTOM_PROCESSES = 7010
CONTROL_CUSTOM_TITLE_KEYWORDS = 7020
CONTROL_CUSTOM_URL_KEYWORDS = 7030
CONTROL_CUSTOM_DEFAULT_MODE = 7040
CONTROL_CUSTOM_SAVE = 7041
CONTROL_CUSTOM_CANCEL = 7042
CONTROL_CUSTOM_TITLE_REGEX = 7050
CONTROL_CUSTOM_PROCESSES_REGEX = 7051
CONTROL_CUSTOM_URL_REGEX = 7052
STATUS_TIMER_ID = 4001
TRAY_UID = 5001
TRAY_MENU_OPEN = 6001
TRAY_MENU_PAUSE = 6002
TRAY_MENU_SETTINGS = 6003
TRAY_MENU_STARTUP_ENABLE = 6004
TRAY_MENU_STARTUP_DISABLE = 6005
TRAY_MENU_LANG_JA = 6006
TRAY_MENU_LANG_EN = 6007
TRAY_MENU_DEVELOPER_SITE = 6008
TRAY_MENU_ABOUT = 6009
TRAY_MENU_EXIT = 6010


kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
shell32 = ctypes.windll.shell32
imm32 = ctypes.windll.imm32
comctl32 = ctypes.windll.comctl32
ole32 = ctypes.windll.ole32
oleaut32 = ctypes.windll.oleaut32


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
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
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


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


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
        ("rcCaret", RECT),
    ]


class INITCOMMONCONTROLSEX(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("dwICC", wintypes.DWORD),
    ]


class NMHDR(ctypes.Structure):
    _fields_ = [
        ("hwndFrom", wintypes.HWND),
        ("idFrom", ULONG_PTR),
        ("code", ctypes.c_int),
    ]


class TCITEMW(ctypes.Structure):
    _fields_ = [
        ("mask", wintypes.UINT),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("pszText", wintypes.LPWSTR),
        ("cchTextMax", ctypes.c_int),
        ("iImage", ctypes.c_int),
        ("lParam", wintypes.LPARAM),
    ]


class DRAWITEMSTRUCT(ctypes.Structure):
    _fields_ = [
        ("CtlType", wintypes.UINT),
        ("CtlID", wintypes.UINT),
        ("itemID", wintypes.UINT),
        ("itemAction", wintypes.UINT),
        ("itemState", wintypes.UINT),
        ("hwndItem", wintypes.HWND),
        ("hDC", wintypes.HDC),
        ("rcItem", RECT),
        ("itemData", ULONG_PTR),
    ]


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]


def guid(data1, data2, data3, data4):
    return GUID(data1, data2, data3, (ctypes.c_ubyte * 8)(*data4))


IID_NULL = guid(0, 0, 0, [0, 0, 0, 0, 0, 0, 0, 0])


WndProcType = ctypes.WINFUNCTYPE(
    LRESULT,
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
)
EnumChildProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


class WNDCLASS(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", WndProcType),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HANDLE),
        ("hCursor", wintypes.HANDLE),
        ("hbrBackground", wintypes.HANDLE),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]


class NOTIFYICONDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT),
        ("uCallbackMessage", wintypes.UINT),
        ("hIcon", wintypes.HANDLE),
        ("szTip", ctypes.c_wchar * 128),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("szInfo", ctypes.c_wchar * 256),
        ("uVersion", wintypes.UINT),
        ("szInfoTitle", ctypes.c_wchar * 64),
        ("dwInfoFlags", wintypes.DWORD),
    ]


LowLevelKeyboardProc = ctypes.WINFUNCTYPE(
    LRESULT,
    ctypes.c_int,
    wintypes.WPARAM,
    wintypes.LPARAM,
)

user32.SetWindowsHookExW.argtypes = [
    ctypes.c_int,
    LowLevelKeyboardProc,
    wintypes.HINSTANCE,
    wintypes.DWORD,
]
user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
user32.CallNextHookEx.restype = LRESULT
user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL
user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = ctypes.c_short
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL
user32.EnumChildWindows.argtypes = [wintypes.HWND, EnumChildProc, wintypes.LPARAM]
user32.EnumChildWindows.restype = wintypes.BOOL
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
user32.GetWindowRect.restype = wintypes.BOOL
user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
user32.GetAncestor.restype = wintypes.HWND
user32.GetGUIThreadInfo.argtypes = [wintypes.DWORD, ctypes.POINTER(GUITHREADINFO)]
user32.GetGUIThreadInfo.restype = wintypes.BOOL
user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostThreadMessageW.restype = wintypes.BOOL
user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL
user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.TranslateMessage.restype = wintypes.BOOL
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.restype = LRESULT
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = LRESULT
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
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL
user32.UpdateWindow.argtypes = [wintypes.HWND]
user32.UpdateWindow.restype = wintypes.BOOL
user32.InvalidateRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT), wintypes.BOOL]
user32.InvalidateRect.restype = wintypes.BOOL
user32.SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
user32.SetWindowTextW.restype = wintypes.BOOL
user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, ctypes.c_void_p]
user32.SendMessageW.restype = ctypes.c_long
user32.SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT,
]
user32.SetWindowPos.restype = wintypes.BOOL
user32.SetScrollRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.BOOL]
user32.SetScrollRange.restype = wintypes.BOOL
user32.SetScrollPos.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, wintypes.BOOL]
user32.SetScrollPos.restype = ctypes.c_int
user32.SetTimer.argtypes = [wintypes.HWND, ULONG_PTR, wintypes.UINT, ctypes.c_void_p]
user32.SetTimer.restype = ULONG_PTR
user32.KillTimer.argtypes = [wintypes.HWND, ULONG_PTR]
user32.KillTimer.restype = wintypes.BOOL
user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.DestroyWindow.restype = wintypes.BOOL
user32.EnableWindow.argtypes = [wintypes.HWND, wintypes.BOOL]
user32.EnableWindow.restype = wintypes.BOOL
user32.MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
user32.MessageBoxW.restype = ctypes.c_int
user32.DrawEdge.argtypes = [wintypes.HDC, ctypes.POINTER(RECT), wintypes.UINT, wintypes.UINT]
user32.DrawEdge.restype = wintypes.BOOL
user32.DrawTextW.argtypes = [wintypes.HDC, wintypes.LPCWSTR, ctypes.c_int, ctypes.POINTER(RECT), wintypes.UINT]
user32.DrawTextW.restype = ctypes.c_int
user32.FillRect.argtypes = [wintypes.HDC, ctypes.POINTER(RECT), wintypes.HBRUSH]
user32.FillRect.restype = ctypes.c_int
user32.GetSysColorBrush.argtypes = [ctypes.c_int]
user32.GetSysColorBrush.restype = wintypes.HBRUSH
gdi32.CreateSolidBrush.argtypes = [wintypes.COLORREF]
gdi32.CreateSolidBrush.restype = wintypes.HBRUSH
gdi32.CreatePen.argtypes = [ctypes.c_int, ctypes.c_int, wintypes.COLORREF]
gdi32.CreatePen.restype = wintypes.HANDLE
gdi32.MoveToEx.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
gdi32.MoveToEx.restype = wintypes.BOOL
gdi32.LineTo.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
gdi32.LineTo.restype = wintypes.BOOL
gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
gdi32.DeleteObject.restype = wintypes.BOOL
user32.PostQuitMessage.argtypes = [ctypes.c_int]
user32.PostQuitMessage.restype = None
user32.LoadImageW.argtypes = [
    wintypes.HINSTANCE,
    wintypes.LPCWSTR,
    wintypes.UINT,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT,
]
user32.LoadImageW.restype = wintypes.HANDLE
user32.LoadIconW.argtypes = [wintypes.HINSTANCE, ctypes.c_void_p]
user32.LoadIconW.restype = wintypes.HANDLE
user32.GetSystemMetrics.argtypes = [ctypes.c_int]
user32.GetSystemMetrics.restype = ctypes.c_int
user32.CreatePopupMenu.restype = wintypes.HMENU
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
user32.TrackPopupMenu.restype = ctypes.c_int
user32.DestroyMenu.argtypes = [wintypes.HMENU]
user32.DestroyMenu.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
shell32.ShellExecuteW.argtypes = [
    wintypes.HWND,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    ctypes.c_int,
]
shell32.ShellExecuteW.restype = wintypes.HINSTANCE
user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
user32.GetCursorPos.restype = wintypes.BOOL
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetCurrentThreadId.restype = wintypes.DWORD
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
kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.GetLastError.restype = wintypes.DWORD
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
gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
gdi32.SelectObject.restype = wintypes.HGDIOBJ
gdi32.SetBkMode.argtypes = [wintypes.HDC, ctypes.c_int]
gdi32.SetBkMode.restype = ctypes.c_int
gdi32.SetTextColor.argtypes = [wintypes.HDC, wintypes.COLORREF]
gdi32.SetTextColor.restype = wintypes.COLORREF
shell32.Shell_NotifyIconW.argtypes = [wintypes.DWORD, ctypes.POINTER(NOTIFYICONDATA)]
shell32.Shell_NotifyIconW.restype = wintypes.BOOL
comctl32.InitCommonControlsEx.argtypes = [ctypes.POINTER(INITCOMMONCONTROLSEX)]
comctl32.InitCommonControlsEx.restype = wintypes.BOOL
ole32.CoInitialize.argtypes = [ctypes.c_void_p]
ole32.CoInitialize.restype = ctypes.c_long
ole32.CoCreateInstance.argtypes = [
    ctypes.POINTER(GUID),
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(GUID),
    ctypes.POINTER(ctypes.c_void_p),
]
ole32.CoCreateInstance.restype = ctypes.c_long
oleaut32.SysFreeString.argtypes = [ctypes.c_void_p]
oleaut32.SysFreeString.restype = None
imm32.ImmGetContext.argtypes = [wintypes.HWND]
imm32.ImmGetContext.restype = wintypes.HANDLE
imm32.ImmGetDefaultIMEWnd.argtypes = [wintypes.HWND]
imm32.ImmGetDefaultIMEWnd.restype = wintypes.HWND
imm32.ImmReleaseContext.argtypes = [wintypes.HWND, wintypes.HANDLE]
imm32.ImmReleaseContext.restype = wintypes.BOOL
imm32.ImmGetOpenStatus.argtypes = [wintypes.HANDLE]
imm32.ImmGetOpenStatus.restype = wintypes.BOOL
imm32.ImmGetCompositionStringW.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
imm32.ImmGetCompositionStringW.restype = ctypes.c_long

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
S_OK = 0
S_FALSE = 1
RPC_E_CHANGED_MODE = 0x80010106


@dataclass(frozen=True)
class TargetDefinition:
    key: str
    label: str
    category: str
    surface: str
    action: str
    default_mode: str
    processes: tuple[str, ...] = ()
    window_title_keywords: tuple[str, ...] = ()
    url_keywords: tuple[str, ...] = ()
    processes_regex: bool = False
    window_title_keywords_regex: bool = False
    url_keywords_regex: bool = False


BUILTIN_TARGETS = [
    TargetDefinition("chatgpt_web", "ChatGPT Web", "生成AI", "Web", ACTION_SHIFT_ENTER, MODE_ENTER, window_title_keywords=("chatgpt", "openai"), url_keywords=("chatgpt.com", "openai.com")),
    TargetDefinition("chatgpt_app", "ChatGPT App", "生成AI", "App", ACTION_SHIFT_ENTER, MODE_ENTER, processes=("chatgpt.exe",), window_title_keywords=("chatgpt",)),
    TargetDefinition("codex_app", "Codex App", "生成AI", "App", ACTION_SHIFT_ENTER, MODE_ENTER, processes=("codex.exe",), window_title_keywords=("codex",)),
    TargetDefinition("claude_web", "Claude Web", "生成AI", "Web", ACTION_SHIFT_ENTER, MODE_ENTER, window_title_keywords=("claude",), url_keywords=("claude.ai",)),
    TargetDefinition("claude_app", "Claude App", "生成AI", "App", ACTION_SHIFT_ENTER, MODE_ENTER, processes=("claude.exe",), window_title_keywords=("claude",)),
    TargetDefinition("gemini_web", "Gemini Web", "生成AI", "Web", ACTION_SHIFT_ENTER, MODE_ENTER, window_title_keywords=("gemini",), url_keywords=("gemini.google.com",)),
    TargetDefinition("copilot_web", "Copilot Web", "生成AI", "Web", ACTION_SHIFT_ENTER, MODE_ENTER, window_title_keywords=("copilot",), url_keywords=("copilot.microsoft.com", "m365copilot.com", "m365.cloud.microsoft/chat")),
    TargetDefinition("copilot_app", "Copilot App", "生成AI", "App", ACTION_SHIFT_ENTER, MODE_ENTER, processes=("copilot.exe",), window_title_keywords=("copilot",)),
    TargetDefinition("perplexity_web", "Perplexity Web", "生成AI", "Web", ACTION_SHIFT_ENTER, MODE_ENTER, window_title_keywords=("perplexity",), url_keywords=("perplexity.ai",)),
    TargetDefinition("grok_web", "Grok Web", "生成AI", "Web", ACTION_SHIFT_ENTER, MODE_ENTER, window_title_keywords=("grok",), url_keywords=("grok.com", "x.com/i/grok")),
    TargetDefinition("deepseek_web", "DeepSeek Web", "生成AI", "Web", ACTION_SHIFT_ENTER, MODE_ENTER, window_title_keywords=("deepseek",), url_keywords=("deepseek.com",)),
    TargetDefinition("agent_i_web", "Agent i Web", "生成AI", "Web", ACTION_SHIFT_ENTER, MODE_ENTER, window_title_keywords=("agent i",), url_keywords=("search.yahoo.co.jp/chat",)),
    TargetDefinition("line_app", "LINE App", "SNS・チャット", "App", ACTION_SHIFT_ENTER, MODE_ENTER, processes=("line.exe",)),
    TargetDefinition("x_web", "X Web", "SNS・チャット", "Web", ACTION_SHIFT_ENTER, MODE_OFF, window_title_keywords=("x.com", "twitter", "/ x", "- x"), url_keywords=("x.com", "twitter.com")),
    TargetDefinition("slack_web", "Slack Web", "SNS・チャット", "Web", ACTION_SHIFT_ENTER, MODE_OFF, window_title_keywords=("slack",), url_keywords=("slack.com",)),
    TargetDefinition("slack_app", "Slack App", "SNS・チャット", "App", ACTION_SHIFT_ENTER, MODE_OFF, processes=("slack.exe",), window_title_keywords=("slack",)),
    TargetDefinition("discord_web", "Discord Web", "SNS・チャット", "Web", ACTION_SHIFT_ENTER, MODE_ENTER, window_title_keywords=("discord",), url_keywords=("discord.com",)),
    TargetDefinition("discord_app", "Discord App", "SNS・チャット", "App", ACTION_SHIFT_ENTER, MODE_ENTER, processes=("discord.exe",), window_title_keywords=("discord",)),
    TargetDefinition("teams_web", "Teams Web", "SNS・チャット", "Web", ACTION_SHIFT_ENTER, MODE_ENTER, window_title_keywords=("teams",), url_keywords=("teams.microsoft.com",)),
    TargetDefinition("teams_app", "Teams App", "SNS・チャット", "App", ACTION_SHIFT_ENTER, MODE_ENTER, processes=("ms-teams.exe", "teams.exe"), window_title_keywords=("teams",)),
    TargetDefinition("instagram_web", "Instagram Web", "SNS・チャット", "Web", ACTION_SHIFT_ENTER, MODE_OFF, window_title_keywords=("instagram",), url_keywords=("instagram.com",)),
    TargetDefinition("whatsapp_web", "WhatsApp Web", "SNS・チャット", "Web", ACTION_SHIFT_ENTER, MODE_ENTER, window_title_keywords=("whatsapp",), url_keywords=("web.whatsapp.com",)),
    TargetDefinition("whatsapp_app", "WhatsApp App", "SNS・チャット", "App", ACTION_SHIFT_ENTER, MODE_ENTER, processes=("whatsapp.exe",), window_title_keywords=("whatsapp",)),
]
DEFAULT_CATEGORIES = ["生成AI", "SNS・チャット"]
TARGETS = list(BUILTIN_TARGETS)
CATEGORIES = list(DEFAULT_CATEGORIES)


def uses_on_off_config(action):
    return action == ACTION_SHIFT_ENTER


def internal_mode_from_config_values(action, mode):
    mode = str(mode).strip()
    if uses_on_off_config(action):
        if mode == CONFIG_MODE_ON:
            return MODE_ENTER
        return MODE_OFF
    return mode if mode in MODE_ORDER else MODE_OFF


def config_mode_from_values(action, mode):
    mode = str(mode).strip()
    if uses_on_off_config(action):
        return CONFIG_MODE_ON if mode in (CONFIG_MODE_ON, MODE_ENTER) else MODE_OFF
    return mode if mode in MODE_ORDER else MODE_OFF


def string_tuple(value):
    if isinstance(value, str):
        text = value.strip()
        return (text,) if text else ()
    if isinstance(value, list):
        result = []
        for item in value:
            text = str(item).strip()
            if text:
                result.append(text)
        return tuple(result)
    return ()


def process_name_list(value, default=()):
    source = value if isinstance(value, list) else list(default)
    result = []
    seen = set()
    for item in source:
        name = str(item).strip().lower()
        if not name:
            continue
        if not name.endswith(".exe"):
            name = f"{name}.exe"
        if name not in seen:
            result.append(name)
            seen.add(name)
    return result


def apply_browser_process_config(browser_processes, chromium_browser_processes):
    global BROWSER_PROCESSES, CHROMIUM_BROWSER_PROCESSES
    browsers = set(process_name_list(browser_processes, DEFAULT_BROWSER_PROCESSES))
    chromium = set(process_name_list(chromium_browser_processes, DEFAULT_CHROMIUM_BROWSER_PROCESSES))
    CHROMIUM_BROWSER_PROCESSES = chromium & browsers
    BROWSER_PROCESSES = browsers


REGEX_FLAG_FIELDS = (
    ("processes", "processes_regex"),
    ("window_title_keywords", "window_title_keywords_regex"),
    ("url_keywords", "url_keywords_regex"),
)


def ensure_regex_flags(item):
    if isinstance(item, dict):
        for field, flag in REGEX_FLAG_FIELDS:
            if field in item and flag not in item:
                item[flag] = False
    return item


_regex_cache = {}


def compiled_regex(pattern):
    if pattern in _regex_cache:
        return _regex_cache[pattern]
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error as error:
        debug_log(f"invalid regex ignored pattern={pattern!r} error={error}")
        compiled = None
    _regex_cache[pattern] = compiled
    return compiled


def regex_error_text(pattern):
    try:
        re.compile(pattern, re.IGNORECASE)
        return ""
    except re.error as error:
        return str(error)


def parse_target_configs(value, reserved_keys=()):
    if not isinstance(value, list):
        return []
    parsed_targets = []
    used_keys = set(reserved_keys)
    for item in value:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key", "")).strip()
        if not re.fullmatch(r"[a-z0-9_]{1,40}", key) or key in used_keys:
            continue
        label = str(item.get("label", key)).strip() or key
        category = str(item.get("category", "生成AI")).strip() or "生成AI"
        surface_value = str(item.get("surface", "App")).strip().lower()
        surface = "Web" if surface_value == "web" else "App"
        action = str(item.get("action", ACTION_SHIFT_ENTER)).strip()
        action = ACTION_SHIFT_ENTER
        default_mode = str(item.get("default_mode", MODE_OFF)).strip()
        default_mode = internal_mode_from_config_values(action, default_mode)
        processes = string_tuple(item.get("processes", ()))
        window_title_keywords = string_tuple(item.get("window_title_keywords", ()))
        url_keywords = string_tuple(item.get("url_keywords", ()))
        processes_regex = bool(item.get("processes_regex", False))
        window_title_keywords_regex = bool(item.get("window_title_keywords_regex", False))
        url_keywords_regex = bool(item.get("url_keywords_regex", False))
        is_custom_slot = key.startswith(("gai_custom_", "sns_custom_"))
        if not is_custom_slot:
            if surface == "Web" and not (window_title_keywords or url_keywords):
                continue
            if surface == "App" and not (processes or window_title_keywords):
                continue
        parsed_targets.append(
            TargetDefinition(
                key,
                label,
                category,
                surface,
                action,
                default_mode,
                processes=processes,
                window_title_keywords=window_title_keywords,
                url_keywords=url_keywords,
                processes_regex=processes_regex,
                window_title_keywords_regex=window_title_keywords_regex,
                url_keywords_regex=url_keywords_regex,
            )
        )
        used_keys.add(key)
    return parsed_targets


def parse_custom_targets(value):
    return parse_target_configs(value, {target.key for target in BUILTIN_TARGETS})


def activate_targets(targets):
    global TARGETS, CATEGORIES
    TARGETS = list(targets)
    CATEGORIES = list(DEFAULT_CATEGORIES)
    for target in TARGETS:
        if target.category not in CATEGORIES:
            CATEGORIES.append(target.category)
        if target.processes_regex:
            for pattern in target.processes:
                compiled_regex(pattern)
        if target.window_title_keywords_regex:
            for pattern in target.window_title_keywords:
                compiled_regex(pattern)
        if target.url_keywords_regex:
            for pattern in target.url_keywords:
                compiled_regex(pattern)


def configured_targets(target_definition_configs, custom_target_configs):
    if isinstance(target_definition_configs, list):
        parsed_targets = parse_target_configs(target_definition_configs)
        if parsed_targets:
            targets_by_key = {target.key: target for target in parsed_targets}
            builtin_keys = {target.key for target in BUILTIN_TARGETS}
            default_builtin_targets = parse_target_configs([
                target_definition_config(target)
                for target in BUILTIN_TARGETS
            ])
            return [
                targets_by_key.get(target.key, target)
                for target in default_builtin_targets
            ] + [
                target for target in parsed_targets
                if target.key not in builtin_keys
            ]
    return parse_target_configs([
        target_definition_config(target)
        for target in BUILTIN_TARGETS
    ]) + parse_custom_targets(custom_target_configs)


def default_builtin_target_definition_configs():
    return [
        target_definition_config(target)
        for target in BUILTIN_TARGETS
    ]


def merge_missing_keywords(existing_values, default_values):
    """既存の設定を残しつつ、内蔵プリセットの新しいキーワードだけを追記する。"""
    merged = list(string_tuple(existing_values))
    seen = {value.casefold() for value in merged}
    for value in string_tuple(default_values):
        if value.casefold() not in seen:
            merged.append(value)
            seen.add(value.casefold())
    return merged


def merge_builtin_target_definition_configs(target_definition_configs):
    if not isinstance(target_definition_configs, list):
        target_definition_configs = []
    source_items = json.loads(json.dumps(target_definition_configs))
    builtin_keys = {target.key for target in BUILTIN_TARGETS}
    existing_by_key = {}
    for item in source_items:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key", "")).strip()
        if key and key not in existing_by_key:
            existing_by_key[key] = item
    merged = []
    for item in default_builtin_target_definition_configs():
        existing_item = existing_by_key.get(item["key"])
        if existing_item:
            existing_item["window_title_keywords"] = []
            existing_item["window_title_keywords_regex"] = False
            # 既存JSONにも、新しく追加したWeb判定URLを補完する。
            if item.get("url_keywords"):
                existing_item["url_keywords"] = merge_missing_keywords(
                    existing_item.get("url_keywords", []),
                    item["url_keywords"],
                )
            merged.append(existing_item)
        else:
            merged.append(item)
    for item in source_items:
        if not isinstance(item, dict):
            merged.append(item)
            continue
        key = str(item.get("key", "")).strip()
        if key not in builtin_keys:
            merged.append(item)
    return [ensure_regex_flags(item) for item in merged]


def target_definition_config(target):
    window_title_keywords = []
    url_keywords = list(target.url_keywords)
    data = {
        "key": target.key,
        "label": target.label,
        "category": target.category,
        "surface": target.surface,
        "action": target.action,
        "window_title_keywords": window_title_keywords,
        "window_title_keywords_regex": bool(target.window_title_keywords_regex),
        "default_mode": config_mode_from_values(target.action, target.default_mode),
    }
    if target.processes:
        data["processes"] = list(target.processes)
        data["processes_regex"] = bool(target.processes_regex)
    if target.surface == "Web" or url_keywords:
        data["url_keywords"] = url_keywords
        data["url_keywords_regex"] = bool(target.url_keywords_regex)
    return data


def default_custom_target_configs():
    result = []
    for index in range(1, 4):
        result.append({
            "key": f"gai_custom_{index}",
            "label": f"GAI Custom {index}",
            "category": "生成AI",
            "surface": "Web",
            "action": ACTION_SHIFT_ENTER,
            "window_title_keywords": [],
            "window_title_keywords_regex": False,
            "url_keywords": [],
            "url_keywords_regex": False,
            "default_mode": MODE_OFF,
        })
    for index in range(1, 4):
        result.append({
            "key": f"sns_custom_{index}",
            "label": f"SNS Custom {index}",
            "category": "SNS・チャット",
            "surface": "App",
            "action": ACTION_SHIFT_ENTER,
            "processes": [],
            "processes_regex": False,
            "window_title_keywords": [],
            "window_title_keywords_regex": False,
            "default_mode": MODE_OFF,
        })
    return result


def default_target_definitions_config():
    return default_builtin_target_definition_configs() + default_custom_target_configs()


def mode_options_for_target(target):
    return AI_SNS_MODE_ORDER


def mode_options_for_category(category):
    return AI_SNS_MODE_ORDER


def normalize_mode_for_target(target, mode):
    options = mode_options_for_target(target)
    return mode if mode in options else MODE_OFF


def internal_mode_from_config_for_target(target, mode):
    return normalize_mode_for_target(
        target,
        internal_mode_from_config_values(target.action, mode),
    )


def config_mode_for_target(target, mode):
    return config_mode_from_values(target.action, normalize_mode_for_target(target, mode))


def config_for_save(config):
    data = copy.deepcopy(config)
    targets = data.get("targets", {})
    if isinstance(targets, dict):
        for target in TARGETS:
            if target.key in targets:
                targets[target.key] = config_mode_for_target(target, targets[target.key])
    definitions = data.get("target_definitions", [])
    if isinstance(definitions, list):
        for item in definitions:
            if not isinstance(item, dict):
                continue
            item["default_mode"] = config_mode_from_values(str(item.get("action", ACTION_SHIFT_ENTER)), item.get("default_mode", MODE_OFF))
    return data


def default_config():
    return {
        "enabled": True,
        "language": LANG_JA,
        "debug_log_enabled": False,
        "browser_processes": list(DEFAULT_BROWSER_PROCESSES),
        "chromium_browser_processes": list(DEFAULT_CHROMIUM_BROWSER_PROCESSES),
        "shift_enter_wrap_processes": list(DEFAULT_SHIFT_ENTER_WRAP_PROCESSES),
        "targets": {target.key: target.default_mode for target in TARGETS},
        "target_definitions": default_target_definitions_config(),
        "custom_targets": [],
    }


_debug_log_lock = threading.Lock()


def debug_log(message):
    if not DEBUG_LOG_ENABLED:
        return
    try:
        # フックスレッド・UIAワーカー・タイマー・GUIから同時に呼ばれるため、
        # ローテーションと追記をロックで直列化する（欠落・破損防止）。
        with _debug_log_lock:
            if DEBUG_LOG_PATH.exists() and DEBUG_LOG_PATH.stat().st_size > DEBUG_LOG_MAX_BYTES:
                backup_path = DEBUG_LOG_PATH.with_name("debug.log.1")
                if backup_path.exists():
                    backup_path.unlink()
                DEBUG_LOG_PATH.replace(backup_path)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with DEBUG_LOG_PATH.open("a", encoding="utf-8") as file:
                file.write(f"{timestamp} {message}\n")
    except OSError:
        pass


def load_config():
    global DEBUG_LOG_ENABLED
    loaded = {}
    config_exists = CONFIG_PATH.exists()
    if config_exists:
        try:
            loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            loaded = {}
    if not isinstance(loaded, dict):
        loaded = {}
    if config_exists:
        target_definition_configs = merge_builtin_target_definition_configs(loaded.get("target_definitions", []))
        custom_target_configs = loaded.get("custom_targets", [])
    else:
        target_definition_configs = default_target_definitions_config()
        custom_target_configs = []
    activate_targets(configured_targets(target_definition_configs, custom_target_configs))
    config = default_config()
    config["target_definitions"] = target_definition_configs if isinstance(target_definition_configs, list) else []
    config["custom_targets"] = custom_target_configs if isinstance(custom_target_configs, list) else []
    config["enabled"] = bool(loaded.get("enabled", config["enabled"]))
    config["debug_log_enabled"] = bool(loaded.get("debug_log_enabled", config["debug_log_enabled"]))
    config["browser_processes"] = process_name_list(loaded.get("browser_processes", config["browser_processes"]), DEFAULT_BROWSER_PROCESSES)
    config["chromium_browser_processes"] = process_name_list(loaded.get("chromium_browser_processes", config["chromium_browser_processes"]), DEFAULT_CHROMIUM_BROWSER_PROCESSES)
    # 旧キー shift_enter_send_on_keydown_processes からの自動移行に対応。
    config["shift_enter_wrap_processes"] = process_name_list(
        loaded.get(
            "shift_enter_wrap_processes",
            loaded.get("shift_enter_send_on_keydown_processes", config["shift_enter_wrap_processes"]),
        ),
        DEFAULT_SHIFT_ENTER_WRAP_PROCESSES,
    )
    apply_browser_process_config(config["browser_processes"], config["chromium_browser_processes"])
    DEBUG_LOG_ENABLED = config["debug_log_enabled"]
    language = loaded.get("language", config["language"])
    config["language"] = language if language in (LANG_JA, LANG_EN) else LANG_JA
    loaded_targets = loaded.get("targets", {})
    if isinstance(loaded_targets, dict):
        target_by_key = {target.key: target for target in TARGETS}
        for key, mode in loaded_targets.items():
            target = target_by_key.get(key)
            if target:
                config["targets"][key] = internal_mode_from_config_for_target(target, mode)
    for target in TARGETS:
        config["targets"][target.key] = normalize_mode_for_target(target, config["targets"].get(target.key, target.default_mode))
    if (
        not config_exists
        or target_definition_configs != loaded.get("target_definitions", [])
        or config["browser_processes"] != loaded.get("browser_processes")
        or config["chromium_browser_processes"] != loaded.get("chromium_browser_processes")
        or config["shift_enter_wrap_processes"] != loaded.get("shift_enter_wrap_processes")
        or "shift_enter_send_method_by_process" in loaded
        or "shift_enter_send_on_keydown_processes" in loaded
    ):
        try:
            save_config(config)
        except OSError:
            pass
    return config


def save_config(config):
    CONFIG_PATH.write_text(json.dumps(config_for_save(config), ensure_ascii=False, indent=2), encoding="utf-8-sig")


def app_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def startup_command():
    return f'"{Path(sys.executable).resolve()}" {START_MINIMIZED_ARG}'


def is_startup_registered():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
            winreg.QueryValueEx(key, STARTUP_RUN_NAME)
        return True
    except OSError:
        return False


def set_startup_registered(enabled):
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            if enabled:
                winreg.SetValueEx(key, STARTUP_RUN_NAME, 0, winreg.REG_SZ, startup_command())
            else:
                try:
                    winreg.DeleteValue(key, STARTUP_RUN_NAME)
                except FileNotFoundError:
                    pass
        return True
    except OSError as exc:
        debug_log(f"startup registration failed enabled={enabled} error={exc}")
        return False


def is_key_down(vk_code):
    return bool(user32.GetAsyncKeyState(vk_code) & 0x8000)


def send_input(item):
    return user32.SendInput(1, ctypes.byref(item), ctypes.sizeof(INPUT)) == 1


def send_inputs(items):
    array_type = INPUT * len(items)
    array = array_type(*items)
    return user32.SendInput(len(items), array, ctypes.sizeof(INPUT)) == len(items)


def key_input(vk_code, key_up=False):
    return INPUT(
        type=1,
        ki=KEYBDINPUT(wVk=vk_code, wScan=0, dwFlags=KEYEVENTF_KEYUP if key_up else 0, time=0, dwExtraInfo=SEND_EXTRA_INFO),
    )


def send_key(vk_code, key_up=False):
    return send_input(key_input(vk_code, key_up=key_up))


def send_scan_key(scan_code, key_up=False):
    return send_input(scan_key_input(scan_code, key_up=key_up))


def scan_key_input(scan_code, key_up=False):
    return INPUT(
        type=1,
        ki=KEYBDINPUT(
            wVk=0,
            wScan=scan_code,
            dwFlags=KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if key_up else 0),
            time=0,
            dwExtraInfo=SEND_EXTRA_INFO,
        ),
    )


def release_current_enter_and_modifiers():
    shift_down = is_key_down(VK_SHIFT)
    ctrl_down = is_key_down(VK_CONTROL)
    alt_down = is_key_down(VK_MENU)
    enter_down = is_key_down(VK_RETURN)
    if enter_down:
        send_key(VK_RETURN, key_up=True)
    if shift_down:
        send_key(VK_SHIFT, key_up=True)
    if ctrl_down:
        send_key(VK_CONTROL, key_up=True)
    if alt_down:
        send_key(VK_MENU, key_up=True)
    return shift_down, ctrl_down, alt_down


def restore_modifiers(shift_down, ctrl_down, alt_down):
    if alt_down:
        send_key(VK_MENU)
    if ctrl_down:
        send_key(VK_CONTROL)
    if shift_down:
        send_key(VK_SHIFT)


def send_shift_enter():
    release_current_enter_and_modifiers()
    time.sleep(0.03)
    return send_inputs([
        scan_key_input(SCAN_SHIFT),
        scan_key_input(SCAN_ENTER),
        scan_key_input(SCAN_ENTER, key_up=True),
        scan_key_input(SCAN_SHIFT, key_up=True),
    ])


def send_line_break(action):
    if action == ACTION_SHIFT_ENTER:
        return send_shift_enter()
    return False


def foreground_window_info():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return 0, 0, wintypes.DWORD()
    pid = wintypes.DWORD()
    thread_id = user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return hwnd, thread_id, pid


def process_name_from_pid(pid):
    if not pid.value:
        return ""
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


def foreground_process_name():
    _hwnd, _thread_id, pid = foreground_window_info()
    return process_name_from_pid(pid)


def process_names_for_window_tree(hwnd):
    names = set()
    if not hwnd:
        return names
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    name = process_name_from_pid(pid)
    if name:
        names.add(name)

    def enum_child(child_hwnd, _lparam):
        child_pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(child_hwnd, ctypes.byref(child_pid))
        child_name = process_name_from_pid(child_pid)
        if child_name:
            names.add(child_name)
        return True

    callback = EnumChildProc(enum_child)
    user32.EnumChildWindows(hwnd, callback, 0)
    return names


def window_text(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def window_class_name(hwnd):
    if not hwnd:
        return ""
    buffer = ctypes.create_unicode_buffer(256)
    if not user32.GetClassNameW(hwnd, buffer, len(buffer)):
        return ""
    return buffer.value


def foreground_title():
    hwnd, _thread_id, _pid = foreground_window_info()
    return window_text(hwnd)


def foreground_gui_thread_info():
    _hwnd, thread_id, _pid = foreground_window_info()
    if not thread_id:
        return None
    info = GUITHREADINFO()
    info.cbSize = ctypes.sizeof(GUITHREADINFO)
    if not user32.GetGUIThreadInfo(thread_id, ctypes.byref(info)):
        return None
    return info


def foreground_window_rect():
    hwnd, _thread_id, _pid = foreground_window_info()
    if not hwnd:
        return None
    rect = RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None
    return rect


def foreground_focus_hwnds():
    hwnd, _thread_id, _pid = foreground_window_info()
    info = foreground_gui_thread_info()
    hwnds = []
    if info:
        hwnds.extend([info.hwndFocus, info.hwndCaret, info.hwndActive])
    hwnds.append(hwnd)
    result = []
    seen = set()
    for item in hwnds:
        value = int(item or 0)
        if value and value not in seen:
            seen.add(value)
            result.append(item)
    return result


def caret_has_size(rect):
    return rect.right != rect.left or rect.bottom != rect.top


def is_caret_in_browser_chrome():
    info = foreground_gui_thread_info()
    window_rect = foreground_window_rect()
    if not info or not window_rect or not info.hwndCaret or not caret_has_size(info.rcCaret):
        return False
    caret_top = info.rcCaret.top - window_rect.top
    caret_bottom = info.rcCaret.bottom - window_rect.top
    window_height = max(1, window_rect.bottom - window_rect.top)
    # Browser address bars and toolbar search fields live near the top edge.
    # Page prompt/chat editors are below the browser chrome.
    chrome_limit = min(145, max(92, int(window_height * 0.18)))
    in_chrome = caret_bottom <= chrome_limit
    if in_chrome:
        debug_log(
            f"browser chrome caret top={caret_top} bottom={caret_bottom} limit={chrome_limit} "
            f"focus_class={window_class_name(info.hwndFocus)!r}"
        )
    return in_chrome


def foreground_focus_class_names():
    return [window_class_name(hwnd) for hwnd in foreground_focus_hwnds() if window_class_name(hwnd)]


CLSID_CUIAutomation = guid(0xFF48DBA4, 0x60EF, 0x4201, [0xAA, 0x87, 0x54, 0x10, 0x3E, 0xEF, 0x59, 0x4E])
IID_IUIAutomation = guid(0x30CBE57D, 0xD9D0, 0x452A, [0xAB, 0x13, 0x7A, 0xC5, 0xAC, 0x48, 0x25, 0xEE])
_uia_automation = ctypes.c_void_p()
_browser_url_cache = {"hwnd": 0, "time": 0.0, "url": ""}


def com_release(ptr):
    if not ptr:
        return
    vtable = ctypes.cast(ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    release = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vtable[2])
    release(ptr)


def bstr_to_text(bstr):
    if not bstr:
        return ""
    try:
        return ctypes.wstring_at(bstr)
    finally:
        oleaut32.SysFreeString(bstr)


UIA_RETRY_SECONDS = 5.0
_uia_last_attempt = 0.0


def uia_automation():
    global _uia_automation, _uia_last_attempt
    if _uia_automation.value:
        return _uia_automation
    now = time.monotonic()
    if now - _uia_last_attempt < UIA_RETRY_SECONDS:
        return None
    _uia_last_attempt = now
    ole32.CoInitialize(None)
    ptr = ctypes.c_void_p()
    hr = ole32.CoCreateInstance(
        ctypes.byref(CLSID_CUIAutomation),
        None,
        CLSCTX_INPROC_SERVER,
        ctypes.byref(IID_IUIAutomation),
        ctypes.byref(ptr),
    )
    if hr < 0 or not ptr.value:
        debug_log(f"uia init failed hr={hr}")
        return None
    _uia_automation = ptr
    debug_log("uia init ok")
    return _uia_automation


def uia_reset():
    global _uia_automation
    ptr = _uia_automation
    _uia_automation = ctypes.c_void_p()
    if ptr.value:
        try:
            com_release(ptr)
        except Exception as exc:
            debug_log(f"uia reset release failed: {exc!r}")


def uia_focused_element_info():
    automation = uia_automation()
    if not automation:
        return {}
    element = ctypes.c_void_p()
    try:
        automation_vtable = ctypes.cast(automation, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        get_focused = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))(automation_vtable[8])
        hr = get_focused(automation, ctypes.byref(element))
        if hr < 0 or not element.value:
            return {}
        element_vtable = ctypes.cast(element, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        get_control_type = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int))(element_vtable[21])
        get_name = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))(element_vtable[23])
        get_class_name = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))(element_vtable[30])
        control_type = ctypes.c_int()
        name_bstr = ctypes.c_void_p()
        class_bstr = ctypes.c_void_p()
        name = ""
        class_name = ""
        if get_control_type(element, ctypes.byref(control_type)) < 0:
            control_type.value = 0
        if get_name(element, ctypes.byref(name_bstr)) >= 0:
            name = bstr_to_text(name_bstr.value)
        if get_class_name(element, ctypes.byref(class_bstr)) >= 0:
            class_name = bstr_to_text(class_bstr.value)
        return {"name": name, "class_name": class_name, "control_type": control_type.value}
    except Exception as exc:
        debug_log(f"uia focused failed: {exc}")
        return {}
    finally:
        if element.value:
            com_release(element)


def uia_element_text_info(element):
    if not element:
        return {}
    try:
        element_vtable = ctypes.cast(element, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        get_control_type = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int))(element_vtable[21])
        get_name = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))(element_vtable[23])
        get_class_name = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))(element_vtable[30])
        get_pattern = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))(element_vtable[16])
        control_type = ctypes.c_int()
        name_bstr = ctypes.c_void_p()
        class_bstr = ctypes.c_void_p()
        pattern = ctypes.c_void_p()
        name = ""
        class_name = ""
        value = ""
        if get_control_type(element, ctypes.byref(control_type)) < 0:
            control_type.value = 0
        if get_name(element, ctypes.byref(name_bstr)) >= 0:
            name = bstr_to_text(name_bstr.value)
        if get_class_name(element, ctypes.byref(class_bstr)) >= 0:
            class_name = bstr_to_text(class_bstr.value)
        if get_pattern(element, UIA_VALUE_PATTERN_ID, ctypes.byref(pattern)) >= 0 and pattern.value:
            try:
                pattern_vtable = ctypes.cast(pattern, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
                get_value = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))(pattern_vtable[4])
                value_bstr = ctypes.c_void_p()
                if get_value(pattern, ctypes.byref(value_bstr)) >= 0:
                    value = bstr_to_text(value_bstr.value)
            finally:
                com_release(pattern)
        return {"name": name, "class_name": class_name, "control_type": control_type.value, "value": value}
    except Exception as exc:
        debug_log(f"uia element info failed: {exc}")
        return {}


def looks_like_browser_url(text):
    lowered = (text or "").strip().lower()
    if lowered.startswith(("http://", "https://")):
        return True
    return "." in lowered and " " not in lowered and len(lowered) >= 4


def browser_current_url():
    hwnd, _thread_id, _pid = foreground_window_info()
    if not hwnd:
        return ""
    now = time.monotonic()
    if _browser_url_cache["hwnd"] == int(hwnd) and now - _browser_url_cache["time"] <= 1.0:
        return _browser_url_cache["url"]

    url = ""
    automation = uia_automation()
    root = ctypes.c_void_p()
    condition = ctypes.c_void_p()
    element_array = ctypes.c_void_p()
    try:
        if not automation:
            return ""
        automation_vtable = ctypes.cast(automation, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        element_from_handle = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, wintypes.HWND, ctypes.POINTER(ctypes.c_void_p))(automation_vtable[6])
        create_true_condition = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))(automation_vtable[21])
        if element_from_handle(automation, hwnd, ctypes.byref(root)) < 0 or not root.value:
            return ""
        if create_true_condition(automation, ctypes.byref(condition)) < 0 or not condition.value:
            return ""

        root_vtable = ctypes.cast(root, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        find_all = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))(root_vtable[6])
        if find_all(root, TREE_SCOPE_DESCENDANTS, condition, ctypes.byref(element_array)) < 0 or not element_array.value:
            return ""

        array_vtable = ctypes.cast(element_array, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        get_length = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int))(array_vtable[3])
        get_element = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))(array_vtable[4])
        length = ctypes.c_int()
        if get_length(element_array, ctypes.byref(length)) < 0:
            return ""

        for index in range(min(length.value, MAX_UIA_URL_ELEMENTS)):
            element = ctypes.c_void_p()
            if get_element(element_array, index, ctypes.byref(element)) < 0 or not element.value:
                continue
            try:
                info = uia_element_text_info(element)
                if info.get("control_type") != UIA_CONTROL_TYPE_EDIT:
                    continue
                label = f"{info.get('name', '')} {info.get('class_name', '')}".lower()
                value = info.get("value", "")
                if any(keyword.lower() in label for keyword in UIA_URL_FIELD_KEYWORDS) and looks_like_browser_url(value):
                    url = value.strip()
                    break
            finally:
                com_release(element)
    except Exception as exc:
        debug_log(f"browser url read failed: {exc}")
        url = ""
    finally:
        if element_array.value:
            com_release(element_array)
        if condition.value:
            com_release(condition)
        if root.value:
            com_release(root)
        # 別スレッドから読まれるため、判定キーのhwndを最後に書く。
        _browser_url_cache["url"] = url
        _browser_url_cache["time"] = now
        _browser_url_cache["hwnd"] = int(hwnd)
        if url:
            debug_log(f"browser url={url!r}")
    return url


def browser_cached_url(max_age_seconds=30.0):
    hwnd, _thread_id, _pid = foreground_window_info()
    if not hwnd:
        return ""
    now = time.monotonic()
    if _browser_url_cache["hwnd"] == int(hwnd) and now - _browser_url_cache["time"] <= max_age_seconds:
        return _browser_url_cache["url"]
    return ""


def is_browser_url_field_focused():
    info = uia_focused_element_info()
    if not info:
        return False
    name = info.get("name", "")
    class_name = info.get("class_name", "")
    control_type = info.get("control_type", 0)
    text = f"{name} {class_name}".lower()
    matched = control_type == UIA_CONTROL_TYPE_EDIT and any(keyword.lower() in text for keyword in UIA_URL_FIELD_KEYWORDS)
    if matched:
        debug_log(f"web skip: url field uia name={name!r} class={class_name!r} type={control_type}")
    else:
        debug_log(f"web uia focus name={name!r} class={class_name!r} type={control_type}")
    return matched


def is_web_input_area_active():
    foreground_process = foreground_process_name()
    focus_classes = foreground_focus_class_names()
    if foreground_process in CHROMIUM_BROWSER_PROCESSES and is_browser_url_field_focused():
        return False
    if is_caret_in_browser_chrome():
        debug_log(f"web skip: browser chrome process={foreground_process} classes={focus_classes}")
        return False
    if foreground_process in CHROMIUM_BROWSER_PROCESSES:
        debug_log(f"web allow: chromium focus process={foreground_process} classes={focus_classes}")
    return True


_web_input_cache = {"hwnd": 0, "time": 0.0, "value": True}
UIA_WORKER_INTERVAL_SECONDS = 0.25
WEB_INPUT_CACHE_MAX_AGE_SECONDS = 0.7


def is_web_input_area_active_cached(max_age_seconds=WEB_INPUT_CACHE_MAX_AGE_SECONDS):
    hwnd, _thread_id, _pid = foreground_window_info()
    if (
        hwnd
        and _web_input_cache["hwnd"] == int(hwnd)
        and time.monotonic() - _web_input_cache["time"] <= max_age_seconds
    ):
        return _web_input_cache["value"]
    # キャッシュが無い/古い場合はUIAを使わない軽量判定のみ行う。
    return not is_caret_in_browser_chrome()


UIA_REINIT_AFTER_EMPTY_SECONDS = 5.0


def uia_worker_loop():
    empty_url_since = 0.0
    while True:
        try:
            hwnd, _thread_id, _pid = foreground_window_info()
            process = foreground_process_name()
            if hwnd and process in BROWSER_PROCESSES:
                url = browser_current_url()
                now = time.monotonic()
                if url:
                    empty_url_since = 0.0
                elif not empty_url_since:
                    empty_url_since = now
                elif now - empty_url_since >= UIA_REINIT_AFTER_EMPTY_SECONDS:
                    # ブラウザ前面なのにURLが取れない状態が続く場合、
                    # UIAが応答不能になっている可能性があるので作り直す。
                    debug_log(f"uia reinit: url empty streak process={process}")
                    uia_reset()
                    empty_url_since = now
                value = is_web_input_area_active()
                # 別スレッドから読まれるため、判定キーのhwndを最後に書く。
                _web_input_cache["value"] = value
                _web_input_cache["time"] = time.monotonic()
                _web_input_cache["hwnd"] = int(hwnd)
            else:
                empty_url_since = 0.0
        except Exception as exc:
            debug_log(f"uia worker error: {exc!r}")
        time.sleep(UIA_WORKER_INTERVAL_SECONDS)


def start_uia_worker():
    threading.Thread(target=uia_worker_loop, name="uia-worker", daemon=True).start()


def ime_has_composition(hwnd):
    if not hwnd:
        return False
    himc = imm32.ImmGetContext(hwnd)
    if not himc:
        return False
    try:
        for index in (GCS_COMPSTR, GCS_COMPATTR, GCS_COMPCLAUSE):
            length = imm32.ImmGetCompositionStringW(himc, index, None, 0)
            if length not in (IMM_ERROR_NODATA, IMM_ERROR_GENERAL) and length > 0:
                return True
    finally:
        imm32.ImmReleaseContext(hwnd, himc)
    return False


def ime_is_open(hwnd):
    if not hwnd:
        return False
    himc = imm32.ImmGetContext(hwnd)
    if not himc:
        return False
    try:
        return bool(imm32.ImmGetOpenStatus(himc))
    finally:
        imm32.ImmReleaseContext(hwnd, himc)


def default_ime_window_status(hwnd):
    ime_hwnd = imm32.ImmGetDefaultIMEWnd(hwnd)
    if not ime_hwnd:
        return False, 0
    open_status = bool(user32.SendMessageW(ime_hwnd, WM_IME_CONTROL, IMC_GETOPENSTATUS, 0))
    conversion_mode = int(user32.SendMessageW(ime_hwnd, WM_IME_CONTROL, IMC_GETCONVERSIONMODE, 0))
    return open_status, conversion_mode


def ime_is_native_mode(hwnd):
    open_status = ime_is_open(hwnd)
    conversion_mode = 0
    if not open_status:
        open_status, conversion_mode = default_ime_window_status(hwnd)
    else:
        _default_open_status, conversion_mode = default_ime_window_status(hwnd)
    return bool(open_status and (conversion_mode & IME_CMODE_NATIVE))


def is_foreground_ime_open():
    for focus_hwnd in foreground_focus_hwnds():
        default_open_status, _conversion_mode = default_ime_window_status(focus_hwnd)
        if ime_is_open(focus_hwnd) or default_open_status:
            return True
    return False


def is_foreground_ime_native_mode():
    for focus_hwnd in foreground_focus_hwnds():
        if ime_is_native_mode(focus_hwnd):
            return True
    return False


def has_ime_candidate_window(_thread_id, _pid_value):
    found = {"value": False, "class": ""}

    def enum_window(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        window_pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
        class_name = window_class_name(hwnd)
        title = window_text(hwnd)
        lowered = class_name.lower()
        title_lowered = title.lower()
        if (
            "candidate" in lowered
            or ("ime" in lowered and "ui" in lowered)
            or "ime" in title_lowered
            or "candidate" in title_lowered
        ):
            found["value"] = True
            process_name = process_name_from_pid(window_pid)
            found["class"] = f"{class_name} title={title!r} process={process_name}"
            return False
        return True

    callback = EnumWindowsProc(enum_window)
    user32.EnumWindows(callback, 0)
    if found["value"]:
        debug_log(f"ime candidate window class={found['class']}")
    return found["value"]


def cached_has_ime_candidate_window(thread_id, pid_value):
    cache_key = (int(thread_id), int(pid_value))
    now = time.monotonic()
    if (
        _ime_candidate_cache["key"] == cache_key
        and now - _ime_candidate_cache["timestamp"] <= IME_CANDIDATE_CACHE_SECONDS
    ):
        return _ime_candidate_cache["value"]
    value = has_ime_candidate_window(thread_id, pid_value)
    _ime_candidate_cache["key"] = cache_key
    _ime_candidate_cache["timestamp"] = now
    _ime_candidate_cache["value"] = value
    return value


def is_ime_composing():
    hwnd, thread_id, pid = foreground_window_info()
    if not hwnd or not thread_id:
        return False
    for focus_hwnd in foreground_focus_hwnds():
        if ime_has_composition(focus_hwnd):
            debug_log(f"ime composition hwnd={int(focus_hwnd)} class={window_class_name(focus_hwnd)!r}")
            return True
    return cached_has_ime_candidate_window(thread_id, pid.value)



def text_matches(text, keywords):
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def keywords_match(text, keywords, use_regex):
    if not use_regex:
        return text_matches(text, keywords)
    for pattern in keywords:
        compiled = compiled_regex(pattern)
        if compiled and compiled.search(text):
            return True
    return False


def processes_match(process_names, target):
    if not target.processes:
        return False
    if target.processes_regex:
        for pattern in target.processes:
            compiled = compiled_regex(pattern)
            if not compiled:
                continue
            for name in process_names:
                if compiled.fullmatch(name):
                    return True
        return False
    target_processes = {item.lower() for item in target.processes}
    return bool(process_names & target_processes)


OWN_WINDOW_CLASS_PREFIX = "ItsumonoKaigyo"


def detect_target(use_cached_browser_url=False):
    hwnd, _thread_id, _pid = foreground_window_info()
    if window_class_name(hwnd).startswith(OWN_WINDOW_CLASS_PREFIX):
        return None
    process_names = process_names_for_window_tree(hwnd)
    foreground_process = foreground_process_name()
    process = foreground_process or next(iter(process_names), "")
    title = foreground_title()
    browser_url = ""
    if foreground_process in BROWSER_PROCESSES:
        browser_url = browser_cached_url() if use_cached_browser_url else browser_current_url()
        if use_cached_browser_url and not browser_url:
            debug_log(f"browser cached url unavailable process={foreground_process}")
    for target in TARGETS:
        if target.surface == "Web":
            title_matched = keywords_match(title, target.window_title_keywords, target.window_title_keywords_regex)
            url_matched = bool(browser_url) and keywords_match(browser_url, target.url_keywords, target.url_keywords_regex)
            if foreground_process in BROWSER_PROCESSES and (title_matched or url_matched):
                return target
            continue
        process_matched = processes_match(process_names, target)
        title_matched = bool(target.window_title_keywords) and keywords_match(title, target.window_title_keywords, target.window_title_keywords_regex)
        if process_matched or (process not in BROWSER_PROCESSES and title_matched):
            return target
    return None


def mode_status_text(mode):
    if mode == MODE_ENTER:
        return "Enterモード有効"
    if mode == MODE_SHIFT_ENTER:
        return "Shift+Enterモード有効"
    return "オフ"


def mode_status_text_for_language(mode, language):
    if language == LANG_EN:
        if mode == MODE_ENTER:
            return "Enter mode enabled"
        if mode == MODE_SHIFT_ENTER:
            return "Shift+Enter mode enabled"
        return "Off"
    return mode_status_text(mode)


def mode_status_text_for_target(target, mode, language):
    mode = normalize_mode_for_target(target, mode)
    if language == LANG_EN:
        return "On" if mode == MODE_ENTER else "Off"
    return AI_SNS_MODE_LABELS.get(mode, MODE_LABELS.get(mode, mode))



def trigger_matches(mode):
    ctrl = is_key_down(VK_CONTROL)
    alt = is_key_down(VK_MENU)
    shift = is_key_down(VK_SHIFT)
    if ctrl or alt:
        return False
    if mode == MODE_ENTER:
        return not shift
    if mode == MODE_SHIFT_ENTER:
        return shift
    return False


class WrapState:
    """Shiftラップ方式（Shiftを押し込みEnterを素通しする変換）の状態機械。

    Win32やスレッド、実時間に依存しない純粋ロジックとして分離してあり、
    test_itsumono_kaigyo.py から時刻を与えて遷移を検証できる。
    排他制御は呼び出し側（KeyboardHook.wrap_lock）が行う。
    """

    def __init__(self):
        self.active = False
        self.started_at = 0.0
        self.hold_until = 0.0
        self.recent_until = 0.0

    def begin(self, now):
        """ラップ開始。Shift押下が必要なとき（新規開始時）Trueを返す。"""
        first = not self.active
        if first:
            self.active = True
            self.started_at = now
        self.hold_until = now + WRAP_SHIFT_HOLD_SECONDS
        return first

    def extend(self, now):
        """Enter keydown（リピート・再送出）で保持期限を延長する。"""
        if not self.active:
            return
        self.hold_until = now + WRAP_SHIFT_HOLD_SECONDS

    def shorten(self, now, linger_seconds=WRAP_SHIFT_KEYUP_LINGER_SECONDS):
        """Enter keyup後、再送出の残りを拾う最小限まで保持期限を縮める。"""
        if not self.active:
            return
        self.hold_until = min(self.hold_until, now + linger_seconds)

    def remaining(self, now):
        """解放までの残り秒数。0以下なら解放すべき。最大保持時間の上限も考慮する。"""
        if not self.active:
            return 0.0
        deadline = min(self.hold_until, self.started_at + WRAP_SHIFT_MAX_HOLD_SECONDS)
        return deadline - now

    def release(self, now):
        """ラップ解放。Shift解放が必要なとき（実際に解放したとき）Trueを返す。"""
        if not self.active:
            return False
        self.active = False
        self.started_at = 0.0
        self.hold_until = 0.0
        self.recent_until = now + WRAP_RESIDUAL_SHIFT_SECONDS
        return True

    def residual_shift_active(self, now):
        """解放直後の残留Shift（再送出遅延分）を自分のものとして扱う期間か。"""
        return now < self.recent_until


class KeyboardHook:
    def __init__(self, config_provider, event_queue):
        self.config_provider = config_provider
        self.event_queue = event_queue
        self.callback = LowLevelKeyboardProc(self._callback)
        self.hook = None
        self.thread = None
        self.thread_id = None
        self.running = threading.Event()
        self.pending_key = None
        self.pending_action = None
        self.pending_wrap = False
        self.wrap_state = WrapState()
        self.wrap_timer = None
        self.wrap_lock = threading.Lock()
        self.last_ime_input_time = 0.0
        self.suppress_enter_until = 0.0

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.running.set()
        self.thread = threading.Thread(target=self._run, name="keyboard-hook", daemon=True)
        self.thread.start()

    def _run(self):
        self.thread_id = kernel32.GetCurrentThreadId()
        self.hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self.callback, kernel32.GetModuleHandleW(None), 0)
        if not self.hook:
            debug_log("hook_start failed")
            self.event_queue.put(("error", "キーボードフックの開始に失敗しました。"))
            self.thread_id = None
            return
        debug_log("hook_start ok worker_thread")
        msg = wintypes.MSG()
        while self.running.is_set() and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        if self.hook:
            user32.UnhookWindowsHookEx(self.hook)
            self.hook = None
        self.thread_id = None
        debug_log("hook_stop worker_thread")

    def stop(self):
        self.running.clear()
        if self.thread_id:
            user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.5)
        self.thread = None
        self.thread_id = None
        self.pending_key = None
        self.pending_action = None
        self.pending_wrap = False
        self._release_wrap("stop")
        self.last_ime_input_time = 0.0
        self.suppress_enter_until = 0.0

    def _callback(self, n_code, w_param, l_param):
        try:
            return self._callback_impl(n_code, w_param, l_param)
        except Exception as error:
            debug_log(f"hook callback error: {error!r}")
            return user32.CallNextHookEx(self.hook, n_code, w_param, l_param)

    def _callback_impl(self, n_code, w_param, l_param):
        if n_code < 0:
            return user32.CallNextHookEx(self.hook, n_code, w_param, l_param)
        info = ctypes.cast(l_param, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        injected = bool(info.flags & LLKHF_INJECTED)
        own_input = info.dwExtraInfo == SEND_EXTRA_INFO
        if own_input:
            return user32.CallNextHookEx(self.hook, n_code, w_param, l_param)
        if self.wrap_state.active:
            if info.vkCode == VK_RETURN:
                if w_param in (WM_KEYDOWN, WM_SYSKEYDOWN):
                    self._extend_wrap()
                    debug_log(f"enter passthrough: wrap hold injected={injected}")
                else:
                    # keyup後は再送出の残りを拾う最小限だけ保持し、早めにShiftを解放する。
                    self._shorten_wrap(WRAP_SHIFT_KEYUP_LINGER_SECONDS)
                    debug_log(f"enter keyup passthrough: wrap hold injected={injected}")
                return user32.CallNextHookEx(self.hook, n_code, w_param, l_param)
            if (
                w_param in (WM_KEYDOWN, WM_SYSKEYDOWN)
                and info.vkCode not in (VK_SHIFT, VK_CONTROL, VK_MENU)
            ):
                self._release_wrap("other keydown")
        if info.vkCode == VK_RETURN and self.suppress_enter_until > time.monotonic():
            if injected and is_key_down(VK_SHIFT):
                debug_log("enter allow: injected shift-enter during conversion window")
                return user32.CallNextHookEx(self.hook, n_code, w_param, l_param)
            debug_log(f"enter suppressed: conversion window injected={injected}")
            return 1
        if w_param in (WM_KEYDOWN, WM_SYSKEYDOWN):
            self._note_possible_ime_input(info.vkCode)
            if info.vkCode == VK_RETURN:
                debug_log(f"enter keydown seen injected={injected}")
            if self.pending_key == info.vkCode:
                if info.vkCode == VK_RETURN:
                    debug_log("enter keydown suppressed: pending")
                return 1
            if self._should_convert(info.vkCode):
                if self.pending_wrap:
                    self._begin_wrap()
                    debug_log(f"enter wrap: shift held, enter passes injected={injected}")
                    return user32.CallNextHookEx(self.hook, n_code, w_param, l_param)
                if info.vkCode == VK_RETURN:
                    debug_log(f"enter keydown convert action={self.pending_action}")
                self.pending_key = info.vkCode
                return 1
        if w_param in (WM_KEYUP, WM_SYSKEYUP) and self.pending_key == info.vkCode:
            action = self.pending_action
            self.suppress_enter_until = time.monotonic() + ENTER_SUPPRESS_AFTER_CONVERSION_SECONDS
            if info.vkCode == VK_RETURN:
                debug_log(f"enter keyup send action={action}")
            threading.Timer(0.01, self._send_conversion, args=(action, True)).start()
            return 1
        return user32.CallNextHookEx(self.hook, n_code, w_param, l_param)

    def _begin_wrap(self):
        with self.wrap_lock:
            first = self.wrap_state.begin(time.monotonic())
        if first:
            send_key(VK_SHIFT)
            debug_log("wrap shift down")
        self._schedule_wrap_check(WRAP_SHIFT_HOLD_SECONDS)

    def _extend_wrap(self):
        with self.wrap_lock:
            self.wrap_state.extend(time.monotonic())

    def _shorten_wrap(self, linger_seconds):
        with self.wrap_lock:
            self.wrap_state.shorten(time.monotonic(), linger_seconds)
        self._schedule_wrap_check(linger_seconds)

    def _schedule_wrap_check(self, delay):
        with self.wrap_lock:
            if self.wrap_timer:
                self.wrap_timer.cancel()
            timer = threading.Timer(max(delay, 0.01), self._wrap_check)
            timer.daemon = True
            self.wrap_timer = timer
        timer.start()

    def _wrap_check(self):
        with self.wrap_lock:
            if not self.wrap_state.active:
                return
            remaining = self.wrap_state.remaining(time.monotonic())
        if remaining <= 0:
            self._release_wrap("timeout")
        else:
            self._schedule_wrap_check(remaining)

    def _release_wrap(self, reason):
        with self.wrap_lock:
            released = self.wrap_state.release(time.monotonic())
            if released and self.wrap_timer:
                self.wrap_timer.cancel()
                self.wrap_timer = None
        if not released:
            return
        send_key(VK_SHIFT, key_up=True)
        debug_log(f"wrap shift up ({reason})")

    def _note_possible_ime_input(self, vk_code):
        if vk_code in (VK_RETURN, VK_SHIFT, VK_CONTROL, VK_MENU, VK_ESCAPE):
            return
        if is_key_down(VK_CONTROL) or is_key_down(VK_MENU):
            self.last_ime_input_time = 0.0
            debug_log(f"recent text input cleared: shortcut vk={vk_code}")
            return
        if vk_code in (VK_BACK, VK_DELETE):
            self.last_ime_input_time = 0.0
            debug_log(f"recent text input cleared vk={vk_code}")
            return
        if (
            0x30 <= vk_code <= 0x5A
            or vk_code in (VK_SPACE, VK_PROCESSKEY)
            or 0xBA <= vk_code <= 0xE4
        ):
            self.last_ime_input_time = time.monotonic()
            debug_log(f"recent text input vk={vk_code}")

    def _has_recent_ime_input(self):
        if not self.last_ime_input_time:
            return False
        return time.monotonic() - self.last_ime_input_time <= IME_RECENT_INPUT_SECONDS

    def _should_convert(self, vk_code):
        if vk_code != VK_RETURN:
            return False
        config = self.config_provider()
        if not config.get("enabled", True):
            debug_log("enter skip: disabled")
            return False
        target = detect_target(use_cached_browser_url=True)
        if not target:
            debug_log(f"enter skip: no target title={foreground_title()!r} process={foreground_process_name()!r}")
            return False
        if target.surface == "Web" and not is_web_input_area_active_cached():
            debug_log(f"enter skip: web non-input target={target.label}")
            return False
        if is_ime_composing():
            debug_log(f"enter skip: ime composing target={target.label}")
            return False
        if is_foreground_ime_open() and self._has_recent_ime_input():
            self.last_ime_input_time = 0.0
            debug_log(f"enter skip: ime open recent input target={target.label}")
            return False
        process_name = foreground_process_name()
        wrap = process_name in set(process_name_list(config.get("shift_enter_wrap_processes", [])))
        mode = normalize_mode_for_target(target, config["targets"].get(target.key, target.default_mode))
        if mode == MODE_OFF or not trigger_matches(mode):
            residual_shift = (
                mode == MODE_ENTER
                and wrap
                and is_key_down(VK_SHIFT)
                and not is_key_down(VK_CONTROL)
                and not is_key_down(VK_MENU)
                and self.wrap_state.residual_shift_active(time.monotonic())
            )
            if not residual_shift:
                debug_log(f"enter skip: mode/trigger target={target.label} mode={mode} shift={is_key_down(VK_SHIFT)} ctrl={is_key_down(VK_CONTROL)} alt={is_key_down(VK_MENU)}")
                return False
            debug_log(f"enter convert: wrap residual shift target={target.label}")
        if mode == MODE_SHIFT_ENTER and target.action == ACTION_SHIFT_ENTER:
            debug_log(f"enter skip: shift-enter already native target={target.label}")
            return False
        self.pending_action = target.action
        self.pending_wrap = wrap
        debug_log(f"enter convert: target={target.label} mode={mode} action={target.action} process={process_name} wrap={wrap}")
        return True

    def _send_conversion(self, action, clear_pending=True):
        try:
            if action:
                ok = send_line_break(action)
                debug_log(f"send_conversion action={action} ok={ok}")
                if not ok:
                    self.event_queue.put(("error", "改行の送信に失敗しました。"))
        finally:
            if clear_pending:
                self.pending_key = None
                self.pending_action = None
                self.pending_wrap = False


def hiword(value):
    return (int(value) >> 16) & 0xFFFF


def loword(value):
    return int(value) & 0xFFFF


def send_message_text(hwnd, msg, w_param, text):
    buffer = ctypes.create_unicode_buffer(text)
    return user32.SendMessageW(hwnd, msg, w_param, ctypes.cast(buffer, ctypes.c_void_p))


class Win32App:
    def __init__(self, start_minimized=False):
        self.hinstance = kernel32.GetModuleHandleW(None)
        self.config_data = load_config()
        self.events = queue.Queue()
        self.hook = KeyboardHook(lambda: copy.deepcopy(self.config_data), self.events)
        self.paused = not self.config_data.get("enabled", True)
        self.main_proc = WndProcType(self._main_wndproc)
        self.settings_proc = WndProcType(self._settings_wndproc)
        self.custom_edit_proc = WndProcType(self._custom_edit_wndproc)
        self.hwnd = None
        self.settings_hwnd = None
        self.custom_edit_hwnd = None
        self.custom_edit_index = 0
        self.custom_edit_configs = []
        self.custom_edit_controls = {}
        self.settings_category_index = 0
        self.settings_modes = {}
        self.settings_combo_hwnds = {}
        self.settings_check_hwnds = {}
        self.settings_scroll_items = []
        self.settings_scroll_offset = 0
        self.settings_scroll_max = 0
        self.settings_viewport_hwnd = None
        self.settings_scrollbar_hwnd = None
        self.settings_tab_hwnd = None
        self.settings_target_keys = []
        self.controls = {}
        self.settings_controls = {}
        self.settings_button_hovered = False
        self.fonts = {}
        self.tray_icon = None
        self.tray_added = False
        self.start_minimized = start_minimized

    def _language(self):
        return self.config_data.get("language", LANG_JA)

    def _is_english(self):
        return self._language() == LANG_EN

    def _app_title(self):
        return APP_NAME_EN if self._is_english() else APP_NAME

    def _settings_title(self):
        return f"{self._app_title()} - {'Settings' if self._is_english() else '設定'}"

    def _custom_edit_title(self):
        return f"{self._app_title()} - {'Edit Custom' if self._is_english() else 'カスタム編集'}"

    def _custom_edit_label(self, key):
        if self._is_english():
            labels = {
                "target": "Target",
                "label": "Display name",
                "surface": "Type",
                "title_keywords": "Title keywords",
                "processes": "Process names",
                "url_keywords": "URL keywords",
                "title_regex": "Regex",
                "processes_regex": "Regex",
                "url_regex": "Regex",
                "default_mode": "Default mode",
                "save": "Save",
                "close": "Close",
            }
        else:
            labels = {
                "target": "対象",
                "label": "表示名",
                "surface": "種類",
                "title_keywords": "タイトルキーワード",
                "processes": "プロセス名",
                "url_keywords": "URLキーワード",
                "title_regex": "正規表現",
                "processes_regex": "正規表現",
                "url_regex": "正規表現",
                "default_mode": "初期モード",
                "save": "保存",
                "close": "閉じる",
            }
        return labels[key]

    def _category_label(self, category):
        if not self._is_english():
            return category
        labels = {
            "生成AI": "AI",
            "SNS・チャット": "SNS / Chat",
        }
        return labels.get(category, category)

    def _mode_option_label(self, mode, target=None):
        if self._is_english():
            return "On" if mode == MODE_ENTER else "Off"
        return AI_SNS_MODE_LABELS.get(mode, MODE_LABELS.get(mode, mode))


    def _custom_mode_option_label(self, mode):
        return self._mode_option_label(mode)


    def _set_language(self, language):
        if language not in (LANG_JA, LANG_EN) or language == self._language():
            return
        self.config_data["language"] = language
        save_config(self.config_data)
        self._apply_language()
        self._refresh_status()

    def _apply_language(self):
        if not self.hwnd:
            return
        is_en = self._is_english()
        user32.SetWindowTextW(self.hwnd, self._app_title())
        if self.controls.get("title"):
            user32.SetWindowTextW(self.controls["title"], self._app_title())
        if self.controls.get("language"):
            user32.SetWindowTextW(self.controls["language"], "日本語" if is_en else "English")
        if self.controls.get("exit"):
            user32.SetWindowTextW(self.controls["exit"], "Exit" if is_en else "終了")
        if self.controls.get("pause"):
            user32.SetWindowTextW(self.controls["pause"], ("Resume" if self.paused else "Pause") if is_en else ("再開" if self.paused else "一時停止"))
        if self.controls.get("minimize"):
            user32.SetWindowTextW(self.controls["minimize"], "Minimize" if is_en else "最小化")
        if self.controls.get("settings"):
            user32.InvalidateRect(self.controls["settings"], None, True)
        if self.tray_added:
            data = self._tray_data()
            shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(data))
        if self.settings_hwnd:
            self._apply_settings_language()
        if self.custom_edit_hwnd:
            self._apply_custom_edit_language()

    def run(self):
        icc = INITCOMMONCONTROLSEX()
        icc.dwSize = ctypes.sizeof(INITCOMMONCONTROLSEX)
        icc.dwICC = ICC_TAB_CLASSES
        comctl32.InitCommonControlsEx(ctypes.byref(icc))
        self._create_fonts()
        self._register_classes()
        self._create_main_window()
        self._add_tray_icon()
        self.hook.start()
        user32.SetTimer(self.hwnd, STATUS_TIMER_ID, 500, None)
        user32.ShowWindow(self.hwnd, SW_HIDE if self.start_minimized else SW_SHOWNORMAL)
        user32.UpdateWindow(self.hwnd)
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        return 0

    def _create_fonts(self):
        self.fonts["body"] = gdi32.CreateFontW(-16, 0, 0, 0, FW_NORMAL, 0, 0, 0, DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH, "Yu Gothic UI")
        self.fonts["title"] = gdi32.CreateFontW(-20, 0, 0, 0, FW_BOLD, 0, 0, 0, DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH, "Yu Gothic UI")
        self.fonts["bold"] = gdi32.CreateFontW(-16, 0, 0, 0, FW_BOLD, 0, 0, 0, DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH, "Yu Gothic UI")
        self.fonts["settings"] = gdi32.CreateFontW(-17, 0, 0, 0, FW_NORMAL, 0, 0, 0, DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH, "Yu Gothic UI")
        self.fonts["icon"] = gdi32.CreateFontW(-24, 0, 0, 0, FW_NORMAL, 0, 0, 0, DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH, "Segoe MDL2 Assets")

    def _register_classes(self):
        for class_name, proc in (
            ("ItsumonoKaigyoMainWindow", self.main_proc),
            ("ItsumonoKaigyoSettingsWindow", self.settings_proc),
            ("ItsumonoKaigyoCustomEditWindow", self.custom_edit_proc),
        ):
            wc = WNDCLASS()
            wc.lpfnWndProc = proc
            wc.hInstance = self.hinstance
            wc.hbrBackground = COLOR_BTNFACE + 1
            wc.lpszClassName = class_name
            user32.RegisterClassW(ctypes.byref(wc))

    def _create_window(self, class_name, text, style, x, y, w, h, parent=None, control_id=0):
        hwnd = user32.CreateWindowExW(
            0,
            class_name,
            text,
            WS_CHILD | WS_VISIBLE | style if parent else style,
            x,
            y,
            w,
            h,
            parent,
            control_id,
            self.hinstance,
            None,
        )
        if self.fonts.get("body"):
            user32.SendMessageW(hwnd, WM_SETFONT, self.fonts["body"], True)
        return hwnd

    def _create_main_window(self):
        self.hwnd = user32.CreateWindowExW(
            0,
            "ItsumonoKaigyoMainWindow",
            APP_NAME,
            WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
            CW_USEDEFAULT,
            CW_USEDEFAULT,
            430,
            230,
            None,
            None,
            self.hinstance,
            None,
        )
        self.controls["title"] = self._create_window("STATIC", APP_NAME, SS_LEFT, 28, 20, 360, 28, self.hwnd)
        user32.SendMessageW(self.controls["title"], WM_SETFONT, self.fonts["title"], True)
        self.controls["language"] = self._create_window("BUTTON", "English", BS_PUSHBUTTON, 319, 24, 68, 28, self.hwnd, CONTROL_MAIN_LANGUAGE)
        self.controls["status_target"] = self._create_window("STATIC", "ステータス：確認中", SS_LEFT, 28, 68, 350, 24, self.hwnd)
        self.controls["status_mode"] = self._create_window("STATIC", "", SS_LEFT, 28, 94, 250, 24, self.hwnd)
        self.controls["settings"] = self._create_window("BUTTON", "設定", BS_OWNERDRAW | BS_FLAT, 22, 136, 100, 30, self.hwnd, CONTROL_MAIN_SETTINGS)
        self.controls["exit"] = self._create_window("BUTTON", "終了", BS_PUSHBUTTON, 139, 134, 80, 34, self.hwnd, CONTROL_MAIN_EXIT)
        self.controls["pause"] = self._create_window("BUTTON", "一時停止", BS_PUSHBUTTON, 223, 134, 80, 34, self.hwnd, CONTROL_MAIN_PAUSE)
        self.controls["minimize"] = self._create_window("BUTTON", "最小化", BS_PUSHBUTTON, 307, 134, 80, 34, self.hwnd, CONTROL_MAIN_MINIMIZE)
        self._apply_window_icons()
        self._apply_language()
        self._refresh_status()

    def _icon_candidate_paths(self):
        candidates = [app_base_dir() / "app_icon.ico"]
        if getattr(sys, "frozen", False):
            candidates.append(Path(getattr(sys, "_MEIPASS", app_base_dir())) / "app_icon.ico")
        return candidates

    def _load_app_icon(self, cx=0, cy=0):
        flags = LR_LOADFROMFILE | (LR_DEFAULTSIZE if not (cx and cy) else 0)
        for icon_path in self._icon_candidate_paths():
            if icon_path.exists():
                icon = user32.LoadImageW(None, str(icon_path), IMAGE_ICON, cx, cy, flags)
                if icon:
                    return icon
        return user32.LoadIconW(None, ctypes.c_void_p(IDI_APPLICATION))

    def _apply_window_icons(self):
        cx_small = user32.GetSystemMetrics(SM_CXSMICON)
        cy_small = user32.GetSystemMetrics(SM_CYSMICON)
        cx_big = user32.GetSystemMetrics(SM_CXICON)
        cy_big = user32.GetSystemMetrics(SM_CYICON)
        small_icon = self._load_app_icon(cx_small, cy_small)
        big_icon = self._load_app_icon(cx_big, cy_big)
        if small_icon:
            user32.SendMessageW(self.hwnd, WM_SETICON, ICON_SMALL, ctypes.c_void_p(small_icon))
        if big_icon:
            user32.SendMessageW(self.hwnd, WM_SETICON, ICON_BIG, ctypes.c_void_p(big_icon))

    def _tray_data(self):
        data = NOTIFYICONDATA()
        data.cbSize = ctypes.sizeof(NOTIFYICONDATA)
        data.hWnd = self.hwnd
        data.uID = TRAY_UID
        data.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
        data.uCallbackMessage = WM_TRAYICON
        data.hIcon = self.tray_icon or self._load_app_icon()
        data.szTip = self._app_title()[:127]
        return data

    def _add_tray_icon(self):
        self.tray_icon = self._load_app_icon()
        data = self._tray_data()
        if shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(data)):
            data.uVersion = NOTIFYICON_VERSION_4
            shell32.Shell_NotifyIconW(NIM_SETVERSION, ctypes.byref(data))
            self.tray_added = True

    def _remove_tray_icon(self):
        if not self.tray_added:
            return
        data = self._tray_data()
        shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(data))
        self.tray_added = False

    def _show_main_window(self):
        user32.ShowWindow(self.hwnd, SW_SHOWNORMAL)
        user32.SetForegroundWindow(self.hwnd)

    def _open_developer_site(self):
        shell32.ShellExecuteW(self.hwnd, "open", DEVELOPER_URL, None, None, SW_SHOWNORMAL)

    def _show_about(self):
        if self._is_english():
            message = (
                f"{APP_NAME_EN}\n"
                f"Developed by {DEVELOPER_NAME_EN}\n\n"
                f"Version: {APP_VERSION}"
            )
            title = f"{APP_NAME_EN} - About"
        else:
            message = (
                f"{APP_NAME}\n"
                f"Developed by {DEVELOPER_NAME}\n\n"
                f"バージョン: {APP_VERSION}"
            )
            title = f"{APP_NAME} - バージョン情報"
        user32.MessageBoxW(self.hwnd, message, title, MB_OK)

    def _set_startup_from_menu(self, enabled):
        if not set_startup_registered(enabled):
            user32.MessageBoxW(self.hwnd, "Windows起動時の設定を変更できませんでした。", APP_NAME, MB_OK)

    def _draw_rect_border(self, hdc, rect, color):
        pen = gdi32.CreatePen(PS_SOLID, 1, color)
        if not pen:
            return
        old_pen = gdi32.SelectObject(hdc, pen)
        left = rect.left
        top = rect.top
        right = rect.right - 1
        bottom = rect.bottom - 1
        gdi32.MoveToEx(hdc, left, top, None)
        gdi32.LineTo(hdc, right, top)
        gdi32.LineTo(hdc, right, bottom)
        gdi32.LineTo(hdc, left, bottom)
        gdi32.LineTo(hdc, left, top)
        if old_pen:
            gdi32.SelectObject(hdc, old_pen)
        gdi32.DeleteObject(pen)

    def _toggle_pause(self):
        self.paused = not self.paused
        self.config_data["enabled"] = not self.paused
        self._apply_language()
        self._refresh_status()

    def _show_tray_menu(self):
        point = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(point))
        menu = user32.CreatePopupMenu()
        if not menu:
            return
        startup_registered = is_startup_registered()
        is_en = self._is_english()
        user32.AppendMenuW(menu, MF_STRING, TRAY_MENU_OPEN, "Open Dialog" if is_en else "ダイアログを開く")
        pause_label = ("Resume" if self.paused else "Pause") if is_en else ("再開" if self.paused else "一時停止")
        user32.AppendMenuW(menu, MF_STRING | (MF_CHECKED if self.paused else 0), TRAY_MENU_PAUSE, pause_label)
        user32.AppendMenuW(menu, MF_STRING, TRAY_MENU_SETTINGS, "Settings" if is_en else "設定")
        user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(menu, MF_STRING | (MF_GRAYED if startup_registered else 0), TRAY_MENU_STARTUP_ENABLE, "Run at Windows startup" if is_en else "Windows起動時に実行する")
        user32.AppendMenuW(menu, MF_STRING | (MF_GRAYED if not startup_registered else 0), TRAY_MENU_STARTUP_DISABLE, "Remove Windows startup registration" if is_en else "Windows起動時の登録を解除する")
        user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(menu, MF_STRING | (MF_CHECKED if not is_en else 0), TRAY_MENU_LANG_JA, "日本語")
        user32.AppendMenuW(menu, MF_STRING | (MF_CHECKED if is_en else 0), TRAY_MENU_LANG_EN, "English")
        user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(menu, MF_STRING, TRAY_MENU_DEVELOPER_SITE, "Developer Website" if is_en else "開発元Webサイト")
        user32.AppendMenuW(menu, MF_STRING, TRAY_MENU_ABOUT, "About" if is_en else "バージョン情報")
        user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(menu, MF_STRING, TRAY_MENU_EXIT, "Exit" if is_en else "終了")
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
        user32.DestroyMenu(menu)
        if command == TRAY_MENU_OPEN:
            self._show_main_window()
        elif command == TRAY_MENU_PAUSE:
            self._toggle_pause()
        elif command == TRAY_MENU_SETTINGS:
            self._show_main_window()
            self._open_settings()
        elif command == TRAY_MENU_STARTUP_ENABLE:
            self._set_startup_from_menu(True)
        elif command == TRAY_MENU_STARTUP_DISABLE:
            self._set_startup_from_menu(False)
        elif command == TRAY_MENU_LANG_JA:
            self._set_language(LANG_JA)
        elif command == TRAY_MENU_LANG_EN:
            self._set_language(LANG_EN)
        elif command == TRAY_MENU_DEVELOPER_SITE:
            self._open_developer_site()
        elif command == TRAY_MENU_ABOUT:
            self._show_about()
        elif command == TRAY_MENU_EXIT:
            self._quit()

    def _draw_settings_button(self, draw):
        rect = RECT(draw.rcItem.left, draw.rcItem.top, draw.rcItem.right, draw.rcItem.bottom)
        pressed = bool(draw.itemState & ODS_SELECTED)
        hovered = self.settings_button_hovered or bool(draw.itemState & ODS_HOTLIGHT)
        if pressed or hovered:
            brush = gdi32.CreateSolidBrush(0x00DADADA if pressed else 0x00E6E6E6)
            if brush:
                user32.FillRect(draw.hDC, ctypes.byref(rect), brush)
                gdi32.DeleteObject(brush)
            else:
                user32.FillRect(draw.hDC, ctypes.byref(rect), user32.GetSysColorBrush(COLOR_BTNFACE))
            self._draw_rect_border(draw.hDC, rect, 0x009A9A9A if pressed else 0x00B8B8B8)
        else:
            user32.FillRect(draw.hDC, ctypes.byref(rect), user32.GetSysColorBrush(COLOR_BTNFACE))
        offset = 1 if pressed else 0
        gdi32.SetBkMode(draw.hDC, TRANSPARENT)
        gdi32.SetTextColor(draw.hDC, 0)

        icon_rect = RECT(rect.left + 7 + offset, rect.top + offset, rect.left + 36 + offset, rect.bottom + offset)
        old_font = gdi32.SelectObject(draw.hDC, self.fonts["icon"])
        user32.DrawTextW(draw.hDC, "\ue713", -1, ctypes.byref(icon_rect), DT_CENTER | DT_VCENTER | DT_SINGLELINE)

        text_rect = RECT(rect.left + 39 + offset, rect.top + offset, rect.right + offset, rect.bottom + offset)
        gdi32.SelectObject(draw.hDC, self.fonts["settings"])
        user32.DrawTextW(draw.hDC, "Settings" if self._is_english() else "設定", -1, ctypes.byref(text_rect), DT_LEFT | DT_VCENTER | DT_SINGLELINE)
        if old_font:
            gdi32.SelectObject(draw.hDC, old_font)
        return 1

    def _update_settings_button_hover(self, force=None):
        button = self.controls.get("settings")
        if not button:
            return
        hovered = bool(force) if force is not None else False
        if force is None:
            point = wintypes.POINT()
            rect = RECT()
            if user32.GetCursorPos(ctypes.byref(point)) and user32.GetWindowRect(button, ctypes.byref(rect)):
                hovered = rect.left <= point.x < rect.right and rect.top <= point.y < rect.bottom
        if hovered != self.settings_button_hovered:
            self.settings_button_hovered = hovered
            user32.InvalidateRect(button, None, True)

    def _main_wndproc(self, hwnd, msg, w_param, l_param):
        if msg == WM_DRAWITEM:
            draw = ctypes.cast(l_param, ctypes.POINTER(DRAWITEMSTRUCT)).contents
            if draw.CtlID == CONTROL_MAIN_SETTINGS:
                return self._draw_settings_button(draw)
        if msg == WM_SETCURSOR:
            if self.controls.get("settings") and int(w_param) == int(self.controls["settings"]):
                self._update_settings_button_hover(True)
        if msg == WM_COMMAND:
            control_id = loword(w_param)
            if control_id == CONTROL_MAIN_PAUSE:
                self._toggle_pause()
                return 0
            if control_id == CONTROL_MAIN_SETTINGS:
                self._open_settings()
                return 0
            if control_id == CONTROL_MAIN_LANGUAGE:
                self._set_language(LANG_JA if self._is_english() else LANG_EN)
                return 0
            if control_id == CONTROL_MAIN_MINIMIZE:
                user32.ShowWindow(hwnd, SW_HIDE)
                return 0
            if control_id == CONTROL_MAIN_EXIT:
                self._quit()
                return 0
        if msg == WM_TIMER:
            self._poll_events()
            self._update_settings_button_hover()
            self._refresh_status()
            return 0
        if msg == WM_TRAYICON:
            tray_msg = loword(l_param)
            if tray_msg == WM_LBUTTONDBLCLK:
                self._show_main_window()
                return 0
            if tray_msg == WM_RBUTTONUP:
                self._show_tray_menu()
                return 0
        if msg == WM_CLOSE:
            user32.ShowWindow(hwnd, SW_HIDE)
            return 0
        if msg == WM_DESTROY:
            user32.PostQuitMessage(0)
            return 0
        return user32.DefWindowProcW(hwnd, msg, w_param, l_param)

    def _open_settings(self):
        if self.settings_hwnd:
            user32.ShowWindow(self.settings_hwnd, SW_SHOW)
            return
        self.settings_modes = json.loads(json.dumps(self.config_data["targets"]))
        self.settings_hwnd = user32.CreateWindowExW(
            0,
            "ItsumonoKaigyoSettingsWindow",
            self._settings_title(),
            WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU,
            CW_USEDEFAULT,
            CW_USEDEFAULT,
            530,
            642,
            self.hwnd,
            None,
            self.hinstance,
            None,
        )
        self._create_settings_controls()
        user32.EnableWindow(self.hwnd, False)
        user32.ShowWindow(self.settings_hwnd, SW_SHOWNORMAL)
        user32.UpdateWindow(self.settings_hwnd)

    def _create_settings_controls(self):
        hwnd = self.settings_hwnd
        for index, category in enumerate(CATEGORIES):
            tab_style = BS_AUTORADIOBUTTON | BS_PUSHLIKE | WS_TABSTOP | (WS_GROUP if index == 0 else 0)
            tab = self._create_window(
                "BUTTON",
                self._category_label(category),
                tab_style,
                32 + index * 132,
                20,
                122,
                30,
                hwnd,
                CONTROL_SETTINGS_TAB_BASE + index,
            )
            self.settings_controls[f"tab_{index}"] = tab
        self.settings_controls["reset_defaults"] = self._create_window("BUTTON", "Reset Defaults" if self._is_english() else "初期値に戻す", BS_PUSHBUTTON | WS_TABSTOP, 350, 20, 120, 30, hwnd, CONTROL_SETTINGS_RESET_DEFAULTS)
        self.settings_viewport_hwnd = None
        self.settings_scrollbar_hwnd = self._create_window("SCROLLBAR", "", SBS_VERT, 470, 72, 18, 448, hwnd, CONTROL_SETTINGS_SCROLLBAR)
        self._render_settings_list()
        self._update_settings_tabs()
        self.settings_controls["custom_edit"] = self._create_window("BUTTON", "Edit Custom" if self._is_english() else "カスタム編集", BS_PUSHBUTTON | WS_TABSTOP, 32, 550, 116, 30, hwnd, CONTROL_SETTINGS_CUSTOM_EDIT)
        self.settings_controls["save"] = self._create_window("BUTTON", "Save" if self._is_english() else "保存", BS_DEFPUSHBUTTON | WS_TABSTOP, 306, 550, 72, 30, hwnd, CONTROL_SETTINGS_SAVE)
        self.settings_controls["cancel"] = self._create_window("BUTTON", "Cancel" if self._is_english() else "キャンセル", BS_PUSHBUTTON | WS_TABSTOP, 388, 550, 82, 30, hwnd, CONTROL_SETTINGS_CANCEL)
        self._update_custom_edit_button()

    def _apply_settings_language(self):
        if not self.settings_hwnd:
            return
        user32.SetWindowTextW(self.settings_hwnd, self._settings_title())
        for index, category in enumerate(CATEGORIES):
            hwnd = self.settings_controls.get(f"tab_{index}")
            if hwnd:
                user32.SetWindowTextW(hwnd, self._category_label(category))
        updates = {
            "reset_defaults": "Reset Defaults" if self._is_english() else "初期値に戻す",
            "custom_edit": "Edit Custom" if self._is_english() else "カスタム編集",
            "save": "Save" if self._is_english() else "保存",
            "cancel": "Cancel" if self._is_english() else "キャンセル",
        }
        for key, text in updates.items():
            hwnd = self.settings_controls.get(key)
            if hwnd:
                user32.SetWindowTextW(hwnd, text)
        self._render_settings_list()
        self._update_settings_tabs()

    def _update_settings_tabs(self):
        for index in range(len(CATEGORIES)):
            hwnd = self.settings_controls.get(f"tab_{index}")
            if hwnd:
                user32.SendMessageW(hwnd, BM_SETCHECK, BST_CHECKED if index == self.settings_category_index else 0, 0)
        self._update_custom_edit_button()

    def _current_settings_category(self):
        if 0 <= self.settings_category_index < len(CATEGORIES):
            return CATEGORIES[self.settings_category_index]
        return ""

    def _update_custom_edit_button(self):
        hwnd = self.settings_controls.get("custom_edit")
        if not hwnd:
            return
        user32.ShowWindow(hwnd, SW_SHOW)

    def _render_settings_list(self):
        for control in self.settings_scroll_items:
            user32.DestroyWindow(control["hwnd"])
        self.settings_scroll_items = []
        self.settings_check_hwnds = {}
        self.settings_target_keys = []
        base_x = 20
        base_y = 72
        y = 10
        row_index = 0
        category = CATEGORIES[self.settings_category_index]
        for target in [item for item in TARGETS if item.category == category]:
            self.settings_target_keys.append(target.key)
            label_width = 260
            label_hwnd = self._create_window("STATIC", target.label, SS_LEFT | SS_CENTERIMAGE, base_x + 22, base_y + y, label_width, 24, self.settings_hwnd)
            self.settings_scroll_items.append({"hwnd": label_hwnd, "x": 22, "y": y, "w": label_width, "h": 24})
            self.settings_check_hwnds[target.key] = {}
            current_mode = normalize_mode_for_target(target, self.settings_modes.get(target.key, target.default_mode))
            self.settings_modes[target.key] = current_mode
            mode_options = mode_options_for_target(target)
            option_x = [310, 388] if mode_options == AI_SNS_MODE_ORDER else [170, 334, 548]
            option_w = [64, 64] if mode_options == AI_SNS_MODE_ORDER else [160, 206, 58]
            for mode_index, mode in enumerate(mode_options):
                x = option_x[mode_index]
                w = option_w[mode_index]
                radio_id = CONTROL_SETTINGS_CHECK_BASE + row_index * 3 + mode_index
                radio = self._create_window("BUTTON", self._mode_option_label(mode, target), BS_RADIOBUTTON | WS_TABSTOP, base_x + x, base_y + y, w, 24, self.settings_hwnd, radio_id)
                user32.SendMessageW(radio, BM_SETCHECK, BST_CHECKED if mode == current_mode else 0, 0)
                self.settings_check_hwnds[target.key][mode] = radio
                self.settings_scroll_items.append({"hwnd": radio, "x": x, "y": y, "w": w, "h": 24})
            y += 28
            row_index += 1
        self.settings_scroll_offset = 0
        self.settings_scroll_max = max(0, y - 448)
        user32.SetScrollRange(self.settings_scrollbar_hwnd, SB_CTL, 0, self.settings_scroll_max, True)
        user32.SetScrollPos(self.settings_scrollbar_hwnd, SB_CTL, 0, True)
        user32.ShowWindow(self.settings_scrollbar_hwnd, SW_SHOW if self.settings_scroll_max > 0 else SW_HIDE)
        self.settings_scroll_offset = -1
        self._set_settings_scroll(0)

    def _set_settings_scroll(self, offset):
        offset = max(0, min(self.settings_scroll_max, offset))
        if offset == self.settings_scroll_offset:
            return
        self.settings_scroll_offset = offset
        user32.SetScrollPos(self.settings_scrollbar_hwnd, SB_CTL, offset, True)
        base_x = 20
        base_y = 72
        view_top = base_y
        view_bottom = base_y + 448
        for item in self.settings_scroll_items:
            y = base_y + item["y"] - offset
            visible = y >= view_top and y + item["h"] <= view_bottom
            user32.SetWindowPos(
                item["hwnd"],
                None,
                base_x + item["x"],
                y,
                item["w"],
                item["h"],
                SWP_NOZORDER | SWP_NOACTIVATE,
            )
            user32.ShowWindow(item["hwnd"], SW_SHOW if visible else SW_HIDE)

    def _mode_from_checkbox_id(self, control_id):
        raw = control_id - CONTROL_SETTINGS_CHECK_BASE
        if raw < 0:
            return None, None
        row_index = raw // 3
        mode_index = raw % 3
        if row_index >= len(self.settings_target_keys):
            return None, None
        target_key = self.settings_target_keys[row_index]
        target = next((item for item in TARGETS if item.key == target_key), None)
        if not target:
            return None, None
        mode_options = mode_options_for_target(target)
        if mode_index >= len(mode_options):
            return None, None
        return target_key, mode_options[mode_index]

    def _select_settings_mode(self, target_key, selected_mode):
        if not target_key or not selected_mode:
            return
        self.settings_modes[target_key] = selected_mode
        for mode, hwnd in self.settings_check_hwnds.get(target_key, {}).items():
            user32.SendMessageW(hwnd, BM_SETCHECK, BST_CHECKED if mode == selected_mode else 0, 0)

    def _store_visible_settings_modes(self):
        for target_key, modes in self.settings_check_hwnds.items():
            for mode, hwnd in modes.items():
                if user32.SendMessageW(hwnd, BM_GETCHECK, 0, 0) == BST_CHECKED:
                    self.settings_modes[target_key] = mode
                    break

    def _custom_target_configs(self):
        definitions = self.config_data.get("target_definitions", [])
        result = []
        category = self._current_settings_category()
        if isinstance(definitions, list):
            for item in definitions:
                if (
                    isinstance(item, dict)
                    and str(item.get("key", "")).startswith(("gai_custom_", "sns_custom_"))
                    and item.get("category") == category
                ):
                    result.append(json.loads(json.dumps(item)))
        return result

    def _custom_edit_mode_options(self):
        return mode_options_for_category(self._current_settings_category())

    def _open_custom_edit(self):
        if self.custom_edit_hwnd:
            user32.ShowWindow(self.custom_edit_hwnd, SW_SHOW)
            return
        self.custom_edit_configs = self._custom_target_configs()
        if not self.custom_edit_configs:
            message = "No custom entries for this category were found in ItsumonoKaigyoForChat_settings.json." if self._is_english() else "この種類のカスタム枠が ItsumonoKaigyoForChat_settings.json に見つかりません。"
            user32.MessageBoxW(self.settings_hwnd, message, self._app_title(), MB_OK)
            return
        self.custom_edit_index = 0
        self.custom_edit_controls = {}
        self.custom_edit_hwnd = user32.CreateWindowExW(
            0,
            "ItsumonoKaigyoCustomEditWindow",
            self._custom_edit_title(),
            WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU,
            CW_USEDEFAULT,
            CW_USEDEFAULT,
            560,
            540,
            self.settings_hwnd,
            None,
            self.hinstance,
            None,
        )
        self._create_custom_edit_controls()
        user32.EnableWindow(self.settings_hwnd, False)
        user32.ShowWindow(self.custom_edit_hwnd, SW_SHOWNORMAL)
        user32.UpdateWindow(self.custom_edit_hwnd)

    def _create_custom_edit_controls(self):
        hwnd = self.custom_edit_hwnd
        labels = {}
        self.custom_edit_controls["labels"] = labels
        labels["target"] = self._create_window("STATIC", self._custom_edit_label("target"), SS_LEFT | SS_CENTERIMAGE, 24, 22, 120, 24, hwnd)
        select = self._create_window("COMBOBOX", "", CBS_DROPDOWNLIST | CBS_HASSTRINGS | WS_TABSTOP, 160, 22, 330, 180, hwnd, CONTROL_CUSTOM_TARGET_SELECT)
        for item in self.custom_edit_configs:
            send_message_text(select, CB_ADDSTRING, 0, f"{item.get('key', '')} - {item.get('label', '')}")
        user32.SendMessageW(select, CB_SETCURSEL, self.custom_edit_index, 0)
        self.custom_edit_controls["select"] = select

        y = 68
        labels["label"] = self._create_window("STATIC", self._custom_edit_label("label"), SS_LEFT | SS_CENTERIMAGE, 24, y, 130, 24, hwnd)
        self.custom_edit_controls["label"] = self._create_window("EDIT", "", WS_BORDER | ES_AUTOHSCROLL | WS_TABSTOP, 160, y - 2, 330, 28, hwnd, CONTROL_CUSTOM_LABEL)
        y += 46

        labels["surface"] = self._create_window("STATIC", self._custom_edit_label("surface"), SS_LEFT | SS_CENTERIMAGE, 24, y, 130, 24, hwnd)
        surface = self._create_window("COMBOBOX", "", CBS_DROPDOWNLIST | CBS_HASSTRINGS | WS_TABSTOP, 160, y, 160, 120, hwnd, CONTROL_CUSTOM_SURFACE)
        for value in ("Web", "App"):
            send_message_text(surface, CB_ADDSTRING, 0, value)
        self.custom_edit_controls["surface"] = surface
        y += 42

        labels["title_keywords"] = self._create_window("STATIC", self._custom_edit_label("title_keywords"), SS_LEFT | SS_CENTERIMAGE, 24, y, 130, 24, hwnd)
        self.custom_edit_controls["window_title_keywords"] = []
        for index in range(3):
            edit = self._create_window("EDIT", "", WS_BORDER | ES_AUTOHSCROLL | WS_TABSTOP, 160, y + index * 32 - 2, 330, 28, hwnd, CONTROL_CUSTOM_TITLE_KEYWORDS + index)
            self.custom_edit_controls["window_title_keywords"].append(edit)
        title_regex = self._create_window("BUTTON", self._custom_edit_label("title_regex"), BS_AUTOCHECKBOX | WS_TABSTOP, 24, y + 32, 120, 24, hwnd, CONTROL_CUSTOM_TITLE_REGEX)
        labels["title_regex"] = title_regex
        self.custom_edit_controls["window_title_keywords_regex"] = title_regex
        y += 104

        self.custom_edit_controls["processes_label"] = self._create_window("STATIC", self._custom_edit_label("processes"), SS_LEFT | SS_CENTERIMAGE, 24, y, 130, 24, hwnd)
        labels["processes"] = self.custom_edit_controls["processes_label"]
        self.custom_edit_controls["processes"] = []
        self.custom_edit_controls["url_keywords_label"] = self._create_window("STATIC", self._custom_edit_label("url_keywords"), SS_LEFT | SS_CENTERIMAGE, 24, y, 130, 24, hwnd)
        labels["url_keywords"] = self.custom_edit_controls["url_keywords_label"]
        self.custom_edit_controls["url_keywords"] = []
        for index in range(3):
            process_edit = self._create_window("EDIT", "", WS_BORDER | ES_AUTOHSCROLL | WS_TABSTOP, 160, y + index * 32 - 2, 330, 28, hwnd, CONTROL_CUSTOM_PROCESSES + index)
            url_edit = self._create_window("EDIT", "", WS_BORDER | ES_AUTOHSCROLL | WS_TABSTOP, 160, y + index * 32 - 2, 330, 28, hwnd, CONTROL_CUSTOM_URL_KEYWORDS + index)
            self.custom_edit_controls["processes"].append(process_edit)
            self.custom_edit_controls["url_keywords"].append(url_edit)
        processes_regex = self._create_window("BUTTON", self._custom_edit_label("processes_regex"), BS_AUTOCHECKBOX | WS_TABSTOP, 24, y + 32, 120, 24, hwnd, CONTROL_CUSTOM_PROCESSES_REGEX)
        labels["processes_regex"] = processes_regex
        self.custom_edit_controls["processes_regex"] = processes_regex
        url_regex = self._create_window("BUTTON", self._custom_edit_label("url_regex"), BS_AUTOCHECKBOX | WS_TABSTOP, 24, y + 32, 120, 24, hwnd, CONTROL_CUSTOM_URL_REGEX)
        labels["url_regex"] = url_regex
        self.custom_edit_controls["url_keywords_regex"] = url_regex
        y += 104

        labels["default_mode"] = self._create_window("STATIC", self._custom_edit_label("default_mode"), SS_LEFT | SS_CENTERIMAGE, 24, y, 130, 24, hwnd)
        default_mode = self._create_window("COMBOBOX", "", CBS_DROPDOWNLIST | CBS_HASSTRINGS | WS_TABSTOP, 160, y, 160, 120, hwnd, CONTROL_CUSTOM_DEFAULT_MODE)
        for mode in self._custom_edit_mode_options():
            send_message_text(default_mode, CB_ADDSTRING, 0, self._custom_mode_option_label(mode))
        self.custom_edit_controls["default_mode"] = default_mode

        self.custom_edit_controls["save"] = self._create_window("BUTTON", self._custom_edit_label("save"), BS_DEFPUSHBUTTON | WS_TABSTOP, 348, 446, 72, 30, hwnd, CONTROL_CUSTOM_SAVE)
        self.custom_edit_controls["cancel"] = self._create_window("BUTTON", self._custom_edit_label("close"), BS_PUSHBUTTON | WS_TABSTOP, 430, 446, 72, 30, hwnd, CONTROL_CUSTOM_CANCEL)
        self._load_custom_edit_form()

    def _apply_custom_edit_language(self):
        if not self.custom_edit_hwnd:
            return
        user32.SetWindowTextW(self.custom_edit_hwnd, self._custom_edit_title())
        labels = self.custom_edit_controls.get("labels", {})
        if isinstance(labels, dict):
            for key, hwnd in labels.items():
                if hwnd:
                    user32.SetWindowTextW(hwnd, self._custom_edit_label(key))
        if self.custom_edit_controls.get("save"):
            user32.SetWindowTextW(self.custom_edit_controls["save"], self._custom_edit_label("save"))
        if self.custom_edit_controls.get("cancel"):
            user32.SetWindowTextW(self.custom_edit_controls["cancel"], self._custom_edit_label("close"))

        default_mode = self.custom_edit_controls.get("default_mode")
        if default_mode:
            selected = int(user32.SendMessageW(default_mode, CB_GETCURSEL, 0, 0))
            options = self._custom_edit_mode_options()
            user32.SendMessageW(default_mode, CB_RESETCONTENT, 0, 0)
            for mode in options:
                send_message_text(default_mode, CB_ADDSTRING, 0, self._custom_mode_option_label(mode))
            if selected < 0 or selected >= len(options):
                selected = 0
            user32.SendMessageW(default_mode, CB_SETCURSEL, selected, 0)

    def _update_custom_edit_fields(self):
        surface = self._combo_value(self.custom_edit_controls["surface"], ["Web", "App"])
        web_visible = surface == "Web"
        for name, visible in (("processes", not web_visible), ("url_keywords", web_visible)):
            controls = self.custom_edit_controls.get(name, [])
            if not isinstance(controls, list):
                controls = [controls]
            extras = [
                self.custom_edit_controls.get(f"{name}_label"),
                self.custom_edit_controls.get(f"{name}_regex"),
            ]
            for hwnd in controls + extras:
                if hwnd:
                    user32.ShowWindow(hwnd, SW_SHOW if visible else SW_HIDE)

    def _set_list_fields(self, name, values):
        values = list(string_tuple(values))
        for index, hwnd in enumerate(self.custom_edit_controls.get(name, [])):
            user32.SetWindowTextW(hwnd, values[index] if index < len(values) else "")

    def _get_list_fields(self, name):
        result = []
        for hwnd in self.custom_edit_controls.get(name, []):
            text = window_text(hwnd).strip()
            if text:
                result.append(text)
        return result

    def _set_check(self, hwnd, checked):
        if hwnd:
            user32.SendMessageW(hwnd, BM_SETCHECK, BST_CHECKED if checked else 0, 0)

    def _get_check(self, hwnd):
        if not hwnd:
            return False
        return int(user32.SendMessageW(hwnd, BM_GETCHECK, 0, 0)) == BST_CHECKED

    def _combo_select_value(self, hwnd, values, value):
        try:
            index = values.index(value)
        except ValueError:
            index = 0
        user32.SendMessageW(hwnd, CB_SETCURSEL, index, 0)

    def _combo_value(self, hwnd, values):
        index = int(user32.SendMessageW(hwnd, CB_GETCURSEL, 0, 0))
        if 0 <= index < len(values):
            return values[index]
        return values[0]

    def _load_custom_edit_form(self):
        if not self.custom_edit_configs:
            return
        item = self.custom_edit_configs[self.custom_edit_index]
        user32.SetWindowTextW(self.custom_edit_controls["label"], str(item.get("label", "")))
        self._set_list_fields("processes", item.get("processes", []))
        self._set_list_fields("window_title_keywords", item.get("window_title_keywords", []))
        self._set_list_fields("url_keywords", item.get("url_keywords", []))
        self._set_check(self.custom_edit_controls.get("processes_regex"), bool(item.get("processes_regex", False)))
        self._set_check(self.custom_edit_controls.get("window_title_keywords_regex"), bool(item.get("window_title_keywords_regex", False)))
        self._set_check(self.custom_edit_controls.get("url_keywords_regex"), bool(item.get("url_keywords_regex", False)))
        self._combo_select_value(self.custom_edit_controls["surface"], ["Web", "App"], str(item.get("surface", "Web")))
        mode_options = self._custom_edit_mode_options()
        mode = internal_mode_from_config_values(str(item.get("action", ACTION_SHIFT_ENTER)), item.get("default_mode", MODE_OFF))
        if mode not in mode_options:
            mode = MODE_OFF
        self._combo_select_value(self.custom_edit_controls["default_mode"], mode_options, mode)
        self._update_custom_edit_fields()

    def _store_custom_edit_form(self):
        if not self.custom_edit_configs:
            return
        item = self.custom_edit_configs[self.custom_edit_index]
        item["label"] = window_text(self.custom_edit_controls["label"]).strip() or item.get("key", "")
        item["surface"] = self._combo_value(self.custom_edit_controls["surface"], ["Web", "App"])
        item["action"] = ACTION_SHIFT_ENTER
        item["window_title_keywords"] = self._get_list_fields("window_title_keywords")
        item["window_title_keywords_regex"] = self._get_check(self.custom_edit_controls.get("window_title_keywords_regex"))
        if item["surface"] == "Web":
            item["url_keywords"] = self._get_list_fields("url_keywords")
            item["url_keywords_regex"] = self._get_check(self.custom_edit_controls.get("url_keywords_regex"))
            item.pop("processes", None)
            item.pop("processes_regex", None)
        else:
            item["processes"] = self._get_list_fields("processes")
            item["processes_regex"] = self._get_check(self.custom_edit_controls.get("processes_regex"))
            item.pop("url_keywords", None)
            item.pop("url_keywords_regex", None)
        item["default_mode"] = self._combo_value(self.custom_edit_controls["default_mode"], self._custom_edit_mode_options())

    def _invalid_custom_regex(self):
        for item in self.custom_edit_configs:
            if not isinstance(item, dict):
                continue
            for field, flag in REGEX_FLAG_FIELDS:
                if not item.get(flag):
                    continue
                for pattern in string_tuple(item.get(field, ())):
                    error = regex_error_text(pattern)
                    if error:
                        return item, field, pattern, error
        return None

    def _save_custom_edit(self):
        self._store_custom_edit_form()
        invalid = self._invalid_custom_regex()
        if invalid:
            item, field, pattern, error = invalid
            if self._is_english():
                message = f"Invalid regular expression in {item.get('key', '')} ({field}):\n{pattern}\n{error}"
            else:
                message = f"{item.get('key', '')} の {field} に不正な正規表現があります。\n{pattern}\n{error}"
            user32.MessageBoxW(self.custom_edit_hwnd, message, self._app_title(), MB_OK)
            return False
        definitions = self.config_data.get("target_definitions", [])
        if not isinstance(definitions, list):
            definitions = []
        custom_by_key = {item.get("key"): item for item in self.custom_edit_configs if isinstance(item, dict)}
        new_definitions = []
        seen = set()
        for item in definitions:
            key = item.get("key") if isinstance(item, dict) else None
            if key in custom_by_key:
                new_definitions.append(custom_by_key[key])
                seen.add(key)
            else:
                new_definitions.append(item)
        for item in self.custom_edit_configs:
            key = item.get("key")
            if key not in seen:
                new_definitions.append(item)
        self.config_data["target_definitions"] = new_definitions
        for item in self.custom_edit_configs:
            key = item.get("key")
            mode = item.get("default_mode", MODE_OFF)
            if key and mode in MODE_ORDER:
                self.config_data.setdefault("targets", {})[key] = mode
                self.settings_modes[key] = mode
        save_config(self.config_data)
        self.config_data = load_config()
        self.settings_modes = json.loads(json.dumps(self.config_data["targets"]))
        self._render_settings_list()
        self._update_settings_tabs()
        return True

    def _reset_settings_defaults(self):
        result = user32.MessageBoxW(self.settings_hwnd, "各対象の選択を初期モードに戻します。よろしいですか？", APP_NAME, MB_OKCANCEL)
        if result != IDOK:
            return
        self._close_custom_edit()
        self._store_visible_settings_modes()
        self.settings_modes = {target.key: normalize_mode_for_target(target, target.default_mode) for target in TARGETS}
        self._render_settings_list()
        self._update_settings_tabs()

    def _close_custom_edit(self):
        if self.custom_edit_hwnd:
            user32.DestroyWindow(self.custom_edit_hwnd)

    def _settings_wndproc(self, hwnd, msg, w_param, l_param):
        if msg == WM_COMMAND:
            control_id = loword(w_param)
            if CONTROL_SETTINGS_TAB_BASE <= control_id < CONTROL_SETTINGS_TAB_BASE + len(CATEGORIES):
                selected = control_id - CONTROL_SETTINGS_TAB_BASE
                if selected != self.settings_category_index:
                    self._store_visible_settings_modes()
                    self.settings_category_index = selected
                    self._render_settings_list()
                    self._update_settings_tabs()
                return 0
            if CONTROL_SETTINGS_CHECK_BASE <= control_id < CONTROL_SETTINGS_CHECK_BASE + len(TARGETS) * 3:
                target_key, mode = self._mode_from_checkbox_id(control_id)
                self._select_settings_mode(target_key, mode)
                return 0
            if control_id == CONTROL_SETTINGS_CUSTOM_EDIT:
                self._store_visible_settings_modes()
                self._open_custom_edit()
                return 0
            if control_id == CONTROL_SETTINGS_RESET_DEFAULTS:
                self._reset_settings_defaults()
                return 0
            if control_id == CONTROL_SETTINGS_SAVE:
                self._store_visible_settings_modes()
                for target in TARGETS:
                    self.settings_modes[target.key] = normalize_mode_for_target(target, self.settings_modes.get(target.key, target.default_mode))
                self.config_data["targets"].update(self.settings_modes)
                save_config(self.config_data)
                self._close_settings()
                self._refresh_status()
                return 0
            if control_id == CONTROL_SETTINGS_CANCEL:
                self._close_settings()
                return 0
        if msg == WM_CLOSE:
            self._close_settings()
            return 0
        if msg == WM_VSCROLL:
            code = loword(w_param)
            thumb = hiword(w_param)
            if code == SB_LINEUP:
                self._set_settings_scroll(self.settings_scroll_offset - 28)
            elif code == SB_LINEDOWN:
                self._set_settings_scroll(self.settings_scroll_offset + 28)
            elif code == SB_PAGEUP:
                self._set_settings_scroll(self.settings_scroll_offset - 280)
            elif code == SB_PAGEDOWN:
                self._set_settings_scroll(self.settings_scroll_offset + 280)
            elif code in (SB_THUMBPOSITION, SB_THUMBTRACK):
                self._set_settings_scroll(thumb)
            return 0
        if msg == WM_MOUSEWHEEL:
            delta = hiword(w_param)
            if delta >= 0x8000:
                delta -= 0x10000
            self._set_settings_scroll(self.settings_scroll_offset - (84 if delta > 0 else -84))
            return 0
        return user32.DefWindowProcW(hwnd, msg, w_param, l_param)

    def _custom_edit_wndproc(self, hwnd, msg, w_param, l_param):
        if msg == WM_COMMAND:
            control_id = loword(w_param)
            code = hiword(w_param)
            if control_id == CONTROL_CUSTOM_TARGET_SELECT and code == CBN_SELCHANGE:
                self._store_custom_edit_form()
                selected = int(user32.SendMessageW(self.custom_edit_controls["select"], CB_GETCURSEL, 0, 0))
                if 0 <= selected < len(self.custom_edit_configs):
                    self.custom_edit_index = selected
                    self._load_custom_edit_form()
                return 0
            if control_id == CONTROL_CUSTOM_SURFACE and code == CBN_SELCHANGE:
                self._update_custom_edit_fields()
                return 0
            if control_id == CONTROL_CUSTOM_SAVE:
                if self._save_custom_edit():
                    self._close_custom_edit()
                return 0
            if control_id == CONTROL_CUSTOM_CANCEL:
                self._close_custom_edit()
                return 0
        if msg == WM_CLOSE:
            self._close_custom_edit()
            return 0
        if msg == WM_DESTROY:
            if self.custom_edit_hwnd == hwnd:
                self.custom_edit_hwnd = None
                self.custom_edit_controls = {}
                self.custom_edit_configs = []
                user32.EnableWindow(self.settings_hwnd, True)
                user32.SetForegroundWindow(self.settings_hwnd)
            return 0
        return user32.DefWindowProcW(hwnd, msg, w_param, l_param)

    def _close_settings(self):
        if not self.settings_hwnd:
            return
        self._close_custom_edit()
        hwnd = self.settings_hwnd
        self.settings_hwnd = None
        self.settings_controls = {}
        self.settings_combo_hwnds = {}
        self.settings_check_hwnds = {}
        self.settings_scroll_items = []
        self.settings_viewport_hwnd = None
        self.settings_scrollbar_hwnd = None
        self.settings_tab_hwnd = None
        self.settings_scroll_offset = 0
        self.settings_scroll_max = 0
        self.settings_target_keys = []
        user32.EnableWindow(self.hwnd, True)
        user32.DestroyWindow(hwnd)

    def _poll_events(self):
        while True:
            try:
                event, message = self.events.get_nowait()
            except queue.Empty:
                break
            if event == "error":
                if message == "error_hook_start":
                    message = "キーボードフックの開始に失敗しました。"
                elif message == "error_send_break":
                    message = "改行の送信に失敗しました。"
                user32.MessageBoxW(self.hwnd, message, APP_NAME, 0)

    def _refresh_status(self):
        is_en = self._is_english()
        if self.paused or not self.config_data.get("enabled", True):
            user32.SetWindowTextW(self.controls["status_target"], "Active: Paused" if is_en else "アクティブ: 一時停止中")
            user32.SetWindowTextW(self.controls["status_mode"], "Status: Off" if is_en else "ステータス: オフ")
            return
        target = detect_target(use_cached_browser_url=True)
        if not target:
            user32.SetWindowTextW(self.controls["status_target"], "Active: No target" if is_en else "アクティブ: 対象外")
            user32.SetWindowTextW(self.controls["status_mode"], "")
            return
        if target.surface == "Web" and not is_web_input_area_active_cached():
            user32.SetWindowTextW(self.controls["status_target"], "Active: No target" if is_en else "アクティブ: 対象外")
            user32.SetWindowTextW(self.controls["status_mode"], "")
            return
        mode = normalize_mode_for_target(target, self.config_data["targets"].get(target.key, target.default_mode))
        user32.SetWindowTextW(self.controls["status_target"], f"{'Active' if is_en else 'アクティブ'}: {target.label}")
        user32.SetWindowTextW(self.controls["status_mode"], f"{'Status' if is_en else 'ステータス'}: {mode_status_text_for_target(target, mode, self._language())}")

    def _quit(self):
        user32.KillTimer(self.hwnd, STATUS_TIMER_ID)
        self.hook.stop()
        self._remove_tray_icon()
        if self.settings_hwnd:
            self._close_settings()
        user32.DestroyWindow(self.hwnd)


def main():
    if sys.platform != "win32":
        print("This app only runs on Windows.")
        return 1
    mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if not mutex:
        return 1
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        user32.MessageBoxW(None, "すでに起動しています。", APP_NAME, 0)
        kernel32.CloseHandle(mutex)
        return 0
    try:
        start_uia_worker()
        app = Win32App(start_minimized=START_MINIMIZED_ARG in sys.argv[1:])
        return app.run()
    finally:
        kernel32.CloseHandle(mutex)


if __name__ == "__main__":
    raise SystemExit(main())
