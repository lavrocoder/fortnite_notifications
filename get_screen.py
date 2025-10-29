import ctypes
import win32con
import win32gui
from ctypes import windll
from struct import pack, calcsize

from PIL import Image

user32, gdi32 = windll.user32, windll.gdi32
PW_RENDERFULLCONTENT = 2


def get_all_window_titles_with_hwnd():
    """
    Получает список пар (HWND, Заголовок) для всех активных окон верхнего уровня.
    """
    results = []

    def enum_handler(hwnd, results):
        """
        Функция обратного вызова для EnumWindows.
        """
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            # Добавляем только окна с непустым заголовком
            if title:
                results.append((hwnd, title))

    # Запускаем перечисление окон
    win32gui.EnumWindows(enum_handler, results)

    return results


def get_hwnd_by_name(name):
    window_info = get_all_window_titles_with_hwnd()
    for hwnd, title in window_info:
        if title.strip() == name.strip():
            return hwnd
    return None


def getWindowBMAP(hwnd, returnImage=False):
    # get Window size and crop pos/size
    L, T, R, B = win32gui.GetWindowRect(hwnd);
    W, H = R - L, B - T
    x, y, w, h = (8, 8, W - 16, H - 16) if user32.IsZoomed(hwnd) else (7, 0, W - 14, H - 7)

    # create dc's and bmp's
    dc = user32.GetWindowDC(hwnd)
    dc1, dc2 = gdi32.CreateCompatibleDC(dc), gdi32.CreateCompatibleDC(dc)
    bmp1, bmp2 = gdi32.CreateCompatibleBitmap(dc, W, H), gdi32.CreateCompatibleBitmap(dc, w, h)

    # render dc1 and dc2 (bmp1 and bmp2) (uncropped and cropped)
    obj1, obj2 = gdi32.SelectObject(dc1, bmp1), gdi32.SelectObject(dc2, bmp2)  # select bmp's into dc's
    user32.PrintWindow(hwnd, dc1, PW_RENDERFULLCONTENT)  # render window to dc1
    gdi32.BitBlt(dc2, 0, 0, w, h, dc1, x, y, win32con.SRCCOPY)  # copy dc1 (x,y,w,h) to dc2 (0,0,w,h)
    gdi32.SelectObject(dc1, obj1);
    gdi32.SelectObject(dc2, obj2)  # restore dc's default obj's

    if returnImage:  # create Image from bmp2
        data = ctypes.create_string_buffer((w * 4) * h)
        bmi = ctypes.c_buffer(pack("IiiHHIIiiII", calcsize("IiiHHIIiiII"), w, -h, 1, 32, 0, 0, 0, 0, 0, 0))
        gdi32.GetDIBits(dc2, bmp2, 0, h, ctypes.byref(data), ctypes.byref(bmi), win32con.DIB_RGB_COLORS)
        img = Image.frombuffer('RGB', (w, h), data, 'raw', 'BGRX')

    # clean up
    gdi32.DeleteObject(bmp1)  # delete bmp1 (uncropped)
    gdi32.DeleteDC(dc1)
    gdi32.DeleteDC(dc2)  # delete created dc's
    user32.ReleaseDC(hwnd, dc)  # release retrieved dc

    return (bmp2, w, h, img) if returnImage else (bmp2, w, h)


def getSnapshot(hwnd):  # get Window HBITMAP as Image
    hbmp, w, h, img = getWindowBMAP(hwnd, True)
    gdi32.DeleteObject(hbmp)
    return img

def get_screen(name, path=None) -> Image.Image | None:
    hwnd = get_hwnd_by_name(name)
    if hwnd is None:
        return None
    img = getSnapshot(hwnd)
    if path:
        img.save(path)
    return img

if __name__ == '__main__':
    get_screen('Fortnite', "screen.png")
