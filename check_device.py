"""
デバイス接続確認スクリプト
まずこれを実行して動作確認してください。
"""
import adb_controller as adb

print("=== デバイス接続確認 ===")
print()
adb.devices()
print()

if adb.check_connection():
    w, h = adb.get_screen_size()
    print(f"画面サイズ: {w} x {h}")
    print()
    print("スクリーンショットを取得中...")
    path = adb.screenshot("test_screenshot.png")
    print(f"保存先: {path}")
    print()
    print("成功！ test_screenshot.png を確認してください")
    print("次は: python capture_tool.py を実行してテンプレート作成")
else:
    print()
    print("トラブルシューティング:")
    print("  [USB接続の場合]")
    print("    - 設定 → 開発者向けオプション → USB デバッグ ON")
    print("    - スマホに「このPCを許可しますか？」が出たら「許可」")
    print()
    print("  [Wi-Fi接続の場合]")
    print("    - スマホとPCが同じWi-Fiに接続")
    print("    - スマホの設定 → 開発者向けオプション → ワイヤレスデバッグ ON")
    print("    - IPアドレスを確認して config.py の DEVICE_SERIAL に設定")
    print("    - コマンド: adb connect <IP>:5555")
