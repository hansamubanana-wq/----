"""
テンプレート画像キャプチャツール

使い方:
  python capture_tool.py

スクリーンショットを表示して、マウスでドラッグした領域を
テンプレート画像として templates/ に保存します。
"""
import cv2
import os
import numpy as np
import adb_controller as adb
import config

drawing = False
start_x, start_y = -1, -1
end_x, end_y = -1, -1
current_img = None
display_img = None
scale = 1.0


def mouse_callback(event, x, y, flags, param):
    global drawing, start_x, start_y, end_x, end_y, display_img, current_img

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_x, start_y = x, y
        end_x, end_y = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_x, end_y = x, y
            display_img = current_img.copy()
            cv2.rectangle(display_img, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_x, end_y = x, y
        display_img = current_img.copy()
        cv2.rectangle(display_img, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)


def run():
    global current_img, display_img, scale

    print("=" * 50)
    print("テンプレートキャプチャツール")
    print("=" * 50)

    if not adb.check_connection():
        print("デバイス未接続")
        return

    print("\nスクリーンショットを取得中...")
    path = adb.screenshot()
    img = cv2.imread(path)
    if img is None:
        print("スクリーンショット取得失敗")
        return

    # 画面に収まるようにリサイズ
    screen_h, screen_w = img.shape[:2]
    max_h = 900
    if screen_h > max_h:
        scale = max_h / screen_h
        display_w = int(screen_w * scale)
        display_h = max_h
        current_img = cv2.resize(img, (display_w, display_h))
    else:
        scale = 1.0
        current_img = img.copy()

    display_img = current_img.copy()

    window_name = "テンプレートキャプチャ (ドラッグで範囲選択)"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)

    print("\n操作方法:")
    print("  ドラッグ: 保存したい領域を選択")
    print("  S キー : 選択領域を保存")
    print("  R キー : スクリーンショットを再取得")
    print("  Q キー : 終了")
    print("\n保存済みテンプレート一覧:", _list_templates())

    while True:
        cv2.imshow(window_name, display_img)
        key = cv2.waitKey(30) & 0xFF

        if key == ord('q') or key == 27:  # Q or ESC
            break

        elif key == ord('s'):  # S = Save
            if start_x == end_x or start_y == end_y:
                print("範囲を選択してから S を押してください")
                continue

            # 実際の座標に変換
            x1 = int(min(start_x, end_x) / scale)
            y1 = int(min(start_y, end_y) / scale)
            x2 = int(max(start_x, end_x) / scale)
            y2 = int(max(start_y, end_y) / scale)

            region = img[y1:y2, x1:x2]

            # 名前入力（コンソールで）
            cv2.destroyAllWindows()
            print(f"\n選択範囲: ({x1},{y1}) - ({x2},{y2})")
            print("保存するテンプレート名を入力 (例: btn_start): ", end="")
            name = input().strip()
            if name:
                save_path = os.path.join(config.TEMPLATES_DIR, f"{name}.png")
                cv2.imwrite(save_path, region)
                print(f"保存しました: {save_path}")

            # ウィンドウ再表示
            cv2.namedWindow(window_name)
            cv2.setMouseCallback(window_name, mouse_callback)
            print("\n保存済みテンプレート一覧:", _list_templates())

        elif key == ord('r'):  # R = Refresh screenshot
            print("スクリーンショットを再取得中...")
            path = adb.screenshot()
            img = cv2.imread(path)
            if scale != 1.0:
                h, w = img.shape[:2]
                current_img = cv2.resize(img, (int(w * scale), int(h * scale)))
            else:
                current_img = img.copy()
            display_img = current_img.copy()
            print("更新しました")

    cv2.destroyAllWindows()
    print("\n終了しました")
    print("保存済みテンプレート:", _list_templates())


def _list_templates():
    if not os.path.exists(config.TEMPLATES_DIR):
        return []
    return [f for f in os.listdir(config.TEMPLATES_DIR) if f.endswith(".png")]


if __name__ == "__main__":
    run()
