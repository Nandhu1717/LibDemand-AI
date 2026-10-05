import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List, Optional

EXPECTED_COLUMNS_INFO = {
    'book_category': {
        'display_name': 'Book Category / Subject',
        'type': 'Categorical (Text)',
        'description': 'Genre or discipline of the book (e.g., Computer Science, Engineering, History, Literature).',
        'required': True,
        'aliases': ['book_category', 'category', 'subject', 'genre', 'book category', 'subject_category', 'Category', 'Book_Category']
    },
    'month': {
        'display_name': 'Month of Academic Year',
        'type': 'Numeric (Integer 1-12)',
        'description': 'Month in which demand is measured (1 = Jan, 12 = Dec). Used to capture seasonality like exams and mid-terms.',
        'required': True,
        'aliases': ['month', 'Month', 'month_num', 'borrowing_month', 'Month_Num']
    },
    'semester': {
        'display_name': 'Academic Semester',
        'type': 'Numeric (Integer 1-8)',
        'description': 'Curriculum term / semester (1 through 8).',
        'required': True,
        'aliases': ['semester', 'Semester', 'term', 'academic_semester', 'Semester_Num']
    },
    'number_of_students': {
        'display_name': 'Enrolled Students Headcount',
        'type': 'Numeric (Integer > 0)',
        'description': 'Number of students enrolled in relevant courses/departments during the period.',
        'required': True,
        'aliases': ['number_of_students', 'students', 'enrolled_students', 'student_count', 'students_count', 'Students', 'Number_Of_Students', 'Headcount']
    },
    'previous_borrowing_count': {
        'display_name': 'Previous Borrowing Count',
        'type': 'Numeric (Integer >= 0)',
        'description': 'Total physical checkout count in the previous month/cycle for this category.',
        'required': True,
        'aliases': ['previous_borrowing_count', 'borrowing', 'past_borrowings', 'previous_borrowings', 'borrow_count', 'Borrowing', 'Previous_Borrowing_Count', 'Previous Borrowings']
    },
    'previous_demand': {
        'display_name': 'Previous Demand Count',
        'type': 'Numeric (Integer >= 0)',
        'description': 'Calculated or observed total demand score from the prior cycle.',
        'required': True,
        'aliases': ['previous_demand', 'past_demand', 'prior_demand', 'Previous_Demand', 'Previous Demand', 'Hist_Demand']
    },
    'demand': {
        'display_name': 'Future Demand (Target)',
        'type': 'Numeric (Integer >= 0)',
        'description': 'The target circulation demand to predict. (Required for Model Training; optional for Batch Prediction).',
        'required': False,  # Optional if performing batch prediction on un-labeled data
        'aliases': ['demand', 'future_demand', 'target_demand', 'actual_demand', 'Demand', 'Book_Demand']
    }
}


class DatasetProcessor:
    """
    Handles file loading, column mapping, data validation, cleaning, and summary generation
    for the Library Book Demand Prediction System.
    """

    def __init__(self):
        self.raw_df: Optional[pd.DataFrame] = None
        self.cleaned_df: Optional[pd.DataFrame] = None
        self.column_mapping: Dict[str, str] = {}
        self.audit_log: Dict[str, Any] = {
            'status': 'Unloaded',
            'original_rows': 0,
            'retained_rows': 0,
            'dropped_rows': 0,
            'missing_filled': 0,
            'duplicate_rows': 0,
            'actions': [],
            'warnings': [],
            'errors': []
        }

    def load_file(self, file_object_or_path, file_type: str = 'csv') -> pd.DataFrame:
        """Loads a dataset from CSV or Excel file."""
        self.audit_log = {
            'status': 'Processing',
            'original_rows': 0,
            'retained_rows': 0,
            'dropped_rows': 0,
            'missing_filled': 0,
            'duplicate_rows': 0,
            'actions': [],
            'warnings': [],
            'errors': []
        }
        
        try:
            if file_type.lower() in ['csv', '.csv']:
                self.raw_df = pd.read_csv(file_object_or_path)
            elif file_type.lower() in ['xlsx', 'xls', '.xlsx', '.xls']:
                self.raw_df = pd.read_excel(file_object_or_path)
            else:
                raise ValueError(f"Unsupported file format: {file_type}. Please upload a CSV or Excel file.")
                
            if self.raw_df.empty:
                raise ValueError("The uploaded dataset is empty. Please provide a file with data rows.")
                
            self.audit_log['original_rows'] = len(self.raw_df)
            self.audit_log['actions'].append(f"Loaded {len(self.raw_df)} rows and {len(self.raw_df.columns)} columns.")
            
            # Suggest column mappings
            self.column_mapping = self.suggest_column_mapping(self.raw_df.columns.tolist())
            return self.raw_df

        except Exception as e:
            self.audit_log['status'] = 'Error'
            self.audit_log['errors'].append(f"Failed to read file: {str(e)}")
            raise e

    @staticmethod
    def suggest_column_mapping(df_columns: List[str]) -> Dict[str, str]:
        """Auto-detects matching column names based on known aliases."""
        mapping = {}
        df_cols_lower = {col.lower().strip(): col for col in df_columns}
        
        for std_col, info in EXPECTED_COLUMNS_INFO.items():
            found = False
            for alias in info['aliases']:
                if alias.lower() in df_cols_lower:
                    mapping[std_col] = df_cols_lower[alias.lower()]
                    found = True
                    break
            if not found:
                mapping[std_col] = None  # Unmapped
        return mapping

    def validate_and_clean(self, mapping: Dict[str, str], is_training: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Validates mapped columns and cleans missing/invalid values.
        Returns cleaned DataFrame and detailed audit report.
        """
        if self.raw_df is None or self.raw_df.empty:
            raise ValueError("No dataset loaded. Please upload a dataset first.")

        df = self.raw_df.copy()
        missing_required = []

        # Check required features
        for std_col, info in EXPECTED_COLUMNS_INFO.items():
            if std_col == 'demand' and not is_training:
                continue # Target column is optional for batch inference
            
            user_col = mapping.get(std_col)
            if not user_col or user_col not in df.columns:
                missing_required.append(f"{info['display_name']} (`{std_col}`)")

        if missing_required:
            error_msg = f"Missing required column(s): {', '.join(missing_required)}. Please map these columns."
            self.audit_log['status'] = 'Invalid Columns'
            self.audit_log['errors'].append(error_msg)
            return pd.DataFrame(), self.audit_log

        # Rename user columns to standard schema
        reverse_map = {v: k for k, v in mapping.items() if v and k in EXPECTED_COLUMNS_INFO}
        df = df[list(reverse_map.keys())].rename(columns=reverse_map)

        # 1. Deduplication
        initial_count = len(df)
        df = df.drop_duplicates()
        dups_removed = initial_count - len(df)
        if dups_removed > 0:
            self.audit_log['duplicate_rows'] = dups_removed
            self.audit_log['actions'].append(f"Removed {dups_removed} duplicate row(s).")

        # 2. Type conversions & missing value handling
        num_cols = ['month', 'semester', 'number_of_students', 'previous_borrowing_count', 'previous_demand']
        if is_training and 'demand' in df.columns:
            num_cols.append('demand')

        # Convert numerical columns
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Handle missing numerical values (Impute with median)
        missing_filled_count = 0
        for col in num_cols:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                median_val = df[col].median()
                if pd.isna(median_val):
                    median_val = 0
                df[col] = df[col].fillna(median_val)
                missing_filled_count += null_count
                self.audit_log['actions'].append(f"Imputed {null_count} missing value(s) in `{col}` with median ({median_val}).")

        # Category column handling
        cat_nulls = df['book_category'].isnull().sum()
        if cat_nulls > 0:
            df['book_category'] = df['book_category'].fillna('Unknown')
            missing_filled_count += cat_nulls
            self.audit_log['actions'].append(f"Filled {cat_nulls} missing category value(s) with 'Unknown'.")

        self.audit_log['missing_filled'] = missing_filled_count

        # 3. Filter invalid range rows
        # Month must be between 1 and 12
        before_range_filter = len(df)
        valid_mask = (df['month'] >= 1) & (df['month'] <= 12) & (df['number_of_students'] >= 0) & (df['previous_borrowing_count'] >= 0)
        
        invalid_rows = len(df) - valid_mask.sum()
        if invalid_rows > 0:
            df = df[valid_mask]
            self.audit_log['actions'].append(f"Filtered out {invalid_rows} row(s) with invalid range values (e.g. month < 1 or > 12).")

        # Clean string formats
        df['book_category'] = df['book_category'].astype(str).str.strip().str.title()

        self.cleaned_df = df
        self.audit_log['retained_rows'] = len(df)
        self.audit_log['dropped_rows'] = self.audit_log['original_rows'] - len(df)
        
        if len(df) < 20 and is_training:
            self.audit_log['warnings'].append(f"Dataset contains only {len(df)} rows after cleaning. Machine Learning models perform best with at least 50+ records.")

        self.audit_log['status'] = 'Valid & Cleaned'
        return self.cleaned_df, self.audit_log

    def get_summary_statistics(self) -> Optional[pd.DataFrame]:
        """Returns descriptive summary statistics for the cleaned dataset."""
        if self.cleaned_df is not None and not self.cleaned_df.empty:
            return self.cleaned_df.describe().T
        return None
