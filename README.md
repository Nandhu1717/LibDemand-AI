# LIBDEMAND AI: LIBRARY BOOK DEMAND PREDICTION SYSTEM 📚🤖

**A Machine Learning-Powered Library Demand Forecasting, Inventory Planning, and Analytics Dashboard for Academic Libraries.**

[![Live Website](https://img.shields.io/badge/Live%20Website-Open%20Now-brightgreen?style=for-the-badge&logo=github)](https://nandhu1717.github.io/LibDemand-AI/)
![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-Random%20Forest-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)

🌐 **Live Demo:** [https://nandhu1717.github.io/LibDemand-AI/](https://nandhu1717.github.io/LibDemand-AI/)

---

## 🌟 KEY HIGHLIGHTS & FEATURES

### 1. 📊 Interactive Demand Prediction
- **Smart Inputs:** Enter the book category, month, semester, student count, and borrowing details.
- **Instant Results:** View estimated book demand and inventory guidance.

### 2. 🤖 Machine Learning Dashboard
- **Easy Upload:** Upload historical library circulation data in CSV or Excel format.
- **Data Cleaning:** Clean and validate the dataset before model training.
- **Random Forest Model:** Train the model and review **MAE, RMSE, and R²** metrics.

### 3. 📈 Demand & Inventory Analytics
- **Trend Analysis:** Explore demand trends and category-wise comparisons.
- **Stock Planning:** Use prediction results to support library stock planning.

### 4. 📥 CSV Reports & Sample Data
- **Batch Reports:** Download batch prediction results as a CSV file.
- **Try Instantly:** Test the dashboard with the included sample dataset.

---

## 📁 PROJECT DIRECTORY STRUCTURE

```text
LibDemand-AI/
├── app.py                    # Streamlit dashboard
├── app.js                    # Browser page interactions and charts
├── index.html                # Interactive browser application
├── style.css                 # Web page styles
├── model.py                  # Random Forest prediction model
├── data_processor.py         # Dataset loading, cleaning, and validation
├── data_generator.py         # Sample data generator
├── library_books_dataset.csv # Sample library dataset
├── library_bg.jpg            # Background image
├── requirements.txt          # Python dependencies
├── .gitignore                # Files excluded from Git
└── README.md                 # Project documentation
```

---

## 🚀 QUICK START GUIDE (HOW TO RUN)

### 1. Launching the Browser Web Page

From the project folder, start a local web server:

```bash
python -m http.server 8080
```

Then open your browser at **[http://localhost:8080](http://localhost:8080)**.

🌐 Or open the published version directly: **[LibDemand AI Live Website](https://nandhu1717.github.io/LibDemand-AI/)**

### 2. Launching the Streamlit Dashboard

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Start the dashboard:

```bash
streamlit run app.py
```

Then open your browser at **[http://localhost:8501](http://localhost:8501)**.

> 📝 **Note:** GitHub Pages hosts only the browser application files. The Python Streamlit dashboard requires a separate Python hosting service.

### 3. Testing the Workflow Instantly

1. Open the **Live Website** or the Streamlit dashboard.
2. Select a **book category**, **month**, and **semester**.
3. Enter the **student count** and **borrowing details**.
4. Click predict and view the **estimated demand** and **inventory guidance**.
5. In the ML dashboard, upload [`library_books_dataset.csv`](library_books_dataset.csv), train the model, and check the **MAE, RMSE, and R²** scores.
6. Download the **batch prediction CSV report**.

---

## 🧠 MODEL INPUT & OUTPUT QUICK REFERENCE

> 💻 This is a **software-only project**, so no physical hardware or wiring is required.

| Type | Details | Notes |
|------|---------|-------|
| **Input** | Book category or subject | Example: Engineering, Science, Literature |
| **Input** | Month and academic semester | Captures seasonal demand |
| **Input** | Student enrollment | Total students using the library |
| **Input** | Previous borrowing / demand | Historical circulation data |
| **Output** | Estimated book demand | Predicted by Random Forest model |
| **Output** | Demand trends & category comparisons | Interactive charts |
| **Output** | Inventory planning guidance | Supports stock decisions |
| **Output** | Downloadable CSV reports | Batch prediction results |

---

## 📄 DOCUMENTATION LINKS

- 🌐 [LibDemand AI Live Website](https://nandhu1717.github.io/LibDemand-AI/)
- 📊 [Streamlit Dashboard](app.py)
- 🤖 [Prediction Model](model.py)
- 🧹 [Dataset Processor](data_processor.py)
- 🎲 [Sample Data Generator](data_generator.py)
- 🖥️ [Browser Application](index.html)
- 📦 [Python Dependencies](requirements.txt)
- 📚 [Sample Dataset](library_books_dataset.csv)

---

## 🛠️ TECH STACK

| Layer | Technology |
|-------|------------|
| Machine Learning | scikit-learn (Random Forest) |
| Data Processing | pandas, NumPy |
| Visualization | Plotly |
| Dashboard | Streamlit |
| Web Interface | HTML, CSS, JavaScript |

---

## 💡 LICENSE & ATTRIBUTION

No license file is currently included in this repository. Add a license file if you want to define how others may reuse or modify the project.

The project uses Python libraries listed in [`requirements.txt`](requirements.txt), including **Streamlit, pandas, NumPy, scikit-learn, and Plotly**.

The included `library_books_dataset.csv` is **sample data for demonstration**. ⚠️ Do not upload private student or library circulation records to a public repository.

Developed with ❤️ for smarter library management and better book availability for students.
