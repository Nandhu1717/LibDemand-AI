/* ==========================================================================
   LibDemand AI - Client-Side Interactive Engine & Visualizations
   ========================================================================== */

// Sample Circulation Dataset
const categories = [
    'Computer Science', 'Engineering', 'Medical', 'Business',
    'Mathematics', 'Physics', 'Literature', 'History'
];

const categoryWeights = {
    'Computer Science': 1.35,
    'Engineering': 1.25,
    'Medical': 1.20,
    'Business': 1.10,
    'Mathematics': 1.05,
    'Physics': 0.95,
    'Literature': 0.85,
    'History': 0.75
};

let dataset = [];
let charts = {};

// Initialize application data
document.addEventListener('DOMContentLoaded', () => {
    generateSampleDataset();
    renderTable();
    initCharts();
    // Run initial default prediction
    document.getElementById('prediction-form').dispatchEvent(new Event('submit'));
});

// Tab Switcher
function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    event.currentTarget.classList.add('active');
    document.getElementById(tabId).classList.add('active');

    // Trigger chart resize if switching to analytics
    if (tabId === 'tab-analytics') {
        Object.values(charts).forEach(chart => chart.resize());
    }
}

// Generate Realistic Sample Dataset (600 rows)
function generateSampleDataset() {
    dataset = [];
    for (let i = 0; i < 600; i++) {
        const cat = categories[Math.floor(Math.random() * categories.length)];
        const month = Math.floor(Math.random() * 12) + 1;
        const semester = Math.floor(Math.random() * 8) + 1;
        const students = Math.floor(Math.random() * 450) + 50;
        const borrowing = Math.max(10, Math.floor(students * 0.4 + (Math.random() * 70 - 35)));
        const prevDemand = Math.max(15, Math.floor(borrowing + (Math.random() * 40 - 15)));

        const catMult = categoryWeights[cat];
        let seasonMult = 1.0;
        if ([5, 12].includes(month)) seasonMult = 1.30;
        else if ([3, 4, 10, 11].includes(month)) seasonMult = 1.15;
        else if ([6, 7].includes(month)) seasonMult = 0.65;

        const calcDemand = (0.35 * borrowing + 0.35 * prevDemand + 0.20 * (students * 0.5) + (Math.random() * 30 - 15)) * catMult * seasonMult;
        const demand = Math.max(15, Math.round(calcDemand));

        dataset.push({
            id: i + 1,
            category: cat,
            month: month,
            semester: semester,
            students: students,
            borrowing: borrowing,
            prevDemand: prevDemand,
            demand: demand
        });
    }
}

// Render Dataset Table
function renderTable() {
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '';

    const displayRows = dataset.slice(0, 50); // Top 50 rows
    displayRows.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>#${row.id}</td>
            <td><strong>${row.category}</strong></td>
            <td>Month ${row.month}</td>
            <td>Semester ${row.semester}</td>
            <td>${row.students} students</td>
            <td>${row.borrowing} checkouts</td>
            <td>${row.prevDemand}</td>
            <td><strong style="color: var(--accent-blue);">${row.demand} books</strong></td>
        `;
        tbody.appendChild(tr);
    });
}

// Table Search Filter
function filterTable() {
    const query = document.getElementById('table-search').value.toLowerCase();
    const rows = document.querySelectorAll('#table-body tr');

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
    });
}

// LibDemand AI Single Prediction Calculation
function calculatePrediction(e) {
    if (e) e.preventDefault();

    const category = document.getElementById('category-select').value;
    const month = parseInt(document.getElementById('month-select').value);
    const semester = parseInt(document.getElementById('semester-input').value);
    const students = parseInt(document.getElementById('students-input').value);
    const borrowing = parseInt(document.getElementById('borrowing-input').value);
    const prevDemand = parseInt(document.getElementById('prev-demand-input').value);

    const catMult = categoryWeights[category] || 1.0;
    let seasonMult = 1.0;
    if ([5, 12].includes(month)) seasonMult = 1.30;
    else if ([3, 4, 10, 11].includes(month)) seasonMult = 1.15;
    else if ([6, 7].includes(month)) seasonMult = 0.65;

    const rawDemand = (0.35 * borrowing + 0.35 * prevDemand + 0.20 * (students * 0.5)) * catMult * seasonMult;
    const predictedDemand = Math.max(10, Math.round(rawDemand));

    // Determine Demand Level
    let level = "Medium";
    let badgeClass = "badge-medium";
    let thresholdText = "Medium Demand (85 – 160 books)";
    let recBoxClass = "rec-box medium";
    let recTitle = "⚠️ MEDIUM PRIORITY - Monitor Borrowing Frequency";
    let recDetail = "Moderate demand expected. Keep standard shelf stock, monitor weekly borrowing trends, and ensure reference desk reserve is ready.";

    if (predictedDemand > 160) {
        level = "High";
        badgeClass = "badge-high";
        thresholdText = "Above 66th percentile (> 160 books)";
        recBoxClass = "rec-box high";
        recTitle = "🚨 HIGH DEMAND PRIORITY - Reorder & Restock Urgently";
        recDetail = "High demand anticipated! Increase physical shelf copies, place priority reorders with suppliers, and activate short-term digital borrowing reserves.";
    } else if (predictedDemand < 85) {
        level = "Low";
        badgeClass = "badge-low";
        thresholdText = "Below 33rd percentile (< 85 books)";
        recBoxClass = "rec-box low";
        recTitle = "🌱 OPTIMAL INVENTORY - Sufficient Shelf Copies";
        recDetail = "Low demand expected. Current inventory is sufficient. Avoid ordering excess shelf inventory and reallocate unused shelf space.";
    }

    // Update UI elements
    document.getElementById('res-demand-val').innerText = predictedDemand;
    
    const badgeEl = document.getElementById('res-badge');
    badgeEl.className = `badge ${badgeClass}`;
    badgeEl.innerText = `${level} Demand`;

    document.getElementById('res-threshold-text').innerText = thresholdText;

    const recContainer = document.getElementById('rec-box-container');
    recContainer.className = recBoxClass;
    document.getElementById('rec-title').innerText = recTitle;
    document.getElementById('rec-detail').innerText = recDetail;
}

// Initialize Chart.js Visualizations
function initCharts() {
    Chart.defaults.color = '#94A3B8';
    Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";

    // 1. Monthly Demand Trend Chart
    const monthlyData = Array(12).fill(0);
    const monthlyCounts = Array(12).fill(0);
    dataset.forEach(row => {
        monthlyData[row.month - 1] += row.demand;
        monthlyCounts[row.month - 1]++;
    });
    const monthlyAvg = monthlyData.map((sum, i) => Math.round(sum / (monthlyCounts[i] || 1)));

    const ctx1 = document.getElementById('monthlyChart').getContext('2d');
    charts.monthly = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May (Exams)', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec (Exams)'],
            datasets: [{
                label: 'Avg Book Demand',
                data: monthlyAvg,
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59, 130, 246, 0.15)',
                fill: true,
                tension: 0.35,
                pointRadius: 5,
                pointBackgroundColor: '#60A5FA'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.08)' } },
                x: { grid: { display: false } }
            }
        }
    });

    // 2. Category Demand Comparison Bar Chart
    const catData = {};
    const catCounts = {};
    categories.forEach(c => { catData[c] = 0; catCounts[c] = 0; });
    dataset.forEach(row => {
        catData[row.category] += row.demand;
        catCounts[row.category]++;
    });
    const catAvg = categories.map(c => Math.round(catData[c] / (catCounts[c] || 1)));

    const ctx2 = document.getElementById('categoryChart').getContext('2d');
    charts.category = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [{
                label: 'Avg Demand',
                data: catAvg,
                backgroundColor: 'rgba(99, 102, 241, 0.75)',
                borderColor: '#6366F1',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.08)' } },
                x: { grid: { display: false } }
            }
        }
    });

    // 3. Demand Level Donut Distribution Chart
    let lowCount = 0, medCount = 0, highCount = 0;
    dataset.forEach(row => {
        if (row.demand < 85) lowCount++;
        else if (row.demand <= 160) medCount++;
        else highCount++;
    });

    const ctx3 = document.getElementById('donutChart').getContext('2d');
    charts.donut = new Chart(ctx3, {
        type: 'doughnut',
        data: {
            labels: ['Low Demand (< 85)', 'Medium Demand (85-160)', 'High Demand (> 160)'],
            datasets: [{
                data: [lowCount, medCount, highCount],
                backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });

    // 4. Feature Importance Horizontal Bar Chart
    const ctx4 = document.getElementById('importanceChart').getContext('2d');
    charts.importance = new Chart(ctx4, {
        type: 'bar',
        data: {
            labels: ['Past Borrowings', 'Past Demand Score', 'Enrolled Students', 'Academic Month', 'Subject Category', 'Semester'],
            datasets: [{
                label: 'Feature Importance',
                data: [0.38, 0.32, 0.16, 0.08, 0.04, 0.02],
                backgroundColor: 'rgba(16, 185, 129, 0.75)',
                borderColor: '#10B981',
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.08)' } },
                y: { grid: { display: false } }
            }
        }
    });
}

// Batch Prediction CSV Downloader
function runBatchPrediction() {
    let csvContent = "data:text/csv;charset=utf-8,ID,Book_Category,Month,Semester,Students,Past_Borrowings,Past_Demand,Predicted_Demand,Demand_Level,Stock_Action\n";

    dataset.forEach(row => {
        const catMult = categoryWeights[row.category] || 1.0;
        let seasonMult = 1.0;
        if ([5, 12].includes(row.month)) seasonMult = 1.30;
        else if ([3, 4, 10, 11].includes(row.month)) seasonMult = 1.15;
        else if ([6, 7].includes(row.month)) seasonMult = 0.65;

        const pred = Math.max(10, Math.round((0.35 * row.borrowing + 0.35 * row.prevDemand + 0.20 * (row.students * 0.5)) * catMult * seasonMult));
        let level = "Medium";
        let action = "Monitor Inventory";
        if (pred > 160) { level = "High"; action = "Priority Reorder & Restock"; }
        else if (pred < 85) { level = "Low"; action = "Sufficient Shelf Stock"; }

        csvContent += `${row.id},${row.category},${row.month},${row.semester},${row.students},${row.borrowing},${row.prevDemand},${pred},${level},"${action}"\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "libdemand_batch_predictions.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
