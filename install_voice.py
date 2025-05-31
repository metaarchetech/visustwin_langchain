"""
語音功能安裝腳本
自動安裝語音互動所需的依賴
"""

import subprocess
import sys
import platform
import os

def run_command(command, description):
    """執行系統命令"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失敗: {e}")
        print(f"錯誤輸出: {e.stderr}")
        return False

def install_voice_dependencies():
    """安裝語音功能依賴"""
    print("🎤 開始安裝語音互動功能依賴...")
    
    # 基礎語音庫
    dependencies = [
        ("pip install SpeechRecognition", "安裝語音識別庫"),
        ("pip install pyttsx3", "安裝文字轉語音引擎"),
    ]
    
    # 根據作業系統安裝 PyAudio
    system = platform.system().lower()
    
    if system == "windows":
        dependencies.append(("pip install pyaudio", "安裝音頻處理庫 (Windows)"))
    elif system == "darwin":  # macOS
        print("🍎 macOS 系統檢測到")
        print("請先安裝 PortAudio:")
        print("  brew install portaudio")
        dependencies.append(("pip install pyaudio", "安裝音頻處理庫 (macOS)"))
    else:  # Linux
        print("🐧 Linux 系統檢測到")
        print("請先安裝系統依賴:")
        print("  sudo apt-get install portaudio19-dev python3-pyaudio")
        print("  或")
        print("  sudo yum install portaudio-devel python3-pyaudio")
        dependencies.append(("pip install pyaudio", "安裝音頻處理庫 (Linux)"))
    
    # 執行安裝
    success_count = 0
    for command, description in dependencies:
        if run_command(command, description):
            success_count += 1
    
    print(f"\n📊 安裝結果: {success_count}/{len(dependencies)} 成功")
    
    if success_count == len(dependencies):
        print("🎉 語音功能依賴安裝完成！")
        print("\n🚀 您現在可以使用以下功能:")
        print("  • 語音輸入查詢")
        print("  • AI 語音回覆")
        print("  • 語音指令控制")
        return True
    else:
        print("⚠️ 部分依賴安裝失敗，可能需要手動處理")
        return False

def test_voice_functionality():
    """測試語音功能"""
    print("\n🧪 測試語音功能...")
    
    # 測試語音識別
    try:
        import speech_recognition as sr
        print("✅ 語音識別庫載入成功")
    except ImportError as e:
        print(f"❌ 語音識別庫載入失敗: {e}")
        return False
    
    # 測試文字轉語音
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("✅ 文字轉語音引擎初始化成功")
    except Exception as e:
        print(f"❌ 文字轉語音引擎初始化失敗: {e}")
        return False
    
    # 測試音頻功能
    try:
        import pyaudio
        print("✅ 音頻處理庫載入成功")
    except ImportError as e:
        print(f"❌ 音頻處理庫載入失敗: {e}")
        return False
    
    print("🎉 所有語音功能測試通過！")
    return True

def main():
    """主函數"""
    print("=" * 60)
    print("🎤 Omniverse 語音互動功能安裝程式")
    print("=" * 60)
    
    # 檢查 Python 版本
    if sys.version_info < (3, 8):
        print("❌ 需要 Python 3.8 或更高版本")
        sys.exit(1)
    
    print(f"✅ Python 版本: {sys.version}")
    print(f"✅ 作業系統: {platform.system()} {platform.release()}")
    
    # 安裝依賴
    if install_voice_dependencies():
        # 測試功能
        if test_voice_functionality():
            print("\n🎊 語音功能安裝和測試完成！")
            print("\n📋 下一步:")
            print("  1. 重新啟動 Streamlit 應用")
            print("  2. 進入「語音互動」標籤頁")
            print("  3. 點擊「語音設定」檢查狀態")
            print("  4. 開始使用語音功能！")
        else:
            print("\n⚠️ 語音功能測試失敗，請檢查安裝")
    else:
        print("\n❌ 語音功能安裝失敗")
        print("\n🔧 手動安裝指令:")
        print("  pip install SpeechRecognition pyttsx3 pyaudio")

if __name__ == "__main__":
    main() 