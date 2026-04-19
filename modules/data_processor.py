import pandas as pd
import numpy as np
from config import SAMPLE_DATA_PATH, MAX_FILE_SIZE_MB

class DataProcessor:
    
    def __init__(self):
        self.df = None
        self.filename = None
        self.analysis_summary = None

    # ── LOAD DATA ──────────────────────────────────────────
    def load_file(self, uploaded_file):
        """Load CSV or Excel file uploaded by user"""
        try:
            filename = uploaded_file.name.lower()
            if filename.endswith('.csv'):
                self.df = pd.read_csv(uploaded_file, encoding='windows-1252')
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                self.df = pd.read_excel(uploaded_file)
            else:
                return False, "Unsupported file format. Please upload CSV or Excel."
            
            self.filename = uploaded_file.name
            self.analysis_summary = self._build_summary()
            return True, "File loaded successfully!"
        except Exception as e:
            return False, f"Error loading file: {str(e)}"

    def load_sample_data(self):
        """Load the built-in demo dataset"""
        try:
            self.df = pd.read_csv(SAMPLE_DATA_PATH)
            self.filename = "Superstore Sales Demo Dataset"
            self.analysis_summary = self._build_summary()
            return True, "Demo dataset loaded!"
        except Exception as e:
            return False, f"Error loading demo data: {str(e)}"

    # ── DATA SUMMARY ───────────────────────────────────────
    def _build_summary(self):
        """Build a comprehensive summary of the dataset for AI context"""
        df = self.df
        summary = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "numeric_columns": list(df.select_dtypes(include=[np.number]).columns),
            "categorical_columns": list(df.select_dtypes(include=['object']).columns),
            "sample_rows": df.head(3).to_string(),
            "basic_stats": df.describe().to_string() if len(df.select_dtypes(include=[np.number]).columns) > 0 else "No numeric columns"
        }
        return summary

    # ── DATA QUALITY ───────────────────────────────────────
    def get_data_quality_report(self):
        """Generate a detailed data quality report"""
        df = self.df
        issues = []
        score = 100

        # Check missing values
        missing = df.isnull().sum()
        missing_cols = missing[missing > 0]
        if len(missing_cols) > 0:
            for col, count in missing_cols.items():
                pct = (count / len(df) * 100).round(1)
                issues.append(f"⚠️ '{col}' has {count} missing values ({pct}%)")
                score -= min(10, pct)

        # Check duplicates
        dupes = df.duplicated().sum()
        if dupes > 0:
            issues.append(f"⚠️ {dupes} duplicate rows detected")
            score -= 5

        # Check numeric columns for outliers
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:3]:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)).sum()
            if outliers > 0:
                issues.append(f"📊 '{col}' has {outliers} potential outliers")

        # Check date columns
        for col in df.columns:
            if 'date' in col.lower():
                try:
                    pd.to_datetime(df[col])
                    issues.append(f"✅ '{col}' detected as date column")
                except:
                    issues.append(f"⚠️ '{col}' may need date formatting")

        score = max(0, round(score))

        return {
            "score": score,
            "issues": issues if issues else ["✅ No major issues found"],
            "total_rows": len(df),
            "total_cols": len(df.columns),
            "missing_total": int(df.isnull().sum().sum()),
            "duplicates": int(dupes)
        }

    # ── BUSINESS METRICS ───────────────────────────────────
    def get_business_metrics(self):
        """Auto-detect and compute key business metrics"""
        df = self.df
        metrics = {}
        cols_lower = {col.lower(): col for col in df.columns}

        # Revenue / Sales
        for keyword in ['sales', 'revenue', 'amount', 'total']:
            if keyword in cols_lower:
                col = cols_lower[keyword]
                metrics['Total Revenue'] = f"${df[col].sum():,.2f}"
                metrics['Avg Transaction'] = f"${df[col].mean():,.2f}"
                break

        # Profit
        for keyword in ['profit', 'margin', 'income']:
            if keyword in cols_lower:
                col = cols_lower[keyword]
                metrics['Total Profit'] = f"${df[col].sum():,.2f}"
                break

        # Profit Margin
      # Profit Margin
        if 'profit' in cols_lower and ('sales' in cols_lower or 'revenue' in cols_lower):
            profit_col = cols_lower['profit']
            sales_col = cols_lower.get('sales') or cols_lower.get('revenue')
            if sales_col:
                margin = (df[profit_col].sum() / df[sales_col].sum() * 100).round(1)
                metrics['Profit Margin'] = f"{margin}%" 
# Orders / Transactions
        for keyword in ['order id', 'orderid', 'transaction', 'id']:
            if keyword in cols_lower:
                col = cols_lower[keyword]
                metrics['Total Orders'] = f"{df[col].nunique():,}"
                break

        # Customers
        for keyword in ['customer', 'client', 'user']:
            for col_lower, col in cols_lower.items():
                if keyword in col_lower:
                    metrics['Unique Customers'] = f"{df[col].nunique():,}"
                    break

        # Date range
        for col_lower, col in cols_lower.items():
            if 'date' in col_lower:
                try:
                    dates = pd.to_datetime(df[col])
                    metrics['Date Range'] = f"{dates.min().strftime('%b %Y')} — {dates.max().strftime('%b %Y')}"
                    break
                except:
                    pass

        # Row count
        metrics['Total Records'] = f"{len(df):,}"

        return metrics 
    # ── EXPLAIN DATA ───────────────────────────────────────
    def get_data_explanation(self):
        """Generate a plain English explanation of what the dataset contains"""
        df = self.df
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        cat_cols = list(df.select_dtypes(include=['object']).columns)

        explanation = {
            "shape": f"{len(df):,} rows × {len(df.columns)} columns",
            "numeric_cols": numeric_cols,
            "categorical_cols": cat_cols,
            "sample_questions": self._generate_sample_questions()
        }
        return explanation

    def _generate_sample_questions(self):
        """Auto-generate relevant sample questions based on column names"""
        df = self.df
        questions = []
        cols_lower = {col.lower(): col for col in df.columns}

        if 'sales' in cols_lower or 'revenue' in cols_lower:
            questions.append("What is the total revenue by region?")
            questions.append("Which month had the highest sales?")

        if 'profit' in cols_lower:
            questions.append("Which product category is most profitable?")
            questions.append("What products are losing money?")

        if 'customer' in ' '.join(cols_lower.keys()):
            questions.append("Who are the top 10 customers?")

        if 'date' in ' '.join(cols_lower.keys()):
            questions.append("Show me the sales trend over time")

        if 'region' in cols_lower or 'state' in cols_lower:
            questions.append("Which region performs best?")

        if len(questions) < 3:
            questions.append("What are the key trends in this data?")
            questions.append("Give me a summary of this dataset")

        return questions[:5]
    # ── CONTEXT FOR AI ─────────────────────────────────────
    def get_ai_context(self):
        """Prepare a concise dataset description for the AI"""
        if self.analysis_summary is None:
            return ""
        s = self.analysis_summary
        context = f"""
Dataset: {self.filename}
Size: {s['rows']:,} rows × {s['columns']} columns
Columns: {', '.join(s['column_names'])}
Numeric columns: {', '.join(s['numeric_columns'])}
Categorical columns: {', '.join(s['categorical_columns'])}
Sample data:
{s['sample_rows']}
Basic statistics:
{s['basic_stats']}
        """
        return context.strip()