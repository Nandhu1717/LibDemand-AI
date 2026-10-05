import os
import base64
import json
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as io

from data_processor import DatasetProcessor, EXPECTED_COLUMNS_INFO
from model import BookDemandModel
from data_generator import generate_library_dataset

# --------------------------------------------------
# STREAMLIT PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="LibDemand AI - Library Book Demand Prediction System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# BACKGROUND & THEMING (Glassmorphism CSS)
# --------------------------------------------------
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

bg_file_path = os.path.join(os.path.dirname(__file__), "library_bg.jpg")
bg_base64 = get_base64_of_bin_file(bg_file_path)

if bg_base64:
    bg_style = f"""
    .stApp {{
        background: linear-gradient(rgba(15, 23, 42, 0.65), rgba(15, 23, 42, 0.70)), url("data:image/jpg;base64,{bg_base64}");
        background-size: cover;
        background-position: center center;
        background-attachment: fixed;
    }}
    """
else:
    bg_style = """
    .stApp {
        background-color: #0F172A;
    }
    """

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #F8FAFC;
    }}
    
    {bg_style}

    /* Glassmorphism Cards */
    .glass-card {{
        background: rgba(30, 41, 59, 0.78);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
    }}

    .app-header {{
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(18px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-left: 6px solid #3B82F6;
        padding: 1.8rem 2.2rem;
        border-radius: 18px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
        margin-bottom: 2rem;
    }}

    .app-header h1 {{
        color: #FFFFFF;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0 0 0.4rem 0;
        letter-spacing: -0.02em;
    }}

    .app-header p {{
        color: #94A3B8;
        font-size: 1.05rem;
        margin: 0;
        font-weight: 500;
    }}

    /* Metric Cards */
    .metric-card {{
        background: rgba(30, 41, 59, 0.82);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        position: relative;
        overflow: hidden;
    }}

    .metric-card::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 4px;
    }}

    .metric-card.navy::before {{ background: #3B82F6; }}
    .metric-card.amber::before {{ background: #F59E0B; }}
    .metric-card.indigo::before {{ background: #6366F1; }}
    .metric-card.emerald::before {{ background: #10B981; }}

    .metric-label {{
        font-size: 0.8rem;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.3rem;
    }}

    .metric-val {{
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF;
    }}

    /* Badges */
    .badge {{
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.95rem;
    }}
    .badge-high {{ background-color: rgba(239, 68, 68, 0.25); color: #FCA5A5; border: 1px solid #EF4444; }}
    .badge-medium {{ background-color: rgba(245, 158, 11, 0.25); color: #FDE68A; border: 1px solid #F59E0B; }}
    .badge-low {{ background-color: rgba(16, 185, 129, 0.25); color: #6EE7B7; border: 1px solid #10B981; }}

    /* Streamlit Tabs */
    button[data-baseweb="tab"] {{
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        color: #94A3B8 !important;
        padding: 0.75rem 1.25rem !important;
    }}

    button[aria-selected="true"] {{
        color: #60A5FA !important;
        border-bottom-color: #60A5FA !important;
    }}

    /* Notice Banner */
    .demo-notice {{
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #FCD34D;
        padding: 0.75rem 1.2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: rgba(15, 23, 42, 0.92) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------
if 'processor' not in st.session_state:
    st.session_state.processor = DatasetProcessor()

if 'model' not in st.session_state:
    st.session_state.model = BookDemandModel()

if 'active_dataset_type' not in st.session_state:
    st.session_state.active_dataset_type = "demo"

if 'column_mapping' not in st.session_state:
    st.session_state.column_mapping = {}

if 'cleaned_df' not in st.session_state:
    st.session_state.cleaned_df = None

if 'audit_log' not in st.session_state:
    st.session_state.audit_log = None

# --------------------------------------------------
# INITIAL DATA INITIALIZATION (Load Demo Dataset by Default)
# --------------------------------------------------
def load_default_demo_dataset():
    sample_csv_path = os.path.join(os.path.dirname(__file__), "library_books_dataset.csv")
    if not os.path.exists(sample_csv_path):
        df_gen = generate_library_dataset(num_samples=600)
        df_gen.to_csv(sample_csv_path, index=False)
    
    st.session_state.processor.load_file(sample_csv_path, file_type='csv')
    st.session_state.column_mapping = st.session_state.processor.column_mapping
    cleaned_df, audit = st.session_state.processor.validate_and_clean(st.session_state.column_mapping, is_training=True)
    st.session_state.cleaned_df = cleaned_df
    st.session_state.audit_log = audit
    st.session_state.active_dataset_type = "demo"

if st.session_state.cleaned_df is None:
    load_default_demo_dataset()

# Auto-train model if dataset is ready and model not trained yet
if st.session_state.cleaned_df is not None and not st.session_state.model.is_trained:
    try:
        st.session_state.model.fit_and_evaluate(st.session_state.cleaned_df)
    except Exception as e:
        pass

# --------------------------------------------------
# HEADER BANNER
# --------------------------------------------------
st.markdown("""
<div class="app-header">
    <h1>📚 LibDemand AI: AI-Based Library Book Demand Prediction</h1>
    <p>Predict future library circulation demand using historical borrowing patterns & Random Forest Regression</p>
</div>
""", unsafe_allow_html=True)

# Notice banner for Demo Data
if st.session_state.active_dataset_type == "demo":
    st.markdown("""
    <div class="demo-notice">
        ℹ️ <strong>DEMONSTRATION SYNTHETIC DATASET ACTIVE:</strong> You are currently viewing synthetic sample data generated for demonstration purposes. Upload your institution's CSV/Excel circulation dataset in the Data Ingestion tab for operational predictions.
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR CONTROLS
# --------------------------------------------------
st.sidebar.title("⚙️ LibDemand AI Settings")

# Dataset Source Option
data_source = st.sidebar.radio(
    "📂 Data Source Mode",
    ["Demonstration Synthetic Dataset", "Upload Custom CSV/Excel File"],
    index=0 if st.session_state.active_dataset_type == "demo" else 1
)

if data_source == "Demonstration Synthetic Dataset" and st.session_state.active_dataset_type != "demo":
    load_default_demo_dataset()
    st.rerun()

# Model Hyperparameter Accordion
with st.sidebar.expander("🛠️ ML Model Settings", expanded=False):
    test_size_val = st.slider("Test Split Ratio (%)", min_value=10, max_value=40, value=20, step=5) / 100.0
    n_estimators_val = st.slider("Random Forest Trees (Estimators)", min_value=20, max_value=300, value=100, step=20)
    max_depth_val = st.slider("Max Tree Depth", min_value=3, max_value=30, value=12, step=1)
    
    if st.button("Apply Settings & Retrain Model"):
        st.session_state.model.n_estimators = n_estimators_val
        st.session_state.model.max_depth = max_depth_val
        if st.session_state.cleaned_df is not None:
            st.session_state.model.fit_and_evaluate(st.session_state.cleaned_df, test_size=test_size_val)
            st.sidebar.success("Model retrained successfully!")

# Demand Classification Thresholds Accordion
with st.sidebar.expander("🏷️ Demand Category Thresholds", expanded=False):
    threshold_mode = st.radio("Threshold Mode", ["Dynamic Quantiles (Data-driven)", "Custom Static Cutoffs"])
    
    if threshold_mode == "Custom Static Cutoffs":
        c_low = st.number_input("Low/Medium Cutoff (Books)", min_value=10, max_value=300, value=80)
        c_high = st.number_input("Medium/High Cutoff (Books)", min_value=50, max_value=600, value=160)
        if st.button("Update Custom Thresholds"):
            if st.session_state.cleaned_df is not None:
                st.session_state.model.fit_and_evaluate(
                    st.session_state.cleaned_df,
                    threshold_mode="custom",
                    custom_low=c_low,
                    custom_high=c_high
                )
                st.sidebar.success("Updated custom thresholds!")

# --------------------------------------------------
# MAIN TAB NAVIGATION
# --------------------------------------------------
tab_data, tab_model, tab_predict, tab_analytics, tab_guide = st.tabs([
    "📥 1. Data Ingestion & Prep",
    "🤖 2. Model Training & Evaluation",
    "🔮 3. Demand Predictor",
    "📊 4. Inventory Analytics",
    "📖 5. Librarian User Guide"
])

# ==================================================
# TAB 1: DATA INGESTION & PREPARATION
# ==================================================
with tab_data:
    st.subheader("📥 Dataset Loading & Cleaning Management")
    st.write("Upload your library's historical circulation records (CSV or Excel) or inspect the current demonstration dataset.")

    col_up1, col_up2 = st.columns([2, 1])
    
    with col_up1:
        uploaded_file = st.file_uploader(
            "Upload Library Dataset (.csv, .xlsx, .xls)",
            type=["csv", "xlsx", "xls"],
            help="Select a circulation dataset containing book categories, student numbers, past borrowing counts, and demand."
        )
        if uploaded_file is not None:
            file_ext = uploaded_file.name.split('.')[-1]
            try:
                st.session_state.processor.load_file(uploaded_file, file_type=file_ext)
                st.session_state.column_mapping = st.session_state.processor.column_mapping
                st.session_state.active_dataset_type = "custom"
                st.success(f"Successfully loaded uploaded file: `{uploaded_file.name}` ({st.session_state.processor.audit_log['original_rows']} rows)")
            except Exception as e:
                st.error(f"Error loading uploaded file: {str(e)}")

    with col_up2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Reset to Demo Dataset"):
            load_default_demo_dataset()
            st.success("Loaded synthetic demonstration dataset.")
            st.rerun()

    # Column Expectations Guide
    with st.expander("📖 Expected Columns & Schema Guide for Librarians", expanded=False):
        st.markdown("LibDemand AI relies on historical circulation indicators to forecast future demand:")
        schema_data = []
        for std_col, info in EXPECTED_COLUMNS_INFO.items():
            schema_data.append({
                "Standard Column Name": std_col,
                "Display Label": info['display_name'],
                "Data Type": info['type'],
                "Required": "Required for Training" if info['required'] else "Optional (Target)",
                "Description": info['description']
            })
        st.dataframe(pd.DataFrame(schema_data), use_container_width=True)

    # Column Mapping Interface
    if st.session_state.processor.raw_df is not None:
        st.markdown("---")
        st.subheader("🔗 Column Mapping Configuration")
        st.caption("Verify or adjust how your file's columns map to the application's required features:")
        
        raw_cols = ["-- Unmapped --"] + st.session_state.processor.raw_df.columns.tolist()
        new_mapping = {}
        
        map_cols = st.columns(3)
        i = 0
        for std_col, info in EXPECTED_COLUMNS_INFO.items():
            with map_cols[i % 3]:
                suggested = st.session_state.column_mapping.get(std_col)
                default_idx = raw_cols.index(suggested) if suggested in raw_cols else 0
                selected_col = st.selectbox(
                    f"{info['display_name']} (`{std_col}`)",
                    options=raw_cols,
                    index=default_idx,
                    key=f"map_{std_col}"
                )
                if selected_col != "-- Unmapped --":
                    new_mapping[std_col] = selected_col
                else:
                    new_mapping[std_col] = None
            i += 1
            
        if st.button("✅ Apply Column Mapping & Clean Dataset"):
            st.session_state.column_mapping = new_mapping
            cleaned_df, audit = st.session_state.processor.validate_and_clean(new_mapping, is_training=True)
            st.session_state.cleaned_df = cleaned_df
            st.session_state.audit_log = audit
            if audit['status'] == 'Valid & Cleaned':
                st.session_state.model.fit_and_evaluate(cleaned_df)
                st.success("Dataset successfully validated, cleaned, and ML model updated!")
                st.rerun()

    # Data Cleaning & Preparation Audit Summary
    if st.session_state.audit_log:
        st.markdown("---")
        st.subheader("🧹 Data Cleaning Audit & Quality Report")
        audit = st.session_state.audit_log
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Original Rows", audit.get('original_rows', 0))
        m2.metric("Retained Clean Rows", audit.get('retained_rows', 0))
        m3.metric("Dropped Rows", audit.get('dropped_rows', 0))
        m4.metric("Imputed Nulls", audit.get('missing_filled', 0))
        
        if audit.get('errors'):
            for err in audit['errors']:
                st.error(f"❌ {err}")
                
        if audit.get('warnings'):
            for warn in audit['warnings']:
                st.warning(f"⚠️ {warn}")
                
        if audit.get('actions'):
            with st.expander("📋 View Detailed Data Cleaning Log", expanded=False):
                for act in audit['actions']:
                    st.write(f"• {act}")

    # Dataset Preview Table
    if st.session_state.cleaned_df is not None and not st.session_state.cleaned_df.empty:
        st.markdown("---")
        st.subheader("📋 Active Cleaned Dataset Explorer")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cats = ["All Categories"] + sorted(st.session_state.cleaned_df['book_category'].unique().tolist())
            selected_cat_filter = st.selectbox("Filter by Category", cats)
        with col_f2:
            search_query = st.text_input("Search dataset (e.g., month number)")
            
        view_df = st.session_state.cleaned_df.copy()
        if selected_cat_filter != "All Categories":
            view_df = view_df[view_df['book_category'] == selected_cat_filter]
            
        st.dataframe(view_df.head(100), use_container_width=True)
        st.caption(f"Showing top rows ({len(view_df)} total records).")


# ==================================================
# TAB 2: MODEL TRAINING & EVALUATION
# ==================================================
with tab_model:
    st.subheader("🤖 Machine Learning Model Diagnostics & Performance Evaluation")
    st.write("Train and evaluate the Random Forest Regressor using a 80/20 train-test split to ensure unbiased accuracy measurement.")

    if st.session_state.cleaned_df is None or st.session_state.cleaned_df.empty:
        st.warning("Please load and clean a valid dataset in Tab 1 before evaluating the model.")
    else:
        if st.button("🚀 Retrain Random Forest Model Now", type="primary"):
            metrics = st.session_state.model.fit_and_evaluate(st.session_state.cleaned_df)
            st.success("Random Forest model trained successfully!")

        model_ref = st.session_state.model
        
        if model_ref.is_trained:
            m = model_ref.metrics
            
            # Key Performance Indicators Cards
            st.markdown("### 📊 Model Evaluation Metrics")
            k1, k2, k3, k4 = st.columns(4)
            
            with k1:
                st.markdown(f"""
                <div class="metric-card navy">
                    <div class="metric-label">Mean Absolute Error (MAE)</div>
                    <div class="metric-val">±{m['mae']} <span style="font-size: 0.9rem; color: #94A3B8;">books</span></div>
                </div>
                """, unsafe_allow_html=True)
                st.caption("Average error per prediction. Lower is better.")

            with k2:
                st.markdown(f"""
                <div class="metric-card amber">
                    <div class="metric-label">Root Mean Squared Error (RMSE)</div>
                    <div class="metric-val">{m['rmse']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.caption("Measures larger error penalties. Lower is better.")

            with k3:
                st.markdown(f"""
                <div class="metric-card emerald">
                    <div class="metric-label">R² Score (Accuracy)</div>
                    <div class="metric-val">{m['r2']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.caption("Variance explained (0.0 to 1.0). Higher is better.")

            with k4:
                st.markdown(f"""
                <div class="metric-card indigo">
                    <div class="metric-label">Test Set Samples</div>
                    <div class="metric-val">{m['test_size']} <span style="font-size: 0.9rem; color: #94A3B8;">/ {m['total_samples']}</span></div>
                </div>
                """, unsafe_allow_html=True)
                st.caption("20% held-out test evaluation sample.")

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Diagnostic Visualizations
            st.subheader("📈 Diagnostic Performance Visualizations")
            col_chart1, col_chart2 = st.columns(2)

            # Scatter Plot: Actual vs Predicted Demand
            with col_chart1:
                if model_ref.test_predictions_df is not None:
                    fig_scatter = px.scatter(
                        model_ref.test_predictions_df,
                        x="Actual_Demand",
                        y="Predicted_Demand",
                        labels={"Actual_Demand": "Actual Demand (Books)", "Predicted_Demand": "Model Predicted Demand (Books)"},
                        title="Actual vs. Predicted Demand (Held-out Test Set)",
                        color_discrete_sequence=["#60A5FA"]
                    )
                    min_val = min(model_ref.test_predictions_df['Actual_Demand'].min(), model_ref.test_predictions_df['Predicted_Demand'].min())
                    max_val = max(model_ref.test_predictions_df['Actual_Demand'].max(), model_ref.test_predictions_df['Predicted_Demand'].max())
                    fig_scatter.add_shape(
                        type="line", line=dict(dash="dash", color="#EF4444", width=2),
                        x0=min_val, y0=min_val, x1=max_val, y1=max_val
                    )
                    fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(30,41,59,0.5)", font_color="#F8FAFC")
                    st.plotly_chart(fig_scatter, use_container_width=True)

            # Feature Importance Bar Chart
            with col_chart2:
                if model_ref.feature_importances_df is not None:
                    fig_imp = px.bar(
                        model_ref.feature_importances_df.head(10),
                        x="Importance",
                        y="Feature",
                        orientation="h",
                        title="Top Drivers of Book Demand (Feature Importances)",
                        color="Importance",
                        color_continuous_scale="Viridis"
                    )
                    fig_imp.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(30,41,59,0.5)",
                        font_color="#F8FAFC",
                        yaxis=dict(autorange="reversed")
                    )
                    st.plotly_chart(fig_imp, use_container_width=True)

            # Model Export Section
            st.markdown("---")
            st.subheader("📥 Export Model Metrics & Diagnostic Results")
            
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                metrics_json = json.dumps(m, indent=2)
                st.download_button(
                    "📥 Download Evaluation Metrics (JSON)",
                    data=metrics_json,
                    file_name="libdemand_model_evaluation_metrics.json",
                    mime="application/json"
                )
            with exp_col2:
                if model_ref.test_predictions_df is not None:
                    csv_data = model_ref.test_predictions_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download Test Set Predictions (CSV)",
                        data=csv_data,
                        file_name="test_set_predictions.csv",
                        mime="text/csv"
                    )


# ==================================================
# TAB 3: DEMAND PREDICTOR (SINGLE & BATCH)
# ==================================================
with tab_predict:
    st.subheader("🔮 LibDemand AI Demand Predictor")
    st.write("Generate real-time predictions for single book titles or run batch predictions across uploaded inventory spreadsheets.")

    pred_tab1, pred_tab2 = st.tabs(["📖 Single Book Prediction", "📂 Batch Dataset Prediction"])

    # --- Sub-tab 1: Single Book Prediction ---
    with pred_tab1:
        if not st.session_state.model.is_trained:
            st.warning("Please train the Machine Learning model in Tab 2 first.")
        else:
            categories_list = sorted(st.session_state.cleaned_df['book_category'].unique().tolist())
            
            col_in1, col_in2, col_in3 = st.columns(3)
            with col_in1:
                input_category = st.selectbox("📖 Select Book Category / Subject", categories_list, index=0)
                input_month = st.selectbox(
                    "📅 Target Month",
                    options=list(range(1, 13)),
                    format_func=lambda x: f"Month {x} ({['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][x-1]})"
                )
            with col_in2:
                input_semester = st.slider("🎓 Academic Semester (1 to 8)", 1, 8, 4)
                input_students = st.number_input("👥 Enrolled Students Headcount", min_value=10, max_value=2000, value=250, step=10)
            with col_in3:
                input_borrowings = st.number_input("📕 Previous Borrowing Count", min_value=0, max_value=1000, value=75, step=5)
                input_prev_demand = st.number_input("📊 Previous Demand Count", min_value=0, max_value=1000, value=85, step=5)

            if st.button("🔮 Calculate Predicted Demand", type="primary"):
                result = st.session_state.model.predict_single(
                    book_category=input_category,
                    month=input_month,
                    semester=input_semester,
                    number_of_students=input_students,
                    previous_borrowing_count=input_borrowings,
                    previous_demand=input_prev_demand
                )

                st.markdown("---")
                st.subheader("📈 Demand Forecast & Planning Results")

                res_col1, res_col2, res_col3 = st.columns(3)
                
                with res_col1:
                    st.markdown(f"""
                    <div class="metric-card navy">
                        <div class="metric-label">Predicted Demand</div>
                        <div class="metric-val">{result['predicted_demand']} <span style="font-size: 1rem; color: #94A3B8;">books</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                with res_col2:
                    badge_class = f"badge-{result['demand_level'].lower()}"
                    st.markdown(f"""
                    <div class="metric-card amber">
                        <div class="metric-label">Demand Classification</div>
                        <div class="metric-val"><span class="badge {badge_class}">{result['demand_level']} Demand</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                with res_col3:
                    st.markdown(f"""
                    <div class="metric-card indigo">
                        <div class="metric-label">Threshold Explanation</div>
                        <div style="color: #CBD5E1; font-size: 0.85rem; font-weight: 500; margin-top: 0.2rem;">
                            {result['threshold_explanation']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Recommendation Box
                rec = result['recommendation']
                st.markdown(f"""
                <div style="background: {rec['bg_color']}; border-left: 6px solid {rec['border_color']}; border-radius: 14px; padding: 1.5rem; margin-top: 1.5rem;">
                    <div style="color: {rec['text_color']}; font-weight: 800; font-size: 1.15rem; margin-bottom: 0.4rem;">
                        {rec['badge']} - {rec['title']}
                    </div>
                    <div style="color: #334155; font-size: 1rem; line-height: 1.6; font-weight: 500;">
                        {rec['detail']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # --- Sub-tab 2: Batch Dataset Prediction ---
    with pred_tab2:
        st.write("Upload an un-labeled spreadsheet (CSV/Excel) containing future course profiles to generate batch demand predictions.")
        
        batch_file = st.file_uploader("Upload Batch Prediction File (.csv, .xlsx)", type=["csv", "xlsx"], key="batch_upload")
        
        if batch_file is not None:
            try:
                batch_processor = DatasetProcessor()
                batch_processor.load_file(batch_file, file_type=batch_file.name.split('.')[-1])
                mapped_batch = batch_processor.suggest_column_mapping(batch_processor.raw_df.columns.tolist())
                
                cleaned_batch, audit_b = batch_processor.validate_and_clean(mapped_batch, is_training=False)
                
                if not cleaned_batch.empty:
                    batch_predictions = st.session_state.model.predict_batch(cleaned_batch)
                    st.success(f"Generated predictions for {len(batch_predictions)} rows!")
                    
                    st.dataframe(batch_predictions[['book_category', 'month', 'semester', 'number_of_students', 'Predicted_Demand', 'Demand_Level', 'Stock_Action']], use_container_width=True)
                    
                    csv_batch = batch_predictions.to_csv(index=False)
                    st.download_button(
                        "📥 Download Predicted Dataset CSV",
                        data=csv_batch,
                        file_name="predicted_libdemand_ai.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Could not validate columns in uploaded batch file. Please ensure expected features are included.")
            except Exception as e:
                st.error(f"Batch prediction error: {str(e)}")


# ==================================================
# TAB 4: INVENTORY ANALYTICS DASHBOARD
# ==================================================
with tab_analytics:
    st.subheader("📊 Visual Analytics & Inventory Dashboard")
    st.write("Explore overall trends, seasonal circulation peaks, and category distribution from historical data.")

    if st.session_state.cleaned_df is None or st.session_state.cleaned_df.empty:
        st.warning("Please load data in Tab 1 to view analytics.")
    else:
        df_analytics = st.session_state.cleaned_df.copy()

        # Filters Bar
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            cat_list = ["All Categories"] + sorted(df_analytics['book_category'].unique().tolist())
            dash_cat = st.selectbox("Filter Dashboard by Category", cat_list, key="dash_cat")
        with f_col2:
            dash_semester = st.multiselect("Filter by Semester", options=sorted(df_analytics['semester'].unique().tolist()), default=sorted(df_analytics['semester'].unique().tolist()))

        if dash_cat != "All Categories":
            df_analytics = df_analytics[df_analytics['book_category'] == dash_cat]
        if dash_semester:
            df_analytics = df_analytics[df_analytics['semester'].isin(dash_semester)]

        # Summary KPIs
        st.markdown("<br>", unsafe_allow_html=True)
        sk1, sk2, sk3, sk4 = st.columns(4)
        sk1.metric("Total Records Evaluated", len(df_analytics))
        sk2.metric("Average Demand / Category", f"{df_analytics['demand'].mean():.1f} books")
        sk3.metric("Peak Observed Demand", f"{df_analytics['demand'].max()} books")
        sk4.metric("Lowest Observed Demand", f"{df_analytics['demand'].min()} books")

        st.markdown("<br>", unsafe_allow_html=True)
        chart_row1_col1, chart_row1_col2 = st.columns(2)

        # 1. Monthly Demand Trend Line Chart
        with chart_row1_col1:
            monthly_agg = df_analytics.groupby('month')['demand'].mean().reset_index()
            month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            monthly_agg['Month_Name'] = monthly_agg['month'].apply(lambda m: month_names[m-1] if 1<=m<=12 else str(m))
            
            fig_month = px.line(
                monthly_agg,
                x='Month_Name',
                y='demand',
                markers=True,
                title="Monthly Demand Trend (Academic Seasonality)",
                labels={'Month_Name': 'Month', 'demand': 'Avg Book Demand'},
                color_discrete_sequence=["#3B82F6"]
            )
            fig_month.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(30,41,59,0.5)", font_color="#F8FAFC")
            st.plotly_chart(fig_month, use_container_width=True)

        # 2. Category Demand Comparison Bar Chart
        with chart_row1_col2:
            cat_agg = df_analytics.groupby('book_category')['demand'].mean().reset_index().sort_values(by='demand', ascending=True)
            fig_cat = px.bar(
                cat_agg,
                x='demand',
                y='book_category',
                orientation='h',
                title="Average Demand by Book Category",
                labels={'book_category': 'Category', 'demand': 'Avg Demand'},
                color='demand',
                color_continuous_scale='Blues'
            )
            fig_cat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(30,41,59,0.5)", font_color="#F8FAFC")
            st.plotly_chart(fig_cat, use_container_width=True)

        chart_row2_col1, chart_row2_col2 = st.columns(2)

        # 3. Demand Level Donut Distribution
        with chart_row2_col1:
            if st.session_state.model.is_trained:
                df_analytics['Level'] = df_analytics['demand'].apply(st.session_state.model.classify_demand)
                level_counts = df_analytics['Level'].value_counts().reset_index()
                level_counts.columns = ['Demand_Level', 'Count']
                
                fig_donut = px.pie(
                    level_counts,
                    names='Demand_Level',
                    values='Count',
                    hole=0.45,
                    title="Demand Level Distribution (Low / Medium / High)",
                    color='Demand_Level',
                    color_discrete_map={'Low': '#10B981', 'Medium': '#F59E0B', 'High': '#EF4444'}
                )
                fig_donut.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC")
                st.plotly_chart(fig_donut, use_container_width=True)

        # 4. Enrolled Students vs Demand Scatter Plot
        with chart_row2_col2:
            fig_stud = px.scatter(
                df_analytics,
                x='number_of_students',
                y='demand',
                color='book_category',
                title="Enrolled Students Headcount vs. Book Demand",
                labels={'number_of_students': 'Enrolled Students', 'demand': 'Demand Count'},
                opacity=0.75
            )
            fig_stud.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(30,41,59,0.5)", font_color="#F8FAFC")
            st.plotly_chart(fig_stud, use_container_width=True)


# ==================================================
# TAB 5: LIBRARIAN USER GUIDE & DOCUMENTATION
# ==================================================
with tab_guide:
    st.subheader("📖 LibDemand AI: User Guide & System Documentation")
    
    st.markdown("""
    ### 📌 Project Overview
    **LibDemand AI** addresses the challenge of library inventory management by replacing manual, retrospective estimation with a Machine Learning-based forecasting engine. Libraries need to keep enough copies of popular books available while avoiding the accumulation of resources that few students borrow. 
    
    By analyzing factors such as **book category, month, semester, number of students, previous borrowing count, and previous demand**, LibDemand AI uses **Random Forest Regression** to learn borrowing patterns, measure prediction accuracy via **MAE** and **R² score**, and present actionable **Low, Medium, or High** demand recommendations.

    ---

    ### 🚀 4-Step Operational Workflow

    1. **Upload or Verify Circulation Dataset (Tab 1)**
       - Upload your institution's historical circulation records as a CSV or Excel file.
       - Use the **Column Mapping Configuration** if your spreadsheet uses non-standard column headers.
       - Review the **Data Cleaning Audit Report** to inspect auto-filled missing values or removed duplicate entries.

    2. **Train & Evaluate the Random Forest Model (Tab 2)**
       - Click **Retrain Model** to fit the Machine Learning pipeline on 80% of your data while holding out 20% for testing.
       - Review the evaluation metrics:
         - **MAE (Mean Absolute Error):** Indicates the average number of books the prediction might be off by.
         - **R² Score:** Indicates model reliability (e.g. 0.85 means 85% of borrowing variance is accurately explained).
       - Download evaluation reports for institutional reporting.

    3. **Generate Predictions & Recommendations (Tab 3)**
       - **Single Title Lookup:** Input target category, month, enrolled headcount, and past borrowing figures to receive instant stock recommendations (**High**, **Medium**, or **Low** priority).
       - **Batch Forecast:** Upload next semester's course spreadsheet to generate predictions across all titles simultaneously and download a ready-to-use ordering CSV.

    4. **Analyze Seasonal Trends (Tab 4)**
       - View mid-term and examination circulation peaks to schedule reserve collections ahead of time.

    ---

    ### 📊 Expected Input Data Fields

    - **Book Category / Subject (`book_category`):** Major discipline (e.g., Computer Science, Engineering, History).
    - **Month of Academic Year (`month`):** Integer (1=January through 12=December). Captures exam peaks in May and December.
    - **Academic Semester (`semester`):** Integer (1 to 8).
    - **Enrolled Students Headcount (`number_of_students`):** Total student enrollment in courses using books in this subject.
    - **Previous Borrowing Count (`previous_borrowing_count`):** Checkout volume during the preceding monthly cycle.
    - **Previous Demand Count (`previous_demand`):** Total requested demand (including hold queues) in the prior cycle.

    ---

    ### 🏷️ Demand Classification & Thresholds

    To ensure transparent decision-making, thresholds are calculated dynamically using **Data-driven Percentile Quantiles**:
    - **Low Demand:** Predictions below the 33rd percentile of historical demand. Recommendation: Maintain current shelf stock; avoid ordering unnecessary duplicates.
    - **Medium Demand:** Predictions between the 33rd and 66th percentiles. Recommendation: Monitor borrowing frequency; ensure reference desk reserve is populated.
    - **High Demand:** Predictions above the 66th percentile. Recommendation: **Priority Reorder** with book suppliers; activate short-term borrowing reserves and digital copy licenses.

    ---

    ### 🔮 Future System Roadmap
    - **Individual Book-Level Prediction:** Fine-tuning from subject category level down to individual ISBNs.
    - **Real-Time Library Systems Integration:** Direct API connectors to ILS (Integrated Library Systems) like Koha or Alma.
    - **Automated Stock Alerts:** Automated email notifications when high-demand thresholds are crossed.
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.85rem; margin-top: 1.5rem; padding-bottom: 1rem;">
    LibDemand AI • AI-Based Library Book Demand Prediction System • Streamlit & Scikit-Learn
</div>
""", unsafe_allow_html=True)
