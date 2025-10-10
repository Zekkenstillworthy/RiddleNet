# 🎯 Quick Image Mapping Guide

## Images You Uploaded → Filenames to Save

### 📸 Image Mapping

| **Image Description** | **Save As** | **Purpose** | **Priority** |
|----------------------|-------------|-------------|--------------|
| Shield with crimping tool + cable | `cable_master_badge.png` | Crimping achievement | ⭐ REQUIRED |
| PC/Desktop computer (dark blue) | `computer_device.png` | Network topology device | 🔵 Optional |
| Router with antennas (dark blue) | `router_device.png` | Network topology device | 🔵 Optional |
| Network switch (dark blue) | `switch_device.png` | Network topology device | 🔵 Optional |
| Shield with wrench + screwdriver | `troubleshooting_pro_badge.png` | Troubleshooting achievement | ⭐ REQUIRED |

---

## 📂 Where to Save All Images

**Directory:** `c:\Users\gilbe\OneDrive\Desktop\RiddleNet\static\img\`

**Full Paths:**
```
c:\Users\gilbe\OneDrive\Desktop\RiddleNet\static\img\cable_master_badge.png
c:\Users\gilbe\OneDrive\Desktop\RiddleNet\static\img\computer_device.png
c:\Users\gilbe\OneDrive\Desktop\RiddleNet\static\img\router_device.png
c:\Users\gilbe\OneDrive\Desktop\RiddleNet\static\img\switch_device.png
c:\Users\gilbe\OneDrive\Desktop\RiddleNet\static\img\troubleshooting_pro_badge.png
```

---

## 🎯 When Each Badge Appears

### Cable Master Badge 🏆
**File:** `cable_master_badge.png`

**Triggers:**
- User scores 100% (perfect) on any crimping challenge
- User scores 75%+ on Hard mode (Rollover wiring)

**Where it shows:**
- Achievement list in crimping simulation results modal
- Dashboard achievements section

### Troubleshooting Pro Badge 🔧
**File:** `troubleshooting_pro_badge.png`

**Triggers:**
- User completes troubleshooting scenario with zero mistakes
- "Perfectionist" achievement unlocked

**Where it shows:**
- Achievement notification popup
- Achievement list in performance sidebar

---

## 🖥️ Device Images (Optional)

**Note:** Your app already has device images (`PC.png`, `Router.png`, `Switch.png`). 
The new device images can:
1. **Replace** existing ones (same functionality, new look)
2. **Supplement** them (offer alternative styles)

### Current vs New

| Device Type | Current File | Your New File | Status |
|-------------|--------------|---------------|--------|
| Computer/PC | `PC.png` | `computer_device.png` | ✅ Already integrated |
| Router | `Router.png` | `router_device.png` | ✅ Already integrated |
| Switch | `Switch.png` | `switch_device.png` | ✅ Already integrated |

**To use your new device images:**
- Either: Overwrite the existing files
- Or: Keep both and update references in code

---

## ⚡ Quick Start (3 Steps)

1. **Save the 2 badge images** (required):
   - `cable_master_badge.png`
   - `troubleshooting_pro_badge.png`

2. **Optionally save device images**:
   - `computer_device.png`, `router_device.png`, `switch_device.png`

3. **Restart app and test:**
   ```cmd
   python run.py
   ```

---

## 🧪 Testing

### Test Cable Master Badge:
1. Open Crimping Simulation
2. Complete with perfect wire placement (100%)
3. View results → Badge should appear in achievements

### Test Troubleshooting Pro Badge:
1. Open Troubleshooting page
2. Complete a scenario without any errors
3. Check achievement notification → Badge should appear

### Test Device Images:
1. Open Topology or Gamified Topology page
2. Check device palette → Images should load
3. Drag device to canvas → Should render properly

---

## 📋 Checklist

- [ ] Downloaded all 5 images from chat
- [ ] Renamed images to exact filenames listed above
- [ ] Saved to `static/img/` directory
- [ ] Restarted application
- [ ] Cleared browser cache (Ctrl+Shift+Delete)
- [ ] Tested crimping perfect score
- [ ] Tested troubleshooting completion
- [ ] Verified badges display correctly

---

## 💡 Tips

- **Exact Filenames:** Must match exactly (case-sensitive)
- **File Format:** Keep as PNG with transparency
- **Don't resize:** Code handles resizing automatically
- **Test First:** Try badge images first (most important)
- **Backup:** Keep original device images as backup

---

## 🆘 Help

**Badge not showing?**
1. Check filename spelling
2. Verify file is in `static/img/`
3. Clear browser cache
4. Check browser console for errors

**Device images broken?**
1. Confirm images are PNG format
2. Check file permissions
3. Restart Flask server

---

**Status:** ✅ Code is ready! Just add the images and test!
