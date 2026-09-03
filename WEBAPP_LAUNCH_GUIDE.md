# 🚀 WEBAPP LAUNCH GUIDE - COMPREHENSIVE

Your project has **4 webapps** ready to run. Here's how to launch each one:

---

## 1️⃣ MOBILE WEB APP - MS Trial Compass (Easiest)

**What it does**: Interactive clinical trials monitor for Multiple Sclerosis  
**Location**: `mobile/index.html`  
**Type**: Progressive Web App (PWA)  
**Status**: ✅ Ready now  

### Launch Options:

#### Option A: Open Directly (Instant)
```bash
# Just open the file in your browser
# File path: C:\Users\49174\projects\autonomous-scientific-agent\mobile\index.html
```

#### Option B: Use Simple HTTP Server (Recommended)
```powershell
# Navigate to mobile folder
cd "C:\Users\49174\projects\autonomous-scientific-agent\mobile"

# Option 1: Python built-in server
python -m http.server 8000

# Then visit: http://localhost:8000/index.html
```

#### Option C: Use Live Server (VS Code)
```
1. Open mobile/index.html in VS Code
2. Right-click → "Open with Live Server"
3. Opens automatically at: http://127.0.0.1:5500/index.html
```

### Features:
- ✅ Search active MS clinical trials
- ✅ Filter by status, phase, location
- ✅ Real-time data from ClinicalTrials.gov
- ✅ Works offline (PWA)
- ✅ Install as mobile app
- ✅ Responsive design

### Direct Link:
```
File: C:\Users\49174\projects\autonomous-scientific-agent\mobile\index.html
```

---

## 2️⃣ INTERACTIVE CLINICAL TRIALS DASHBOARD

**What it does**: Visual dashboard of clinical trials data  
**Location**: `visuals/ms_clinical_trials.html`  
**Type**: Static HTML (1858 lines)  
**Status**: ✅ Ready now  

### Launch:
```bash
# Option 1: Open directly
# File: C:\Users\49174\projects\autonomous-scientific-agent\visuals\ms_clinical_trials.html

# Option 2: Serve with Python
cd "C:\Users\49174\projects\autonomous-scientific-agent\visuals"
python -m http.server 8001
# Visit: http://localhost:8001/ms_clinical_trials.html
```

### Features:
- ✅ Interactive trial data visualization
- ✅ Charts and graphs
- ✅ Real-time updates
- ✅ Searchable database
- ✅ Geographic filtering

---

## 3️⃣ PYTHON FLASK DASHBOARD

**What it does**: Agent results, metrics, and system monitoring  
**Location**: `src/dashboard/app.py`  
**Type**: Flask application  
**Status**: ✅ Ready to run  

### Quick Start:
```powershell
cd "C:\Users\49174\projects\autonomous-scientific-agent"

# Install dependencies (if needed)
pip install flask

# Run the dashboard
python -m src.dashboard.app
```

### Expected Output:
```
 * Running on http://127.0.0.1:5000/
 * Press CTRL+C to quit
```

### Access:
```
http://localhost:5000
```

### Features:
- ✅ Evaluation reports
- ✅ System status monitoring
- ✅ Metrics visualization
- ✅ Agent results display
- ✅ Real-time updates

---

## 4️⃣ R SHINY ANALYTICS DASHBOARD

**What it does**: Advanced statistical analysis and visualization  
**Location**: `r/shiny_dashboard.R`  
**Type**: Shiny interactive app  
**Status**: ✅ Ready to run  

### Requirements:
```r
# Make sure you have R installed
# https://www.r-project.org/

# Install required packages (first time only)
install.packages("shiny")
install.packages("ggplot2")
install.packages("plotly")
install.packages("dplyr")
```

### Launch:
```bash
# Option 1: Command line
R -e "shiny::runApp('r/shiny_dashboard.R')"

# Option 2: From R console
# Open R/RStudio and run:
shiny::runApp("r/shiny_dashboard.R")

# Option 3: Using RStudio
# Open r/shiny_dashboard.R in RStudio
# Click "Run App" button
```

### Expected Output:
```
Listening on http://127.0.0.1:5642
```

### Features:
- ✅ Interactive analytics
- ✅ Mathematical visualization
- ✅ Statistical testing
- ✅ Data exploration
- ✅ Real-time computation

---

## 📊 COMPARISON TABLE

| Webapp | Location | Type | Start Command | URL | Best For |
|--------|----------|------|---|---|---|
| **Mobile Trial Compass** | `mobile/index.html` | PWA | Open or `http.server` | `file://` or `localhost:8000` | Mobile, clinical trials, offline |
| **Clinical Trials Dashboard** | `visuals/ms_clinical_trials.html` | HTML | Open or `http.server` | `file://` or `localhost:8001` | Visualization, trials data |
| **Python Dashboard** | `src/dashboard/app.py` | Flask | `python -m src.dashboard.app` | `localhost:5000` | Agent results, metrics |
| **R Analytics Dashboard** | `r/shiny_dashboard.R` | Shiny | `Rscript` or RStudio | `localhost:5642` | Statistical analysis, plots |

---

## 🚀 QUICK START COMMANDS

### Launch All at Once:
```powershell
# Terminal 1 - Mobile App
cd "C:\Users\49174\projects\autonomous-scientific-agent\mobile"
python -m http.server 8000

# Terminal 2 - Trials Dashboard  
cd "C:\Users\49174\projects\autonomous-scientific-agent\visuals"
python -m http.server 8001

# Terminal 3 - Python Dashboard
cd "C:\Users\49174\projects\autonomous-scientific-agent"
python -m src.dashboard.app

# Terminal 4 - R Dashboard (if R installed)
R -e "shiny::runApp('r/shiny_dashboard.R')"
```

### Access All:
```
Mobile App:         http://localhost:8000/index.html
Trials Dashboard:   http://localhost:8001/ms_clinical_trials.html
Python Dashboard:   http://localhost:5000
R Analytics:        http://localhost:5642
```

---

## 🎯 RECOMMENDED FOR YOU

### Easiest to Start (Now):
1. **Mobile Web App** ← Start here!
   ```bash
   # Just open this file:
   C:\Users\49174\projects\autonomous-scientific-agent\mobile\index.html
   ```

2. **Interactive Dashboard**
   ```bash
   # Or open this file:
   C:\Users\49174\projects\autonomous-scientific-agent\visuals\ms_clinical_trials.html
   ```

### Run Locally:
```powershell
# Start Python Dashboard
cd "C:\Users\49174\projects\autonomous-scientific-agent"
python -m src.dashboard.app
# Visit: http://localhost:5000
```

---

## 📋 FILE PATHS

```
📱 Mobile App
C:\Users\49174\projects\autonomous-scientific-agent\mobile\index.html

📊 Clinical Trials Dashboard  
C:\Users\49174\projects\autonomous-scientific-agent\visuals\ms_clinical_trials.html

🐍 Python Dashboard
C:\Users\49174\projects\autonomous-scientific-agent\src\dashboard\app.py

📈 R Analytics Dashboard
C:\Users\49174\projects\autonomous-scientific-agent\r\shiny_dashboard.R
```

---

## ✅ WHAT YOU CAN DO WITH EACH

### Mobile Trial Compass
- Search 100+ active MS clinical trials
- Filter by status, phase, location
- View eligibility criteria
- Get trial details and contacts
- Works offline
- Install as app

### Clinical Trials Dashboard
- Visualize trial data
- Interactive charts
- Real-time updates
- Geographic filtering
- Trial analysis

### Python Dashboard
- View agent evaluation results
- Monitor system performance
- See metrics and KPIs
- Track research progress
- Export reports

### R Analytics Dashboard
- Advanced statistical analysis
- Data visualization
- Mathematical testing
- Interactive plots
- Statistical insights

---

## 🌐 URLS AT A GLANCE

```
Mobile Web App:
  File: C:\Users\49174\projects\autonomous-scientific-agent\mobile\index.html
  Or:   http://localhost:8000/index.html

Trials Dashboard:
  File: C:\Users\49174\projects\autonomous-scientific-agent\visuals\ms_clinical_trials.html
  Or:   http://localhost:8001/ms_clinical_trials.html

Python Dashboard:
  http://localhost:5000

R Dashboard:
  http://localhost:5642
```

---

## 🎯 NEXT STEPS

1. **Choose your preferred webapp** (I recommend Mobile first!)
2. **Follow the launch command** for that webapp
3. **Visit the URL** in your browser
4. **Explore the features** and data
5. **Try other webapps** as needed

---

## 💡 TROUBLESHOOTING

### Port Already in Use
```powershell
# Use different ports
python -m http.server 9000    # Instead of 8000
python -m http.server 9001    # Instead of 8001
```

### Python Module Not Found
```powershell
# Install required packages
pip install flask
pip install plotly
pip install pandas
```

### R Not Installed
```
Download from: https://www.r-project.org/
Then: install.packages("shiny")
```

### Can't Open File
```
Use full path:
start "C:\Users\49174\projects\autonomous-scientific-agent\mobile\index.html"
```

---

**Status**: ✅ All 4 webapps ready to launch  
**Recommendation**: Start with Mobile Trial Compass!  
**Next**: Pick one and start exploring! 🚀
