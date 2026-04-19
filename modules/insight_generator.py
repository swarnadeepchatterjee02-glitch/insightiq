import pandas as pd
import numpy as np

class InsightGenerator:

    def __init__(self):
        pass

    # ── BEFORE VS AFTER ────────────────────────────────────
    def get_before_after(self):
        """Return the before vs after value framing"""
        return {
            "before": [
                "📊 Manual Excel work taking hours",
                "💻 Writing complex SQL queries",
                "📈 Building dashboards from scratch",
                "🔍 Guessing which data matters",
                "📄 Writing reports manually"
            ],
            "after": [
                "💬 Ask questions in plain English",
                "⚡ Get instant AI-powered insights",
                "📊 Automated charts and visualizations",
                "🎯 AI identifies what matters most",
                "📑 One-click PDF report generation"
            ]
        }

    # ── QUICK STATS ────────────────────────────────────────
    def get_quick_stats(self, df):
        """Generate quick statistical summary"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        stats = []

        for col in numeric_cols[:4]:
            stats.append({
                "column": col,
                "mean": round(df[col].mean(), 2),
                "median": round(df[col].median(), 2),
                "min": round(df[col].min(), 2),
                "max": round(df[col].max(), 2),
                "std": round(df[col].std(), 2)
            })
        return stats

    # ── GROWTH ANALYSIS ────────────────────────────────────
    def get_growth_analysis(self, df):
        """Calculate year over year or period growth"""
        results = []
        
        # Find date column
        date_col = None
        for col in df.columns:
            if 'date' in col.lower():
                date_col = col
                break
        
        if not date_col:
            return results

        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col])
            df_copy['Year'] = df_copy[date_col].dt.year

            numeric_cols = df.select_dtypes(include=[np.number]).columns[:3]
            
            for col in numeric_cols:
                yearly = df_copy.groupby('Year')[col].sum()
                if len(yearly) >= 2:
                    years = sorted(yearly.index)
                    first_val = yearly[years[0]]
                    last_val = yearly[years[-1]]
                    if first_val != 0:
                        growth = ((last_val - first_val) / abs(first_val) * 100).round(1)
                        results.append({
                            "metric": col,
                            "from_year": years[0],
                            "to_year": years[-1],
                            "from_value": round(first_val, 2),
                            "to_value": round(last_val, 2),
                            "growth_pct": growth,
                            "direction": "↑" if growth > 0 else "↓"
                        })
        except:
            pass

        return results

    # ── TOP PERFORMERS ─────────────────────────────────────
    def get_top_performers(self, df, n=5):
        """Find top and bottom performers across key dimensions"""
        results = {}
        cat_cols = df.select_dtypes(include=['object']).columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(cat_cols) == 0 or len(numeric_cols) == 0:
            return results

        # Use first good categorical and numeric
        skip = ['name', 'id', 'date', 'description']
        cat_col = None
        for col in cat_cols:
            if not any(s in col.lower() for s in skip):
                cat_col = col
                break

        numeric_col = None
        for col in numeric_cols:
            if 'profit' in col.lower() or 'sales' in col.lower():
                numeric_col = col
                break
        if not numeric_col:
            numeric_col = numeric_cols[0]

        if cat_col and numeric_col:
            grouped = df.groupby(cat_col)[numeric_col].sum().reset_index()
            grouped = grouped.sort_values(numeric_col, ascending=False)
            
            results['top'] = grouped.head(n).to_dict('records')
            results['bottom'] = grouped.tail(n).to_dict('records')
            results['cat_col'] = cat_col
            results['numeric_col'] = numeric_col

        return results

    # ── CORRELATION FINDER ─────────────────────────────────
    def get_correlations(self, df):
        """Find strong correlations between numeric columns"""
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) < 2:
            return []

        corr_matrix = numeric_df.corr()
        strong_correlations = []

        cols = corr_matrix.columns.tolist()
        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.5:
                    strong_correlations.append({
                        "col1": cols[i],
                        "col2": cols[j],
                        "correlation": round(corr_val, 3),
                        "strength": "Strong" if abs(corr_val) > 0.7 else "Moderate",
                        "direction": "positive" if corr_val > 0 else "negative"
                    })

        return sorted(strong_correlations, key=lambda x: abs(x['correlation']), reverse=True)[:5]

    # ── SEGMENT ANALYSIS ───────────────────────────────────
    def get_segment_analysis(self, df):
        """Analyze performance across key segments"""
        segments = {}
        cat_cols = df.select_dtypes(include=['object']).columns[:3]
        
        sales_col = None
        profit_col = None
        for col in df.columns:
            if 'sales' in col.lower() or 'revenue' in col.lower():
                sales_col = col
            if 'profit' in col.lower():
                profit_col = col

        if not sales_col:
            return segments

        for cat_col in cat_cols:
            skip = ['name', 'id', 'date', 'postal', 'address']
            if any(s in cat_col.lower() for s in skip):
                continue
            if df[cat_col].nunique() > 20:
                continue
                
            grouped = df.groupby(cat_col).agg({
                sales_col: 'sum',
                **({profit_col: 'sum'} if profit_col else {})
            }).reset_index()
            
            grouped['Revenue Share %'] = (grouped[sales_col] / grouped[sales_col].sum() * 100).round(1)
            segments[cat_col] = grouped.to_dict('records')

        return segments