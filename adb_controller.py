"""ADB 操作ラッパー"""
import subprocess
import time
import config


def _adb(*args, binary=False):
    """ADB コマンドを実行して結果を返す"""
    cmd = [config.ADB_PATH]
    if config.DEVICE_SERIAL:
        cmd += ["-s", config.DEVICE_SERIAL]
    cmd += list(args)
    if binary:
        result = subprocess.run(cmd, capture_output=True)
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
    return result


def devices():
    """接続デバイス一覧を表示"""
    result = _adb("devices")
    print(result.stdout)
    return result.stdout


def screenshot_bytes():
    """スクリーンショットをバイト列で直接取得（高速）"""
    result = _adb("exec-out", "screencap", "-p", binary=True)
    return result.stdout


def screenshot(save_path=None):
    """スクリーンショットを取得して保存（capture_tool用）"""
    if save_path is None:
        save_path = config.SCREENSHOT_PATH
    data = screenshot_bytes()
    with open(save_path, "wb") as f:
        f.write(data)
    return save_path


def tap(x, y):
    """座標をタップ"""
    _adb("shell", "input", "tap", str(x), str(y))
    time.sleep(config.TAP_DELAY)


def swipe(x1, y1, x2, y2, duration_ms=300):
    """スワイプ"""
    _adb("shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms))
    time.sleep(config.TAP_DELAY)


def key_event(keycode):
    """キーイベント送信（例: 4=BACK, 3=HOME）"""
    _adb("shell", "input", "keyevent", str(keycode))
    time.sleep(config.TAP_DELAY)


def back():
    """バックボタン"""
    key_event(4)


def home():
    """ホームボタン"""
    key_event(3)


def launch_prospi():
    """プロスピAを起動"""
    _adb("shell", "monkey", "-p", "jp.konami.BaseballSpiritsA", "1")
    time.sleep(3.0)


def get_screen_size():
    """実際のスクリーンサイズを取得"""
    result = _adb("shell", "wm", "size")
    # 例: "Physical size: 1080x2400"
    line = result.stdout.strip()
    if ":" in line:
        size_str = line.split(":")[1].strip()
        w, h = size_str.split("x")
        return int(w), int(h)
    return config.SCREEN_WIDTH, config.SCREEN_HEIGHT


def check_connection():
    """ADB 接続確認"""
    result = _adb("get-state")
    connected = "device" in result.stdout
    if connected:
        print("[OK] デバイス接続済み")
    else:
        print("[NG] デバイスが見つかりません")
        print("     USB デバッグが有効か確認してください")
        print("     または: adb connect <IPアドレス> でWi-Fi接続")
    return connected
