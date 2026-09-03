# 🌐 WEB APPLICATIONS GUIDE - RUN COMMANDS

Your project includes **5 different web applications**. Choose one to run:

---

## 🎯 QUICKEST START (Recommended)

### Clinical Trials Interactive Dashboard
**Best for**: Visual data analysis, clinical research

```bash
# In PowerShell, run:
cd C:\Users\49174\projects\autonomous-scientific-agent
python -m http.server 8001 --directory visuals/
```

**Then open in browser:**
```
http://localhost:8001/ms_clinical_trials.html
```

**Features:**
- ✅ Interactive clinical trial visualization
- ✅ Real-time data analysis
- ✅ Responsive design (mobile/desktop)
- ✅ No dependencies needed
- ✅ 1,858 lines of modern JavaScript

---

## 📱 ALL AVAILABLE WEB APPS

### 1. CLINICAL TRIALS DASHBOARD (HTML) ⭐ RECOMMENDED
```bash
cd C:\Users\49174\projects\autonomous-scientific-agent
python -m http.server 8001 --directory visuals/
```
**URL**: http://localhost:8001/ms_clinical_trials.html  
**Type**: Pure HTML/JavaScript (no server code needed)  
**Features**: Interactive charts, real-time analysis  

### 2. MOBILE PWA (Progressive Web App)
```bash
cd C:\Users\49174\projects\autonomous-scientific-agent
python -m http.server 8000 --directory mobile/
```
**URL**: http://localhost:8000  
**Type**: Cross-platform mobile app  
**Features**: Offline support, installable, responsive  

### 3. TRIALS WEB SERVER (Python)
```bash
cd C:\Users\49174\projects\autonomous-scientific-agent
python scripts/serve_ms_trials.py
```
**URL**: http://localhost:8080  
**Type**: Python Flask server  
**Features**: Backend API, data processing  

### 4. FLASK DASHBOARD (Python)
```bash
cd C:\Users\49174\projects\autonomous-scientific-agent
python -m src.dashboard.app
```
**URL**: http://localhost:5000  
**Type**: Python Flask dashboard  
**Features**: System metrics, performance monitoring  

### 5. SHINY DASHBOARD (R - if R is installed)
```bash
cd C:\Users\49174\projects\autonomous-scientific-agent
Rscript r/shiny_dashboard.R
```
**URL**: http://localhost:3838  
**Type**: R Shiny interactive dashboard  
**Features**: Statistical analysis, R integration  

---

## 🚀 STEP-BY-STEP: RUN CLINICAL TRIALS DASHBOARD

### Step 1: Open PowerShell
- Press `Win + X` → Select "Windows PowerShell" or "Terminal"

### Step 2: Navigate to Project
```powershell
cd C:\Users\49174\projects\autonomous-scientific-agent
```

### Step 3: Start Web Server
```powershell
python -m http.server 8001 --directory visuals/
```

### Step 4: Open in Browser
- Copy and paste: `http://localhost:8001/ms_clinical_trials.html`
- Or click the link from the terminal

### Step 5: Explore Dashboard
- View clinical trial data
- Interact with charts
- Analyze research findings

### Step 6: Stop Server
- Press `Ctrl + C` in PowerShell to stop

---

## 📋 WHICH APP TO CHOOSE?

| App | Best For | Start Command | URL |
|-----|----------|--------------|-----|
| **Clinical Trials** | Visual analysis | `python -m http.server 8001 --directory visuals/` | http://localhost:8001/ms_clinical_trials.html |
| **Mobile PWA** | Cross-platform | `python -m http.server 8000 --directory mobile/` | http://localhost:8000 |
| **Trials Server** | Backend API | `python scripts/serve_ms_trials.py` | http://localhost:8080 |
| **Flask Dashboard** | System monitoring | `python -m src.dashboard.app` | http://localhost:5000 |
| **Shiny Dashboard** | R analytics | `Rscript r/shiny_dashboard.R` | http://localhost:3838 |

---

## 🎯 RECOMMENDED CHOICE

**Clinical Trials Dashboard** (`http://localhost:8001/ms_clinical_trials.html`)

**Why?**
- ✅ Easiest to run (just HTTP server)
- ✅ No Python dependencies
- ✅ Beautiful interactive interface
- ✅ Real clinical data visualization
- ✅ Works on any device (mobile/desktop)
- ✅ 1,858 lines of well-structured code

---

## 💻 COMMAND COPY-PASTE READY

### For Clinical Trials Dashboard:
```powershell
cd C:\Users\49174\projects\autonomous-scientific-agent; python -m http.server 8001 --directory visuals/
```

### For Mobile PWA:
```powershell
cd C:\Users\49174\projects\autonomous-scientific-agent; python -m http.server 8000 --directory mobile/
```

### For Trials Server:
```powershell
cd C:\Users\49174\projects\autonomous-scientific-agent; python scripts/serve_ms_trials.py
```

---

## 🌐 FILE LOCATIONS

```
autonomous-scientific-agent/
├── visuals/
│   └── ms_clinical_trials.html          ← Main dashboard
│   ├── ms_clinical_trials_preview.png
│   ├── portfolio_slide_deck.pdf
│   └── [other reports and images]
├── mobile/
│   ├── index.html                       ← PWA entry
│   ├── manifest.webmanifest
│   └── sw.js
├── scripts/
│   ├── serve_ms_trials.py               ← Trials server
│   └── [other utilities]
└── src/
    └── dashboard/
        └── app.py                       ← Flask dashboard
```

---

## 🆘 TROUBLESHOOTING

### "Port already in use" error
**Solution**: Change the port number
```powershell
# Instead of 8001, use 8002:
python -m http.server 8002 --directory visuals/
# Then go to: http://localhost:8002/ms_clinical_trials.html
```

### "Python not found" error
**Solution**: Use full path to Python
```powershell
C:\Users\49174\AppData\Local\Programs\Python\Python311\python.exe -m http.server 8001 --directory visuals/
```

### "Command not found" error
**Solution**: Make sure you're in the right directory
```powershell
cd C:\Users\49174\projects\autonomous-scientific-agent
# Then run the command again
```

### Browser shows "cannot GET" error
**Solution**: Check the URL format
```
Correct: http://localhost:8001/ms_clinical_trials.html
Wrong: http://localhost:8001/visuals/ms_clinical_trials.html
```

---

## 🎨 WHAT YOU'LL SEE

### Clinical Trials Dashboard Features:
- 📊 Interactive charts and graphs
- 📈 Real-time data updates
- 🔍 Search and filter capabilities
- 📱 Mobile-responsive design
- 🎯 Clinical trial metrics
- 📋 Research data analysis
- 💡 Evidence-based insights

---

## 📞 QUICK REFERENCE

**Most Popular**: Clinical Trials Dashboard
```
http://localhost:8001/ms_clinical_trials.html
```

**Mobile-First**: PWA
```
http://localhost:8000
```

**Data Backend**: Trials Server
```
http://localhost:8080
```

---

## ✅ READY TO RUN

Copy this command and paste in PowerShell:

```
cd C:\Users\49174\projects\autonomous-scientific-agent; python -m http.server 8001 --directory visuals/
```

Then open: **http://localhost:8001/ms_clinical_trials.html**

**That's it!** 🎉

