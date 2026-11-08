from machine import Pin, mem32
import time

# ===== ピン設定 =====
red = Pin(15, Pin.OUT)
yellow = Pin(14, Pin.OUT)
green = Pin(13, Pin.OUT)
buzzer = Pin(17, Pin.OUT)
PIR_PIN = 16
pir = Pin(PIR_PIN, Pin.IN, Pin.PULL_DOWN)

# ===== 動作の設定 =====
HOLD_MS = 10000  # 最後の検知から赤を保つ時間（10秒）
WARN_MS = 3000   # 消える前に黄色にする時間（残り3秒）

# ===== RP2350-E9対策 =====
PAD = 0x40038000 + 0x04 + PIR_PIN * 4
IE = 1 << 6
SET, CLR = 0x2000, 0x3000
mem32[PAD + CLR] = IE

def read_pir():
    mem32[PAD + SET] = IE
    v = pir.value()
    mem32[PAD + CLR] = IE
    return v

def lights(r, y, g):
    red.value(r)
    yellow.value(y)
    green.value(g)

def beep(times):
    for _ in range(times):
        buzzer.on()
        time.sleep(0.08)
        buzzer.off()
        time.sleep(0.08)

def log(msg):
    print(time.ticks_ms() // 1000, "秒:", msg)

# ===== 起動：センサーの安定待ち（黄色点滅） =====
log("起動中…30秒待ちます")
for _ in range(30):
    lights(0, 1, 0)
    time.sleep(0.5)
    lights(0, 0, 0)
    time.sleep(0.5)
beep(1)
log("監視開始")

alarm = False
last_seen = 0

while True:
    now = time.ticks_ms()
    if read_pir():
        last_seen = now
        if not alarm:
            alarm = True
            log("侵入者を検知！")
            lights(1, 0, 0)
            beep(3)

    if alarm:
        elapsed = time.ticks_diff(now, last_seen)
        if elapsed > HOLD_MS:
            alarm = False
            log("解除（待機に戻る）")
        elif elapsed > HOLD_MS - WARN_MS:
            lights(0, 1, 0)  # もうすぐ解除
        else:
            lights(1, 0, 0)
    else:
        lights(0, 0, 1)

    time.sleep(0.1)