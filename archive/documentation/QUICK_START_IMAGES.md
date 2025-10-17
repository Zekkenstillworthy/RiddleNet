# 🎯 Quick Start Guide - Adding Topology Images to Quiz

## Step 1: Save the Images ⬇️

Save both images from your chat to this folder:
```
c:\Users\gilbe\OneDrive\Desktop\RiddleNet\static\images\topology\
```

### Image Files:
1. **bus-topology.jpg** - The image showing computers connected to a horizontal network backbone
2. **ring-topology.jpg** - The image showing computers connected in a circular/ring formation

## Step 2: Test the Images 🧪

Visit this test page to verify images are loaded:
```
http://127.0.0.1:5001/quiz/test-images
```

You should see:
- ✅ Green checkmarks if images loaded successfully
- ❌ Red error messages if images are missing

## Step 3: Try the Quiz 🎮

Go to the quiz page:
```
http://127.0.0.1:5001/quiz/
```

The topology images will appear on:
- **Question 7** - Bus Topology (with BUS image)
- **Question 8** - Ring Topology (with RING image)

## Visual Guide

### What You'll See in the Quiz:

```
┌─────────────────────────────────────┐
│ Question 7 of 30                    │
│                                     │
│ What type of network topology is    │
│ shown in the image below?           │
│                                     │
│  ╔════════════════════════════╗    │
│  ║  [BUS TOPOLOGY IMAGE]      ║    │
│  ║  Computers on a backbone   ║    │
│  ╚════════════════════════════╝    │
│                                     │
│  A) Bus Topology                    │
│  B) Star Topology                   │
│  C) Ring Topology                   │
│  D) Mesh Topology                   │
└─────────────────────────────────────┘
```

## Troubleshooting 🔧

### Images Not Showing?

**Check 1:** File names are exact
- ✅ `bus-topology.jpg` (lowercase, hyphen, .jpg)
- ❌ NOT `Bus-Topology.JPG` or `bus_topology.png`

**Check 2:** Files in correct folder
```
RiddleNet/
  └── static/
      └── images/
          └── topology/
              ├── bus-topology.jpg  ← HERE
              └── ring-topology.jpg ← HERE
```

**Check 3:** Restart Flask server
```cmd
# Stop server (Ctrl+C)
# Start again
python run.py
```

**Check 4:** Clear browser cache
- Press `Ctrl + Shift + R` to hard refresh

## Quick Commands 💻

### Check if files exist:
```cmd
dir "c:\Users\gilbe\OneDrive\Desktop\RiddleNet\static\images\topology\"
```

You should see:
```
bus-topology.jpg
ring-topology.jpg
```

## What Was Changed? 📝

✅ **quiz_challenge.html** - Added image support
✅ **quiz_routes.py** - Added test route
✅ **CSS** - Added image styling
✅ **JavaScript** - Added image rendering

## Features ✨

- 🖼️ Images display beautifully with glow effects
- 📱 Fully responsive on mobile
- ✨ Hover to zoom slightly
- 🎨 Matches RiddleNet's cyber theme
- ⚡ Fast loading

## Need Help? 🆘

If images still don't show:
1. Check browser console (F12) for errors
2. Verify file names exactly match
3. Ensure Flask server is running
4. Try the test page first
5. Check file permissions

---

**Ready to test?** → http://127.0.0.1:5001/quiz/test-images

**Ready to quiz?** → http://127.0.0.1:5001/quiz/
