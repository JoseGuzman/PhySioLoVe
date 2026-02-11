# 🏃‍♂️ PhysioLog: Personal Health Tracker

A personal health tracking dashboard to visualize weight, body composition, nutrition, sleep, and activity metrics with an elegant dark-themed interface.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![UV](https://img.shields.io/badge/UV-Package%20Manager-purple)
![Flask](https://img.shields.io/badge/Flask-3.0-green)

## ✨ Features

- 🎨 **Dark Theme Interface** - Modern sidebar navigation with purple accents
- 📊 **Interactive Visualizations** - Plotly charts with time range selectors
- 📈 **Track Multiple Metrics** - Weight, body fat, calories, steps, and sleep
- 📉 **7-Day Moving Averages** - See trends clearly
- 📝 **Easy Data Entry** - Simple web form
- 📁 **CSV/TSV Import** - Import historical data
- 💾 **SQLite Database** - All data stored locally

## 🎯 Interface

### Navigation

- **TRACK Section**
  - 📊 Overview - Statistics cards + data entry form
  - 📈 Visualizations - 4 interactive charts with moving averages
- **MANAGE Section** (coming soon)
  - Data management features

### Charts

1. **Weight Trend** - Daily weight + 7-day average
2. **Body Fat Trend** - Daily body fat % + 7-day average
3. **Daily Steps** - Bar chart + 7-day average
4. **Sleep Total** - Sleep hours + 7-day average

All charts include time range selectors: Last 30 days, Last 90 days, All

## 📋 Prerequisites

- Python 3.11 or higher
- Git (optional, for version control)

## 🚀 Installation

### Step 1: Install UV

UV is a blazing-fast Python package manager (10-100x faster than pip!).

#### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows (PowerShell)

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Alternative: Install with pip

```bash
pip install uv
```

#### Verify Installation

After installation, **restart your terminal** and verify:

```bash
uv --version
```

You should see something like: `uv 0.x.x`

### Step 2: Clone or Download Project

```bash
# If using Git
git clone https://github.com/yourusername/physiolog.git
cd physiolog

# OR download and extract ZIP, then:
cd physiolog
```

### Step 3: Install Dependencies

```bash
uv sync
```

This command will:

- Create a virtual environment in `.venv/`
- Install Flask, SQLAlchemy, and pandas
- Create a `uv.lock` file for reproducible builds

⏱️ **Takes ~2 seconds** (compared to ~45 seconds with pip!)

### Step 4: Prepare Your Data (Optional)

Place your health data CSV or TSV file in the `data/` folder:

```bash
cp ~/path/to/your/health_data.csv data/
```

**Expected CSV format:**

Your file should have these columns (names are flexible):

- Date
- Weight (kg)
- Body Fat (%)
- Calories
- Steps
- Sleep total (h)
- Sleep Quality
- Observations

### Step 5: Import Your Data (Optional)

```bash
uv run python scripts/import_data.py data/health_data.csv
```

You should see:

```
📊 Importing data from data/health_data.csv...
📋 Found columns: ['Date', 'Weight (kg)', 'Body Fat (%)', ...]
✓ Import complete!
  • Added: 114 entries
```

### Step 6: Run the Application

```bash
uv run python app.py
```

You should see:

```
✓ Database initialized

🏃‍♂️ Health Tracker Starting...
📊 Visit: http://localhost:5000
```

### Step 7: Open in Browser

Open your web browser and navigate to:

**<http://localhost:5000>**

🎉 You should now see your health tracking dashboard!

## 📖 Usage

### Viewing Your Data

The **Overview** page displays:

- **Statistics Cards**: Average weight, body fat, calories, steps, total entries
- **Data Entry Form**: Add new daily entries

The **Visualizations** page displays:

- **4 Interactive Charts**: Weight, Body Fat, Steps, Sleep
- **7-Day Moving Averages**: Smoothed trend lines
- **Time Range Selectors**: View Last 30 days, 90 days, or All data

### Adding New Entries

1. Go to the Overview page
2. Fill in the form with your daily metrics
3. Click "Add Entry"
4. View updated statistics immediately!

### Re-importing Data

If you have new data to import:

```bash
uv run python scripts/import_data.py data/new_data.csv
```

The script will skip existing entries and only add new ones.

## 🎨 Customization

### Change Theme Colors

Edit `templates/base.html` to customize colors:

```css
/* Primary purple accent */
background: #8b5cf6;

/* Dark backgrounds */
background: #1a1a1a;  /* Main background */
background: #252525;  /* Card background */
background: #0f0f0f;  /* Sidebar background */

/* Borders */
border: 1px solid #cccccc;  /* Light grey borders */
```

## 📁 Project Structure

```
physiolog/
├── app.py                  # Main Flask application
├── pyproject.toml          # Project configuration & dependencies
├── uv.lock                 # Locked dependency versions
├── .venv/                  # Virtual environment (auto-created)
├── templates/
│   ├── base.html          # Base template with sidebar
│   ├── overview.html      # Overview page
│   └── visualizations.html # Charts page
├── scripts/
│   └── import_data.py     # Data import script
├── data/
│   └── health_data.csv    # Your health data (gitignored)
└── physiolog.db           # SQLite database (auto-created)
```

## 🐳 Docker Deployment (Coming Soon)

Preparing for deployment on AWS:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
EXPOSE 5000
CMD ["uv", "run", "python", "app.py"]
```

## 🔧 Common Commands

### Run the Application

```bash
uv run python app.py
```

### Import Data

```bash
uv run python scripts/import_data.py data/your_file.csv
```

### Add a New Package

```bash
uv add package-name
```

### Update All Packages

```bash
uv sync --upgrade
```

## 🐛 Troubleshooting

### UV command not found

After installation, restart your terminal. If still not working:

```bash
# macOS/Linux
export PATH="$HOME/.cargo/bin:$PATH"
source ~/.bashrc  # or ~/.zshrc
```

### Port 5000 already in use

```bash
# Find and kill the process
lsof -i :5000
kill -9 <PID>

# Or use a different port (edit app.py, last line)
```

### Database is locked

```bash
# Stop the app (Ctrl+C) and delete the database
rm physiolog.db

# Re-import your data
uv run python scripts/import_data.py data/health_data.csv
```

## 🔒 Data Privacy

Your health data stays **local**:

- Stored in `physiolog.db` (SQLite database)
- Never sent to any server
- You have complete control

## 🎯 Roadmap

- [ ] Docker containerization
- [ ] AWS deployment (Lightsail/ECS)
- [ ] PostgreSQL support
- [ ] Export functionality (CSV/Excel)
- [ ] Additional charts (correlations, trends)
- [ ] Mobile-responsive improvements
- [ ] User authentication

## 📄 License

MIT License - Feel free to use and modify!

## 🙏 Acknowledgments

Built with:

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Plotly](https://plotly.com/javascript/) - Interactive charts
- [UV](https://github.com/astral-sh/uv) - Fast package manager
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM

---

**Happy tracking!** 💪📊
