# D-Vision Smart Glasses - Hardware Build Guide

Complete step-by-step guide to build DIY full-lens OLED smart glasses for dementia assistance.

**Budget:** ~$220-250  
**Difficulty:** Intermediate  
**Build Time:** 8-12 hours

---

## 📦 Parts List

### 1. Displays (~$95)

| Part | Quantity | Price | Link |
|------|----------|-------|------|
| 0.39" Micro-OLED 1920x1080 (LS039Y8SX01 or similar) | 2 | $35 each | [AliExpress](https://www.aliexpress.com/w/wholesale-LS039Y8SX01.html) |
| HDMI-to-MIPI Driver Board (dual channel) | 1 | $25 | Usually bundled with OLEDs |

> [!TIP]
> Search for "VR OLED display module" or "dual micro OLED HDMI" - many sellers bundle the driver board.

### 2. Optics (~$15)

| Part | Quantity | Price | Notes |
|------|----------|-------|-------|
| Fresnel Lens 50mm diameter, f=50mm | 2 | $4 each | [Amazon](https://www.amazon.com/dp/B07D7ZQVXJ) |
| Black foam eye cups | 2 | $5 | Light blocking around eyes |

### 3. Compute (~$55)

| Part | Price | Link |
|------|-------|------|
| Raspberry Pi Zero 2 W | $15 | [Official Reseller](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/) |
| Pi Camera Module 3 Wide (120° FOV) | $35 | [Amazon](https://www.amazon.com/dp/B0BYGS8HQ7) |
| Mini HDMI to HDMI adapter | $5 | [Amazon](https://www.amazon.com/dp/B00B2HORKE) |

### 4. Audio (~$25)

| Part | Price | Link |
|------|-------|------|
| I2S MEMS Microphone (SPH0645) | $8 | [Adafruit](https://www.adafruit.com/product/3421) |
| Bone Conduction Transducer | $15 | [Amazon](https://www.amazon.com/dp/B09TPFGS9M) |

### 5. Power (~$35)

| Part | Price | Link |
|------|-------|------|
| 3.7V 3000mAh LiPo Battery | $12 | [Amazon](https://www.amazon.com/dp/B08T6QSXJV) |
| Adafruit PowerBoost 1000C | $20 | [Adafruit](https://www.adafruit.com/product/2465) |
| USB-C breakout board (optional) | $3 | For charging |

### 6. Frame & Mounting (~$25)

| Part | Price | Notes |
|------|-------|-------|
| 3D printed frame | $15 | Or free if you own a printer |
| M2 screws assortment | $5 | For mounting components |
| Velcro straps / elastic headband | $5 | Secure fit |

---

## 🔧 Tools Required

- Soldering iron + solder
- Heat shrink tubing
- Wire strippers
- Small Phillips screwdriver
- Multimeter (for testing)
- 3D printer (or order prints from JLCPCB/Shapeways)
- Hot glue gun

---

## 📐 Step-by-Step Build

### Phase 1: Test Components (1-2 hours)

#### Step 1.1: Test Pi Zero 2 W

1. Flash Raspberry Pi OS Lite (64-bit) to microSD card
2. Enable SSH and configure WiFi in `wpa_supplicant.conf`
3. Boot Pi and SSH in
4. Run system update:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

#### Step 1.2: Test Camera

1. Connect Pi Camera via ribbon cable
2. Enable camera interface:
   ```bash
   sudo raspi-config
   # Interface Options → Camera → Enable
   ```
3. Test camera:
   ```bash
   libcamera-hello --timeout 5000
   ```

#### Step 1.3: Test OLED Displays

1. Connect HDMI-to-MIPI driver board to Pi via mini HDMI
2. Power the driver board (usually 5V from Pi or separate)
3. Connect both OLEDs to driver board
4. Boot Pi - displays should mirror desktop

> [!IMPORTANT]
> If displays don't work, check driver board documentation for correct resolution settings in `/boot/config.txt`.

---

### Phase 2: Configure Display Output (1 hour)

#### Step 2.1: Set Resolution

Edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

Add/modify these lines:
```ini
# Force HDMI output
hdmi_force_hotplug=1

# Set resolution for micro-OLEDs
hdmi_group=2
hdmi_mode=87
hdmi_cvt=1920 1080 60 6 0 0 0

# Disable overscan
disable_overscan=1

# GPU memory for video processing
gpu_mem=256
```

Reboot and verify displays work.

#### Step 2.2: Configure Side-by-Side (SBS) Mode

For dual-eye display, we need to render the same image twice (or with IPD offset). Install framebuffer tools:

```bash
sudo apt install fbset
```

---

### Phase 3: Solder Audio Components (1-2 hours)

#### Step 3.1: I2S Microphone Wiring

Connect SPH0645 to Pi Zero 2 W:

| Mic Pin | Pi GPIO | Pi Physical Pin |
|---------|---------|-----------------|
| 3V      | 3.3V    | Pin 1           |
| GND     | GND     | Pin 6           |
| BCLK    | GPIO 18 | Pin 12          |
| LRCL    | GPIO 19 | Pin 35          |
| DOUT    | GPIO 20 | Pin 38          |

#### Step 3.2: Enable I2S Audio

Edit `/boot/config.txt`:
```ini
dtparam=i2s=on
dtoverlay=i2s-soundcard
```

Install audio drivers:
```bash
sudo apt install alsa-utils
```

Test recording:
```bash
arecord -D plughw:1,0 -f cd -d 5 test.wav
aplay test.wav
```

#### Step 3.3: Bone Conduction Speaker

Connect to GPIO 12 (PWM) or use a USB audio adapter for better quality.

---

### Phase 4: Assemble Optics (2 hours)

#### Step 4.1: Calculate Eye Relief

The Fresnel lens needs proper distance from eye and OLED:

```
[OLED] ←-- 50mm --→ [Fresnel] ←-- 50mm --→ [Eye]
```

- OLED to lens: ~50mm (focal length of lens)
- Lens to eye: ~50mm (comfortable viewing distance)

#### Step 4.2: Build Lens Holders

3D print or cut from cardboard:
- Tube to hold OLED at back
- Slot for Fresnel lens in middle
- Open front for eye

```
     ┌─────────────────────────────┐
     │  OLED   │   Fresnel   │ Eye │
     │  Mount  │    Slot     │     │
     └─────────────────────────────┘
           50mm       50mm
```

#### Step 4.3: Adjust IPD (Inter-Pupillary Distance)

Most adults have IPD between 54-74mm. Make lens holders adjustable:
- Use sliding rails, or
- Print multiple sizes (60mm, 65mm, 70mm spacing)

---

### Phase 5: Build Frame (2-3 hours)

#### Step 5.1: 3D Print Components

Print these parts (STL files in `docs/stl/` folder):

| Part | Quantity | Print Time |
|------|----------|------------|
| Main housing (eye chambers) | 1 | 4 hours |
| Camera mount | 1 | 30 min |
| Pi mount bracket | 1 | 1 hour |
| Battery holder | 1 | 45 min |

Print settings:
- Material: PLA or PETG
- Layer height: 0.2mm
- Infill: 20%
- Supports: Yes (for overhangs)

#### Step 5.2: Assembly Order

1. **Mount OLEDs** in rear of eye chambers (hot glue edges)
2. **Insert Fresnel lenses** into slots
3. **Attach foam eye cups** around openings
4. **Mount camera** on front center (facing out)
5. **Mount Pi Zero** on top or side of housing
6. **Attach battery holder** on rear/top

#### Step 5.3: Cable Management

- Route camera ribbon cable cleanly
- Use cable clips to secure wires
- Leave slack for head movement

---

### Phase 6: Power System (1 hour)

#### Step 6.1: Wire PowerBoost

```
LiPo Battery (+) → PowerBoost BAT
LiPo Battery (-) → PowerBoost GND
PowerBoost 5V    → Pi 5V (Pin 2)
PowerBoost GND   → Pi GND (Pin 6)
```

PowerBoost also powers:
- OLED driver board (if 5V input)
- Other components

#### Step 6.2: Add Power Switch

Wire a small toggle switch between battery and PowerBoost for on/off.

#### Step 6.3: Charging

The PowerBoost 1000C has built-in USB-C charging. Mount a USB-C port accessibly on the frame.

---

### Phase 7: Final Assembly (1 hour)

#### Step 7.1: Connect Everything

1. Camera ribbon → Pi Camera port
2. Mini HDMI → Driver board → OLEDs
3. I2S wires → Pi GPIO
4. PowerBoost → Pi 5V/GND
5. Bone conduction → GPIO 12

#### Step 7.2: Secure Components

- Hot glue or screw all components into mounts
- Zip-tie loose cables
- Add strain relief on ribbon cables

#### Step 7.3: Add Headstrap

Attach elastic headband with velcro for adjustable fit.

---

## 🔌 Complete Wiring Diagram

```
                    ┌──────────────────────────────────┐
                    │         FRONT OF GLASSES         │
                    │                                  │
                    │   [Pi Camera 3 Wide]             │
                    │          ○                       │
                    └──────────────────────────────────┘
                                   │ ribbon
                                   ▼
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│    ┌─────────┐                              ┌─────────┐        │
│    │  OLED   │◄───MIPI───┐      ┌───MIPI───►│  OLED   │        │
│    │  LEFT   │           │      │           │  RIGHT  │        │
│    └─────────┘           │      │           └─────────┘        │
│         │                │      │                │             │
│    ┌─────────┐      ┌────┴──────┴────┐     ┌─────────┐         │
│    │ FRESNEL │      │  HDMI-to-MIPI  │     │ FRESNEL │         │
│    │  LENS   │      │  Driver Board  │     │  LENS   │         │
│    └─────────┘      └───────┬────────┘     └─────────┘         │
│                             │ HDMI                             │
│                             ▼                                  │
│                    ┌─────────────────┐                         │
│                    │  Pi Zero 2 W   │◄──5V──┐                  │
│                    │                 │       │                 │
│                    │ GPIO 18,19,20 ──┼───────┼──► [I2S Mic]    │
│                    │ GPIO 12 ────────┼───────┼──► [Speaker]    │
│                    └─────────────────┘       │                 │
│                                              │                 │
│                    ┌─────────────────┐       │                 │
│                    │  PowerBoost    │───────┘                  │
│                    │    1000C       │                          │
│                    └────────┬───────┘                          │
│                             │                                  │
│                    ┌────────┴───────┐                          │
│                    │  3000mAh LiPo  │                          │
│                    └────────────────┘                          │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## ✅ Testing Checklist

- [ ] Pi boots and connects to WiFi
- [ ] Camera captures video
- [ ] Both OLEDs display image
- [ ] Microphone records audio
- [ ] Speaker plays audio
- [ ] Battery provides 2+ hours runtime
- [ ] Frame fits comfortably
- [ ] Lenses focus correctly at eye distance

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| OLEDs don't turn on | Check driver board power, verify HDMI connection |
| Image blurry | Adjust OLED-to-lens distance (should be ~50mm) |
| Display flickers | Add `hdmi_force_hotplug=1` to config.txt |
| No audio recording | Check I2S wiring, verify dtoverlay in config |
| Short battery life | Reduce Pi CPU frequency, lower display brightness |
| Uncomfortable fit | Adjust headstrap, add more foam padding |

---

## 📊 Expected Specs

| Spec | Value |
|------|-------|
| Resolution | 1920x1080 per eye |
| FOV | ~50° diagonal |
| Weight | ~200g |
| Battery Life | 2-3 hours |
| Latency | ~50-80ms (camera to display) |

---

## Next Steps

After hardware is built:

1. **Install D-Vision software** - `pip install -e .`
2. **Configure video passthrough** - Updates to `camera.py` and `ui.py`
3. **Test face recognition** - Verify overlays appear on passthrough video
4. **Add audio feedback** - TTS announces recognized people

See [SOFTWARE_SETUP.md](./SOFTWARE_SETUP.md) for software configuration.
