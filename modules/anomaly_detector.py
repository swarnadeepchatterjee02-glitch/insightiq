import pandas as pd
import numpy as np

class AnomalyDetector:

    def __init__(self):
        pass

    # ── STATISTICAL ANOMALIES ──────────────────────────────
    def detect_statistical_anomalies(self, df):
        """Detect values that are statistically unusual"""
        anomalies = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            mean = df[col].mean()
            std = df[col].std()
            if std == 0:
                continue

            # Find extreme outliers (3 standard deviations)
            extreme_mask = np.abs((df[col] - mean) / std) > 3
            extreme_count = extreme_mask.sum()

            if extreme_count > 0:
                extreme_vals = df[col][extreme_mask]
                anomalies.append({
                    "type": "Statistical Outlier",
                    "column": col,
                    "count": int(extreme_count),
                    "severity": "High" if extreme_count > 10 else "Medium",
                    "message": f"'{col}' has {extreme_count} extreme values",
                    "detail": f"Range of outliers: {extreme_vals.min():.2f} to {extreme_vals.max():.2f}",
                    "icon": "🔴" if extreme_count > 10 else "🟡"
                })

        return anomalies

    # ── TREND ANOMALIES ────────────────────────────────────
    def detect_trend_anomalies(self, df):
        """Detect unusual patterns in time series data"""
        anomalies = []

        # Find date column
        date_col = None
        for col in df.columns:
            if 'date' in col.lower():
                date_col = col
                break

        if not date_col:
            return anomalies

        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col])
            df_copy['Month'] = df_copy[date_col].dt.to_period('M')

            numeric_cols = df.select_dtypes(include=[np.number]).columns[:3]

            for col in numeric_cols:
                monthly = df_copy.groupby('Month')[col].sum()
                if len(monthly) < 3:
                    continue

                mean_val = monthly.mean()
                std_val = monthly.std()

                if std_val == 0:
                    continue

                for period, value in monthly.items():
                    z_score = abs((value - mean_val) / std_val)
                    if z_score > 2:
                        direction = "spike" if value > mean_val else "drop"
                        pct_diff = abs((value - mean_val) / mean_val * 100)
                        anomalies.append({
                            "type": "Trend Anomaly",
                            "column": col,
                            "period": str(period),
                            "severity": "High" if z_score > 3 else "Medium",
                            "message": f"{col} {direction} in {period}",
                            "detail": f"{pct_diff:.1f}% {'above' if direction == 'spike' else 'below'} average",
                            "icon": "📈" if direction == "spike" else "📉"
                        })

        except Exception as e:
            pass

        return anomalies[:5]

    # ── BUSINESS ANOMALIES ─────────────────────────────────
    def detect_business_anomalies(self, df):
        """Detect business-specific unusual patterns"""
        anomalies = []
        cols_lower = {col.lower(): col for col in df.columns}

        # Negative profit on high sales
        if 'profit' in cols_lower and 'sales' in cols_lower:
            profit_col = cols_lower['profit']
            sales_col = cols_lower['sales']

            high_sales_threshold = df[sales_col].quantile(0.75)
            high_sales_neg_profit = df[
                (df[sales_col] > high_sales_threshold) &
                (df[profit_col] < 0)
            ]

            if len(high_sales_neg_profit) > 0:
                anomalies.append({
                    "type": "Business Anomaly",
                    "severity": "High",
                    "message": f"{len(high_sales_neg_profit)} high-sales orders with negative profit",
                    "detail": "Orders with top 25% sales but negative profit — possible pricing or discount issue",
                    "icon": "⚠️"
                })

        # Extreme discounts
        if 'discount' in cols_lower:
            discount_col = cols_lower['discount']
            high_discount = df[df[discount_col] > 0.5]
            if len(high_discount) > 0:
                anomalies.append({
                    "type": "Business Anomaly",
                    "severity": "Medium",
                    "message": f"{len(high_discount)} orders with >50% discount",
                    "detail": "Heavy discounting may be eroding profit margins",
                    "icon": "🏷️"
                })

        # Zero sales
        if 'sales' in cols_lower:
            sales_col = cols_lower['sales']
            zero_sales = df[df[sales_col] == 0]
            if len(zero_sales) > 0:
                anomalies.append({
                    "type": "Data Quality",
                    "severity": "Medium",
                    "message": f"{len(zero_sales)} orders with zero sales value",
                    "detail": "These records may need review",
                    "icon": "🔍"
                })

        return anomalies

    # ── FULL REPORT ────────────────────────────────────────
    def get_full_anomaly_report(self, df):
        """Run all anomaly detections and return combined report"""
        all_anomalies = []
        all_anomalies.extend(self.detect_statistical_anomalies(df))
        all_anomalies.extend(self.detect_business_anomalies(df))
        all_anomalies.extend(self.detect_trend_anomalies(df))

        high = [a for a in all_anomalies if a.get('severity') == 'High']
        medium = [a for a in all_anomalies if a.get('severity') == 'Medium']

        return {
            "total": len(all_anomalies),
            "high": high,
            "medium": medium,
            "all": all_anomalies
        }