// static/js/dashboard.js

// -----------------------------
// Config
// -----------------------------
const CHART_IDS = ['weightChart', 'bodyFatChart', 'stepsChart', 'sleepChart'];

const BASE_LAYOUT = {
    paper_bgcolor: '#252525', // card background
    plot_bgcolor: '#252525',//plot_bgcolor: '#202020',
    font: { color: '#e0e0e0' },
    hovermode: 'x unified',
    showlegend: false,
    margin: { t: 20, r: 20, b: 60, l: 60 }
};

const PLOTLY_CONFIG = {
    responsive: true,
    displaylogo: false,
    scrollZoom: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
};


// Store latest date so global range buttons anchor correctly
let LATEST_DATE_ISO = null;

// -----------------------------
// Utilities
// -----------------------------
/**
 * Calculates moving average over numeric array.
 */
function calculateMovingAverage(data, windowSize = 7) {
    const result = [];
    for (let i = 0; i < data.length; i++) {
        if (i < windowSize - 1) {
            result.push(null);
            continue;
        }
        const window = data.slice(i - windowSize + 1, i + 1).filter(v => v != null);
        if (window.length === 0) {
            result.push(null);
            continue;
        }
        const avg = window.reduce((a, b) => a + b, 0) / window.length;
        result.push(avg);
    }
    return result;
}
/**
 * Creates a standardized x-axis configuration for time-series charts.
 *
 * @param {number} angle - Rotation angle for tick labels (default: -45).
 * @returns {Object} Plotly x-axis configuration object.
 */
function makeXAxis(angle = -45) {
    return {
        type: 'date',
        tickangle: angle
    };
}

async function fetchJson(url, options) {
    const res = await fetch(url, options);
    if (!res.ok) {
        const text = await res.text().catch(() => '');
        throw new Error(`${url} failed: ${res.status} ${res.statusText} ${text}`);
    }
    return res.json();
}

function hasAnyElement(ids) {
    return ids.some(id => document.getElementById(id));
}

function setButtonActive(activeId) {
    const ids = ['btn30', 'btn90', 'btnAll'];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        el.style.opacity = (id === activeId) ? '1' : '0.7';
        el.style.transform = (id === activeId) ? 'translateY(-1px)' : 'none';
    });
}

// -----------------------------
// Global range controls
// -----------------------------
function setGlobalRange(days) {
    if (!hasAnyElement(CHART_IDS)) return;
    if (!LATEST_DATE_ISO) return;

    if (days == null) {
        // All
        CHART_IDS.forEach(id => {
            if (document.getElementById(id)) {
                Plotly.relayout(id, { 'xaxis.autorange': true });
            }
        });
        setButtonActive('btnAll');
        return;
    }

    const end = new Date(LATEST_DATE_ISO + 'T00:00:00');
    const start = new Date(end);
    start.setDate(start.getDate() - days);

    const update = {
        'xaxis.range': [start.toISOString().slice(0, 10), end.toISOString().slice(0, 10)]
    };

    CHART_IDS.forEach(id => {
        if (document.getElementById(id)) {
            Plotly.relayout(id, update);
        }
    });

    setButtonActive(days === 30 ? 'btn30' : 'btn90');
}

// -----------------------------
// Stats
// -----------------------------
async function loadStats() {
    const statsEl = document.getElementById('stats');
    if (!statsEl) return;

    try {
        const stats = await fetchJson('/api/stats');

        statsEl.innerHTML = `
            <div class="stat-card">
                <div class="stat-label">Avg Weight</div>
                <div class="stat-value">${stats.avg_weight ?? '--'} kg</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Body Fat</div>
                <div class="stat-value">${stats.avg_body_fat ?? '--'}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Calories</div>
                <div class="stat-value">${stats.avg_calories ?? '--'}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Steps</div>
                <div class="stat-value">${stats.avg_steps ?? '--'}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Entries</div>
                <div class="stat-value">${stats.total_entries ?? '--'}</div>
            </div>
        `;
    } catch (err) {
        console.error(err);
        statsEl.innerHTML = `
            <div class="stat-card">
                <div class="stat-label">Stats</div>
                <div class="stat-value">--</div>
            </div>
        `;
    }
}

// -----------------------------
// Charts
// -----------------------------
async function loadCharts() {
    if (!hasAnyElement(CHART_IDS)) return;

    let entries;
    try {
        entries = await fetchJson('/api/entries');
    } catch (err) {
        console.error(err);
        return;
    }

    // Sort ascending by date (oldest -> newest)
    entries.sort((a, b) => new Date(a.date) - new Date(b.date));

    const dates = entries.map(e => e.date);
    if (dates.length) LATEST_DATE_ISO = dates[dates.length - 1];

    // -----------------------------
    // Weight
    // -----------------------------
    if (document.getElementById('weightChart')) {
        const weightData = entries.map(e => e.weight);
        const weightMA = calculateMovingAverage(weightData, 7);

        Plotly.react('weightChart', [
            {
                x: dates,
                y: weightData,
                name: 'Daily Weight',
                type: 'scatter',
                mode: 'markers',
                marker: { size: 6, opacity: 0.5 }
            },
            {
                x: dates,
                y: weightMA,
                name: '7-Day Average',
                type: 'scatter',
                mode: 'lines'
            }
        ], {
            ...BASE_LAYOUT,
            yaxis: {
                title: 'Weight (kg)', gridcolor: '#333',
                tickcolor: '#888',
                linecolor: '#888'
            },
            xaxis: {
                ...makeXAxis(-30), gridcolor: '#333',
            },
            hovermode: 'x unified',
        }, PLOTLY_CONFIG);
    }

    // -----------------------------
    // Body fat
    // -----------------------------
    if (document.getElementById('bodyFatChart')) {
        const bfData = entries.map(e => e.body_fat);
        const bfMA = calculateMovingAverage(bfData, 7);

        Plotly.react('bodyFatChart', [
            {
                x: dates,
                y: bfData,
                name: 'Daily Body Fat',
                type: 'scatter',
                mode: 'markers',
                marker: { size: 6, opacity: 0.5 }
            },
            {
                x: dates,
                y: bfMA,
                name: '7-Day Average',
                type: 'scatter',
                mode: 'lines'
            }
        ], {
            ...BASE_LAYOUT,
            yaxis: { title: 'Body Fat (%)', tickcolor: '#888', linecolor: '#888', gridcolor: '#333' },
            xaxis: { ...makeXAxis(-30), gridcolor: '#333' },
            hovermode: 'x unified',
        }, PLOTLY_CONFIG);
    }

    // -----------------------------
    // Steps
    // -----------------------------
    if (document.getElementById('stepsChart')) {
        const stepsData = entries.map(e => e.steps);
        const stepsMA = calculateMovingAverage(stepsData, 7);

        Plotly.react('stepsChart', [
            {
                x: dates,
                y: stepsData,
                name: 'Daily Steps',
                type: 'bar',
                opacity: 0.6
            },
            {
                x: dates,
                y: stepsMA,
                name: '7-Day Average',
                type: 'scatter',
                mode: 'lines'
            }
        ], {
            ...BASE_LAYOUT,
            yaxis: { title: 'Steps', linecolor: '#888', tickcolor: '#888' },
            xaxis: { ...makeXAxis(-30), linecolor: '#888', tickcolor: '#888' },
        }, PLOTLY_CONFIG);
    }

    // -----------------------------
    // Sleep
    // -----------------------------
    if (document.getElementById('sleepChart')) {
        const sleepData = entries.map(e => e.sleep_total);
        const sleepMA = calculateMovingAverage(sleepData, 7);

        Plotly.react('sleepChart', [
            {
                x: dates,
                y: sleepData,
                name: 'Daily Sleep',
                type: 'bar',
                opacity: 0.6
            },
            {
                x: dates,
                y: sleepMA,
                name: '7-Day Average',
                type: 'scatter',
                mode: 'lines'
            }
        ], {
            ...BASE_LAYOUT,
            yaxis: { title: 'Sleep (hours)', linecolor: '#888', tickcolor: '#888' },
            xaxis: { ...makeXAxis(-30), linecolor: '#888', tickcolor: '#888' },
        }, PLOTLY_CONFIG);
    }
}

// -----------------------------
// Form handling (optional — only if form exists)
// -----------------------------
function wireEntryForm() {
    const form = document.getElementById('entryForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            date: document.getElementById('date')?.value,
            weight: parseFloat(document.getElementById('weight')?.value) || null,
            body_fat: parseFloat(document.getElementById('bodyFat')?.value) || null,
            calories: parseInt(document.getElementById('calories')?.value) || null,
            steps: parseInt(document.getElementById('steps')?.value) || null,
            sleep_total: parseFloat(document.getElementById('sleep')?.value) || null,
        };

        try {
            await fetchJson('/api/entries', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            alert('Entry added!');
            form.reset();
            await loadStats();
            await loadCharts();

            // Keep the current selected range if buttons exist
            // default to last 90
            if (document.getElementById('btn90')) setGlobalRange(90);
        } catch (err) {
            console.error(err);
            alert('Error adding entry');
        }
    });
}

// -----------------------------
// Global button wiring (optional — only if buttons exist)
// -----------------------------
function wireRangeButtons() {
    const btn30 = document.getElementById('btn30');
    const btn90 = document.getElementById('btn90');
    const btnAll = document.getElementById('btnAll');

    if (btn30) btn30.addEventListener('click', () => setGlobalRange(30));
    if (btn90) btn90.addEventListener('click', () => setGlobalRange(90));
    if (btnAll) btnAll.addEventListener('click', () => setGlobalRange(null));
}

// -----------------------------
// Init
// -----------------------------
document.addEventListener('DOMContentLoaded', async () => {
    wireEntryForm();
    wireRangeButtons();

    await loadStats();
    await loadCharts();

    // Default view if buttons exist
    if (document.getElementById('btn90')) {
        setGlobalRange(90);
    }
});
