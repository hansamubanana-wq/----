"""
プロ野球スピリッツA - 自動化ボット

【使い方】
1. ゲームを起動し、対象モードの開始画面まで手動で進める
   - 試練: 初級/中級/上級 が並ぶ画面
   - Vロード: 「自動試合開始」ボタンが見える画面
2. python bot.py を実行
3. モードを選択
4. Ctrl+C で停止
"""
import time
import sys
import adb_controller as adb
import screen
import config

# 難易度を順番に回す（試練モード用）
DIFFICULTIES = ["btn_shokyu", "btn_chukyu", "btn_jokyu"]
DIFF_LABELS  = {"btn_shokyu": "初級", "btn_chukyu": "中級", "btn_jokyu": "上級"}


def wait(sec):
    time.sleep(sec)


def tap_center():
    adb.tap(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)


def safe_tap():
    """TAP SCREEN を消すための安全タップ（画面上部の何もない場所）"""
    adb.tap(config.SCREEN_WIDTH // 2, 300)


# ===================================================
# 共通フェーズ
# ===================================================

def phase_start_battle():
    """自動試合開始ボタンをタップ"""
    print("[1] 自動試合開始")
    if not screen.tap_template("btn_auto_start", timeout=15):
        print("    → ボタンが見つかりません。手動でタップしてください")
        input("    → 試合開始したら Enter: ")
    wait(config.LOADING_WAIT)


# ===================================================
# 試練 フェーズ
# ===================================================

def phase_select_difficulty(template_name):
    """難易度ボタン（初級/中級/上級）をタップ"""
    label = DIFF_LABELS.get(template_name, template_name)
    print(f"[0] 難易度選択: {label}")
    if not screen.tap_template(template_name, timeout=10):
        print(f"    → {label}ボタンが見つかりません。手動でタップしてください")
        input("    → タップしたら Enter: ")
    wait(config.LOADING_WAIT)


def phase_wait_and_advance_shiruren():
    """試練: 試合終了 〜 難易度選択画面に戻るまでを一括処理"""
    print("[2] 試合終了 & 結果画面を処理中...")
    deadline = time.time() + 300

    while time.time() < deadline:
        img = screen.capture()

        # 難易度選択画面に戻ったら完了
        for diff in DIFFICULTIES:
            if screen.find_template(img, diff):
                print("    → 難易度選択画面に戻りました")
                return

        # スタミナ不足 → 80回復 → OK
        pos = screen.find_template(img, "btn_recover_80")
        if pos:
            print("    [!] スタミナ不足 → 80回復")
            adb.tap(pos[0], pos[1])
            wait(0.8)
            img2 = screen.capture()
            pos2 = screen.find_template(img2, "btn_ok")
            if pos2:
                adb.tap(pos2[0], pos2[1])
            else:
                tap_center()
            wait(config.LOADING_WAIT)
            continue

        # TAP SCREEN が見えたらタップして消す
        if screen.find_template(img, "screen_tap"):
            print("    TAP SCREEN → タップ")
            tap_center()
            wait(0.4)
            continue

        # 次へボタン
        pos = screen.find_template(img, "btn_next")
        if pos:
            print("    次へ → タップ")
            adb.tap(pos[0], pos[1])
            wait(0.4)
            continue

        wait(0.5)

    print("    タイムアウト。手動で難易度選択画面まで戻してください")
    input("    準備できたら Enter: ")


# ===================================================
# Vロード フェーズ
# ===================================================

def phase_wait_and_advance_vroad():
    """Vロード: 試合終了 〜 自動試合開始画面に戻るまでを一括処理"""
    print("[2] 試合終了 & 結果画面を処理中...")
    deadline = time.time() + 300
    last_action = time.time()
    IDLE_TIMEOUT = 5  # 何も反応しない秒数でタップ

    while time.time() < deadline:
        img = screen.capture()

        # 自動試合開始画面に戻ったら完了
        if screen.find_template(img, "btn_auto_start"):
            print("    → 自動試合開始画面に戻りました")
            return

        # スタミナ不足 → 80回復 → OK
        pos = screen.find_template(img, "btn_recover_80")
        if pos:
            print("    [!] スタミナ不足 → 80回復")
            adb.tap(pos[0], pos[1])
            wait(0.8)
            img2 = screen.capture()
            pos2 = screen.find_template(img2, "btn_ok")
            if pos2:
                adb.tap(pos2[0], pos2[1])
            else:
                tap_center()
            wait(config.LOADING_WAIT)
            last_action = time.time()
            continue

        # TAP SCREEN が見えたらタップして消す
        if screen.find_template(img, "screen_tap"):
            print("    TAP SCREEN → タップ")
            tap_center()
            wait(0.4)
            last_action = time.time()
            continue

        # ラウンド結果画面（ROUND〇RESULT）→ 1秒間隔で3回タップ
        if screen.find_template(img, "screen_round_result"):
            print("    ROUND RESULT → 3回タップ")
            for i in range(3):
                tap_center()
                wait(1.0)
            last_action = time.time()
            continue

        # 次の試合へ（btn_nextより先に確認）
        pos = screen.find_template(img, "btn_next_match")
        if pos:
            print("    次の試合へ → タップ")
            adb.tap(pos[0], pos[1])
            wait(0.4)
            last_action = time.time()
            continue

        # Vロード用 次へ（btn_nextより先に確認）
        pos = screen.find_template(img, "btn_next_vroad")
        if pos:
            print("    次へ(Vロード) → タップ")
            adb.tap(pos[0], pos[1])
            wait(0.4)
            last_action = time.time()
            continue

        # 通常の次へ
        pos = screen.find_template(img, "btn_next")
        if pos:
            print("    次へ → タップ")
            adb.tap(pos[0], pos[1])
            wait(0.4)
            last_action = time.time()
            continue

        # 何も検出できない時間が続いたらアイドルタップ
        if time.time() - last_action >= IDLE_TIMEOUT:
            print("    [アイドル] 何も検出されず → タップ")
            safe_tap()
            last_action = time.time()

        wait(0.5)

    print("    タイムアウト。手動で自動試合開始画面まで戻してください")
    input("    準備できたら Enter: ")


# ===================================================
# メインループ（試練）
# ===================================================

def run_shiruren():
    print("=" * 50)
    print("プロスピA 試練 自動化ボット（無限ループ）")
    print("=" * 50)
    print()

    print("【準備】試練の種類を選んで 初級/中級/上級 が並ぶ画面まで進めてください")
    input("準備できたら Enter: ")
    print()

    total = 0
    diff_index = 0

    try:
        while True:
            diff = DIFFICULTIES[diff_index % 3]
            label = DIFF_LABELS[diff]
            total += 1
            print(f"\n{'='*50}")
            print(f"[{total}周目] {label}")
            print(f"{'='*50}")

            phase_select_difficulty(diff)
            phase_start_battle()
            phase_wait_and_advance_shiruren()

            diff_index += 1

    except KeyboardInterrupt:
        print(f"\n\n停止しました（完了: {total}周）")


# ===================================================
# メインループ（Vロード）
# ===================================================

def run_vroad():
    print("=" * 50)
    print("プロスピA Vロード 自動化ボット（無限ループ）")
    print("=" * 50)
    print()

    # 必要なテンプレートの確認
    import os
    missing = []
    for tpl in ["btn_next_match", "btn_next_vroad", "screen_round_result"]:
        path = os.path.join(config.TEMPLATES_DIR, f"{tpl}.png")
        if not os.path.exists(path):
            missing.append(tpl)
    if missing:
        print("[!] 以下のテンプレート画像が未登録です:")
        for m in missing:
            print(f"    - {m}.png")
        print("    capture_tool.py で登録してから再実行してください")
        sys.exit(1)

    print("【準備】Vロードの「自動試合開始」ボタンが見える画面まで進めてください")
    input("準備できたら Enter: ")
    print()

    total = 0

    try:
        while True:
            total += 1
            print(f"\n{'='*50}")
            print(f"[{total}周目]")
            print(f"{'='*50}")

            phase_start_battle()
            phase_wait_and_advance_vroad()

    except KeyboardInterrupt:
        print(f"\n\n停止しました（完了: {total}周）")


# ===================================================
# エントリポイント
# ===================================================

def run():
    if not adb.check_connection():
        print("デバイスが接続されていません")
        sys.exit(1)

    print("=" * 50)
    print("プロスピA 自動化ボット")
    print("=" * 50)
    print()
    print("モードを選択してください:")
    print("  1. 試練")
    print("  2. Vロード")
    print()

    while True:
        choice = input("番号を入力 (1 or 2): ").strip()
        if choice == "1":
            run_shiruren()
            break
        elif choice == "2":
            run_vroad()
            break
        else:
            print("1 か 2 を入力してください")


if __name__ == "__main__":
    run()
