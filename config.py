# ===== 設定ファイル =====

# ADB の場所（scrcpy フォルダ内のものを使用）
ADB_PATH = r"C:\Users\Soichi\Downloads\scrcpy-win64-v3.3.4\scrcpy-win64-v3.3.4\adb.exe"

# デバイス（複数台接続時は adb devices で確認して指定。1台なら None でOK）
DEVICE_SERIAL = None  # 例: "192.168.1.5:5555" や "R3CN90XXXXX"

# スクショ保存先（一時ファイル）
SCREENSHOT_PATH = "screenshot.png"

# テンプレート画像フォルダ
TEMPLATES_DIR = "templates"

# ===== 試練 自動化 設定 =====

# 繰り返し回数（0 = 無限ループ）
REPEAT_COUNT = 0  # 0 = 無限ループ

# 各操作後の待機時間（秒）
TAP_DELAY = 0.1         # タップ後の待機
BATTLE_WAIT = 1.0       # バトル開始後の待機
RESULT_WAIT = 0.5       # 結果画面の待機
LOADING_WAIT = 0.5      # ローディング待機

# テンプレートマッチング の閾値（0.0〜1.0、高いほど厳密）
MATCH_THRESHOLD = 0.80

# ===== 解像度設定 =====
# Pixel 8a のデフォルト解像度: 1080x2400
# scrcpy で確認できます
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 2400
