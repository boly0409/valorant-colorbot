import cv2
from mss import mss
import numpy as np
import win32api
import serial
import time
import os

# === 설정 ===
XOR_KEY = 119
USE_DEADPIXEL = True

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    print("="*50)
    print("🔥 Aim Assist by Ddochi")
    print("="*50)

def get_user_config():
    port = input("▶ 아두이노 포트 (예: COM6): ").strip().upper()
    fov = int(input("▶ FOV 크기 (예: 150): "))
    xspd = float(input("▶ X 속도 (기본 0.1): ") or 0.1)
    yspd = float(input("▶ Y 속도 (기본 0.1): ") or 0.1)
    return port, fov, xspd, yspd

def init_serial(port):
    try:
        arduino = serial.Serial(port, 115200)
        time.sleep(2)
        print(f"[✓] 포트 {port} 연결됨.")
        return arduino
    except:
        print(f"[X] 포트 {port} 연결 실패. 확인 후 다시 시도하세요.")
        exit()

def send_movement(arduino, dx, dy):
    dx = int(dx)
    dy = int(dy)

    if dx < 0:
        dx += 256
    if dy < 0:
        dy += 256

    dx ^= XOR_KEY
    dy ^= XOR_KEY

    command = f"m{dx},{dy}\n"
    arduino.write(command.encode())

def main_loop(arduino, fov, xspd, yspd):
    sct = mss()
    monitor = sct.monitors[1]
    monitor['left'] = int((monitor['width'] / 2) - (fov / 2))
    monitor['top'] = int((monitor['height'] / 2) - (fov / 2))
    monitor['width'] = fov
    monitor['height'] = fov
    center_x = fov / 2  # float 중심
    center_y = fov / 2

    lower = np.array([140, 111, 160])
    upper = np.array([148, 154, 194])

    print("\n[INFO] 왼쪽 Alt 키로 자동 조준 활성화됨.\n")

    while True:
        if win32api.GetAsyncKeyState(0xA4) < 0:
            img = np.array(sct.grab(monitor))
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower, upper)

            if np.any(mask):
                ys, xs = np.where(mask != 0)

                # 거리 우선순위 계산 (정밀 중심 사용)
                distances = (xs - center_x) ** 2 + (ys - center_y) ** 2
                priority = distances + ys * 128 # 필요 시 가중치 조절 가능
                best_idx = np.argmin(priority)
                target_x = xs[best_idx]
                target_y = ys[best_idx]

                dx = (target_x - center_x) * xspd
                dy = (target_y - center_y) * yspd

                if USE_DEADPIXEL and abs(dx) < 2 and abs(dy) < 2:
                    dx = 0
                    dy = 0

                send_movement(arduino, dx, dy - 1.2)  # 머리 보정값 (필요시 조정)


# === 실행 ===
if __name__ == "__main__":
    clear_console()
    banner()
    port, fov, xspd, yspd = get_user_config()
    arduino = init_serial(port)
    main_loop(arduino, fov, xspd, yspd)
