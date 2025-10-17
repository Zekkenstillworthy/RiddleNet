# 🎯 Quick Reference: Wired & Wireless Connections in Troubleshooting Module

## 🔌 Connection Types at a Glance

### Wired Connections
```
Button: 🔗 "Wired"
Color: Cyan (#00D9FF)
Style: ━━━━━━━━ (Solid line)
Width: 3px
Use: Physical cables, Ethernet
```

### Wireless Connections
```
Button: 📶 "Wireless"  
Color: Purple (#8B5CF6)
Style: ┄┄┄┄┄┄┄┄ (Dashed line)
Width: 2px
Use: WiFi, wireless links
```

---

## 📍 Visual Quick ID

| What You See | Connection Type |
|--------------|----------------|
| **Solid cyan line** | Wired (Ethernet) |
| **Dashed purple line** | Wireless (WiFi) |
| **Cyan preview line** | Drawing wired connection |
| **Purple preview line** | Drawing wireless connection |
| **Cyan device border** | First device selected (wired mode) |
| **Purple device border** | First device selected (wireless mode) |
| **Green glow** | Connection selected |

---

## ⚡ Quick Actions

### Create Wired Connection
1. Click **Wired** button (🔗)
2. Click device #1 → See cyan border
3. Click device #2 → Solid cyan line appears

### Create Wireless Connection
1. Click **Wireless** button (📶)
2. Click device #1 → See purple border
3. Click device #2 → Dashed purple line appears

### Cancel Connection
- Click active button again
- Switch to different tool
- Click empty canvas area

### Delete Connection
1. Click **Remove Link** button (🔗)
2. Click on the connection to delete

---

## 🎨 Color Codes (for developers)

```javascript
// Wired
const WIRED_COLOR = '#00D9FF';        // Cyan
const WIRED_LINE_WIDTH = 3;
ctx.setLineDash([]);                  // Solid

// Wireless  
const WIRELESS_COLOR = '#8B5CF6';     // Purple
const WIRELESS_LINE_WIDTH = 2;
ctx.setLineDash([8, 4]);              // Dashed

// Selection
const SELECTION_COLOR = '#39FF14';     // Neon green

// Preview
const PREVIEW_WIRED = 'rgba(0, 217, 255, 0.6)';
const PREVIEW_WIRELESS = 'rgba(139, 92, 246, 0.6)';
```

---

## 🧪 Quick Test Checklist

✅ **Wired**: Solid cyan, 3px wide  
✅ **Wireless**: Dashed purple, 2px wide  
✅ **Preview**: Shows while drawing  
✅ **Tooltip**: Displays connection type on hover  
✅ **Buttons**: Toggle on/off correctly  
✅ **Colors**: Match dynamic simulation  

---

## 🔧 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Buttons not visible | Hard refresh (Ctrl+F5) |
| All connections same color | Check connection.type property |
| No preview line | Verify mousemove listener |
| Dashed line not showing | Check setLineDash([8, 4]) called |

---

## 📊 Comparison with Dynamic Simulation

| Feature | Troubleshooting | Dynamic Simulation | Match? |
|---------|----------------|-------------------|---------|
| Wired color | Cyan (#00D9FF) | Cyan (#00D9FF) | ✅ |
| Wireless color | Purple (#8B5CF6) | Purple (#8B5CF6) | ✅ |
| Wired style | Solid | Solid | ✅ |
| Wireless style | Dashed (8-4) | Dashed (8-4) | ✅ |
| Line widths | 3px / 2px | 3px / 2px | ✅ |
| Preview | Yes | Yes | ✅ |

---

## 📱 Testing URLs

- **Troubleshooting**: http://127.0.0.1:5001/troubleshooting/
- **Dynamic Simulation** (reference): http://127.0.0.1:5001/dynamic/simulation/70

---

**Last Updated**: October 7, 2025  
**Status**: ✅ Complete  
**Version**: MVP 1.0
