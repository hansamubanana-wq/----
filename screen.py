"""スクリーンショット取得・画像認識"""
import os
import cv2
import numpy as np
import config
import adb_controller as adb


def capture():
    """スクリーンショットを撮影して numpy 配列で返す（ファイル経由なし・高速）"""
    data = adb.screenshot_bytes()
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError("スクリーンショットの取得失敗")
    return img


def find_template(screen_img, template_name, threshold=None):
    """
    テンプレート画像をスクリーン上で探す。
    見つかった場合は中心座標 (x, y) を返す。見つからなければ None。

    template_name: templates/ フォルダ内のファイル名（拡張子なし）
    """
    if threshold is None:
        threshold = config.MATCH_THRESHOLD

    template_path = os.path.join(config.TEMPLATES_DIR, f"{template_name}.png")
    if not os.path.exists(template_path):
        return None

    template = cv2.imread(template_path)
    if template is None:
        return None

    # グレースケールでマッチング（色の影響を除く）
    screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template_gray.shape
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        print(f"  [FOUND] {template_name} at ({center_x}, {center_y}), score={max_val:.3f}")
        return (center_x, center_y)

    return None


def wait_for_template(template_name, timeout=30, interval=1.0, threshold=None):
    """
    指定テンプレートが画面に現れるまで待つ。
    見つかったら座標を返す。タイムアウトしたら None。
    """
    import time
    print(f"  [{template_name}] を待機中...")
    elapsed = 0
    while elapsed < timeout:
        screen = capture()
        pos = find_template(screen, template_name, threshold)
        if pos:
            return pos
        time.sleep(interval)
        elapsed += interval
    print(f"  [{template_name}] タイムアウト ({timeout}秒)")
    return None


def tap_template(template_name, timeout=30, threshold=None):
    """
    テンプレートを見つけてタップ。
    成功したら True、失敗したら False。
    """
    pos = wait_for_template(template_name, timeout=timeout, threshold=threshold)
    if pos:
        adb.tap(pos[0], pos[1])
        return True
    return False


def is_visible(template_name, threshold=None):
    """テンプレートが現在の画面に表示されているか確認"""
    screen = capture()
    pos = find_template(screen, template_name, threshold)
    return pos is not None


def save_region(screen_img, x, y, w, h, save_name):
    """
    スクリーンの指定領域を切り出してテンプレートとして保存。
    capture_tool.py から呼ばれる。
    """
    region = screen_img[y:y+h, x:x+w]
    save_path = os.path.join(config.TEMPLATES_DIR, f"{save_name}.png")
    cv2.imwrite(save_path, region)
    print(f"  テンプレート保存: {save_path}")
    return save_path
