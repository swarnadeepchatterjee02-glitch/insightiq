import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import CHART_THEME, MAX_CHART_ROWS

class Visualizer:

    def __init__(self):
        self.theme = CHART_THEME
        self.colors = [
            '#4F8EF7', '#22C55E', '#F59E0B', '#EF4444',
            '#7C3AED', '#06B6D4', '#F97316', '#84CC16'
        ]

    # ── SMART CHART SELECTOR ───────────────────────────────
    def smart_chart(self, df, question):
        """Automatically select the best chart type based on question and data"""
        question_lower = question.lower()
        
        # Detect chart type from question
        if any(word in question_lower for word in ['trend', 'over time', 'monthly', 'yearly', 'growth']):
            return self._time_series_chart(df, question), "Line Chart — best for showing trends over time"
        
        elif any(word in question_lower for word in ['compare', 'vs', 'versus', 'difference', 'region', 'category']):
            return self._bar_chart(df, question), "Bar Chart — best for comparing categories"
        
        elif any(word in question_lower for word in ['distribution', 'spread', 'range', 'histogram']):
            return self._histogram(df, question), "Histogram — best for showing data distribution"
        
        elif any(word in question_lower for word in ['proportion', 'percentage', 'share', 'breakdown']):
            return self._pie_chart(df, question), "Donut Chart — best for showing proportions"
        
        elif any(word in question_lower for word in ['correlation', 'relationship', 'scatter']):
            return self._scatter_chart(df, question), "Scatter Plot — best for showing relationships"
        
        elif any(word in question_lower for word in ['top', 'best', 'worst', 'highest', 'lowest', 'ranking']):
            return self._ranking_chart(df, question), "Horizontal Bar Chart — best for rankings"
        
        else:
            return self._auto_chart(df, question), "Bar Chart — best default for this data"

    # ── TIME SERIES ────────────────────────────────────────
    def _time_series_chart(self, df, question):
        """Build a time series line chart"""
        try:
            date_col = self._find_date_column(df)
            numeric_col = self._find_best_numeric(df, question)
            
            if date_col and numeric_col:
                df_copy = df.copy()
                df_copy[date_col] = pd.to_datetime(df_copy[date_col])
                monthly = df_copy.groupby(df_copy[date_col].dt.to_period('M'))[numeric_col].sum().reset_index()
                monthly[date_col] = monthly[date_col].astype(str)
                
                fig = px.area(
                    monthly, x=date_col, y=numeric_col,
                    title=f"{numeric_col} Over Time",
                    template=self.theme,
                    color_discrete_sequence=self.colors
                )
                fig.update_traces(line_color=self.colors[0], fillcolor='rgba(79,142,247,0.2)')
                fig.update_layout(self._chart_layout())
                return fig
        except:
            pass
        return self._auto_chart(df, question)

    # ── BAR CHART ──────────────────────────────────────────
    def _bar_chart(self, df, question):
        """Build a grouped bar chart"""
        try:
            cat_col = self._find_best_categorical(df, question)
            numeric_col = self._find_best_numeric(df, question)
            
            if cat_col and numeric_col:
                grouped = df.groupby(cat_col)[numeric_col].sum().reset_index()
                grouped = grouped.sort_values(numeric_col, ascending=False).head(MAX_CHART_ROWS)
                
                colors = [self.colors[2] if v < 0 else self.colors[0] for v in grouped[numeric_col]]
                
                fig = px.bar(
                    grouped, x=cat_col, y=numeric_col,
                    title=f"{numeric_col} by {cat_col}",
                    template=self.theme,
                    color=numeric_col,
                    color_continuous_scale=['#EF4444', '#F59E0B', '#22C55E']
                )
                fig.update_layout(self._chart_layout())
                return fig
        except:
            pass
        return self._auto_chart(df, question)

    # ── RANKING CHART ──────────────────────────────────────
    def _ranking_chart(self, df, question):
        """Build a horizontal bar chart for rankings"""
        try:
            cat_col = self._find_best_categorical(df, question)
            numeric_col = self._find_best_numeric(df, question)
            
            if cat_col and numeric_col:
                grouped = df.groupby(cat_col)[numeric_col].sum().reset_index()
                
                if any(word in question.lower() for word in ['worst', 'lowest', 'loss']):
                    grouped = grouped.sort_values(numeric_col, ascending=True).head(10)
                else:
                    grouped = grouped.sort_values(numeric_col, ascending=False).head(10)
                
                colors = ['#EF4444' if v < 0 else '#22C55E' for v in grouped[numeric_col]]
                
                fig = go.Figure(go.Bar(
                    x=grouped[numeric_col],
                    y=grouped[cat_col],
                    orientation='h',
                    marker_color=colors
                ))
                fig.update_layout(
                    title=f"Top {cat_col} by {numeric_col}",
                    template=self.theme,
                    **self._chart_layout()
                )
                return fig
        except:
            pass
        return self._auto_chart(df, question)

    # ── PIE CHART ──────────────────────────────────────────
    def _pie_chart(self, df, question):
        """Build a donut chart"""
        try:
            cat_col = self._find_best_categorical(df, question)
            numeric_col = self._find_best_numeric(df, question)
            
            if cat_col and numeric_col:
                grouped = df.groupby(cat_col)[numeric_col].sum().reset_index()
                grouped = grouped[grouped[numeric_col] > 0].head(8)
                
                fig = px.pie(
                    grouped, names=cat_col, values=numeric_col,
                    title=f"{numeric_col} Distribution by {cat_col}",
                    template=self.theme,
                    color_discrete_sequence=self.colors,
                    hole=0.4
                )
                fig.update_layout(self._chart_layout())
                return fig
        except:
            pass
        return self._auto_chart(df, question)

    # ── HISTOGRAM ──────────────────────────────────────────
    def _histogram(self, df, question):
        """Build a histogram"""
        try:
            numeric_col = self._find_best_numeric(df, question)
            if numeric_col:
                fig = px.histogram(
                    df, x=numeric_col,
                    title=f"Distribution of {numeric_col}",
                    template=self.theme,
                    color_discrete_sequence=self.colors,
                    nbins=40
                )
                fig.update_layout(self._chart_layout())
                return fig
        except:
            pass
        return self._auto_chart(df, question)

    # ── SCATTER CHART ──────────────────────────────────────
    def _scatter_chart(self, df, question):
        """Build a scatter plot"""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 2:
                fig = px.scatter(
                    df.sample(min(500, len(df))),
                    x=numeric_cols[0], y=numeric_cols[1],
                    title=f"Relationship: {numeric_cols[0]} vs {numeric_cols[1]}",
                    template=self.theme,
                    color_discrete_sequence=self.colors,
                    opacity=0.6
                )
                fig.update_layout(self._chart_layout())
                return fig
        except:
            pass
        return self._auto_chart(df, question)

    # ── AUTO CHART ─────────────────────────────────────────
    def _auto_chart(self, df, question):
        """Fallback chart — auto-detect best visualization"""
        try:
            cat_col = self._find_best_categorical(df, question)
            numeric_col = self._find_best_numeric(df, question)
            
            if cat_col and numeric_col:
                grouped = df.groupby(cat_col)[numeric_col].sum().reset_index()
                grouped = grouped.sort_values(numeric_col, ascending=False).head(15)
                
                fig = px.bar(
                    grouped, x=cat_col, y=numeric_col,
                    title=f"{numeric_col} by {cat_col}",
                    template=self.theme,
                    color=numeric_col,
                    color_continuous_scale=['#EF4444', '#F59E0B', '#22C55E']
                )
                fig.update_layout(self._chart_layout())
                return fig
            
            elif numeric_col:
                fig = px.histogram(
                    df, x=numeric_col,
                    template=self.theme,
                    color_discrete_sequence=self.colors
                )
                fig.update_layout(self._chart_layout())
                return fig
                
        except Exception as e:
            pass
        return None

    # ── OVERVIEW CHARTS ────────────────────────────────────
    def get_overview_charts(self, df):
        """Generate 4 overview charts for the dashboard"""
        charts = []
        
        try:
            # Chart 1 - Revenue trend
            date_col = self._find_date_column(df)
            numeric_col = self._find_best_numeric(df, "sales revenue")
            if date_col and numeric_col:
                df_copy = df.copy()
                df_copy[date_col] = pd.to_datetime(df_copy[date_col])
                monthly = df_copy.groupby(df_copy[date_col].dt.to_period('M'))[numeric_col].sum().reset_index()
                monthly[date_col] = monthly[date_col].astype(str)
                fig = px.area(monthly, x=date_col, y=numeric_col,
                    title="Revenue Trend Over Time", template=self.theme,
                    color_discrete_sequence=self.colors)
                fig.update_traces(line_color=self.colors[0], fillcolor='rgba(79,142,247,0.2)')
                fig.update_layout(self._chart_layout())
                charts.append(("Revenue Trend", fig))
        except:
            pass

        try:
            # Chart 2 - Top categories
            cat_col = self._find_best_categorical(df, "category region")
            numeric_col = self._find_best_numeric(df, "sales")
            if cat_col and numeric_col:
                grouped = df.groupby(cat_col)[numeric_col].sum().reset_index()
                grouped = grouped.sort_values(numeric_col, ascending=False).head(10)
                fig = px.bar(grouped, x=cat_col, y=numeric_col,
                    title=f"{numeric_col} by {cat_col}",
                    template=self.theme,
                    color=numeric_col,
                    color_continuous_scale=['#EF4444', '#F59E0B', '#22C55E'])
                fig.update_layout(self._chart_layout())
                charts.append((f"{numeric_col} by {cat_col}", fig))
        except:
            pass

        try:
            # Chart 3 - Profit analysis
            profit_col = None
            for col in df.columns:
                if 'profit' in col.lower():
                    profit_col = col
                    break
            cat_col = self._find_best_categorical(df, "category sub-category")
            if profit_col and cat_col:
                grouped = df.groupby(cat_col)[profit_col].sum().reset_index()
                grouped = grouped.sort_values(profit_col)
                colors = ['#EF4444' if v < 0 else '#22C55E' for v in grouped[profit_col]]
                fig = go.Figure(go.Bar(
                    x=grouped[profit_col], y=grouped[cat_col],
                    orientation='h', marker_color=colors))
                fig.update_layout(title=f"Profit by {cat_col}",
                    template=self.theme, **self._chart_layout())
                charts.append((f"Profit by {cat_col}", fig))
        except:
            pass

        try:
            # Chart 4 - Distribution
            numeric_col = self._find_best_numeric(df, "profit margin")
            if numeric_col:
                fig = px.histogram(df, x=numeric_col,
                    title=f"Distribution of {numeric_col}",
                    template=self.theme,
                    color_discrete_sequence=self.colors, nbins=40)
                fig.update_layout(self._chart_layout())
                charts.append((f"{numeric_col} Distribution", fig))
        except:
            pass

        return charts

    # ── HELPERS ────────────────────────────────────────────
    def _find_date_column(self, df):
        for col in df.columns:
            if 'date' in col.lower():
                return col
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col].head(5))
                    return col
                except:
                    pass
        return None

    def _find_best_numeric(self, df, question):
        question_lower = question.lower()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        priority = ['profit margin', 'profit', 'sales', 'revenue', 'amount']
        for keyword in priority:
            if keyword in question_lower:
                for col in numeric_cols:
                    if keyword in col.lower():
                        return col
        
        for keyword in priority:
            for col in numeric_cols:
                if keyword in col.lower():
                    return col
        
        return numeric_cols[0] if numeric_cols else None

    def _find_best_categorical(self, df, question):
        question_lower = question.lower()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        priority = ['sub-category', 'category', 'region', 'segment', 'state', 'city']
        for keyword in priority:
            if keyword in question_lower:
                for col in cat_cols:
                    if keyword in col.lower():
                        return col
        
        for keyword in priority:
            for col in cat_cols:
                if keyword in col.lower():
                    return col
        
        skip = ['name', 'id', 'date', 'description', 'address']
        for col in cat_cols:
            if not any(s in col.lower() for s in skip):
                return col
        
        return cat_cols[0] if cat_cols else None

    def _chart_layout(self):
        return {
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "font": {"family": "DM Sans, sans-serif", "color": "#e8eaf6"},
            "margin": {"t": 50, "b": 40, "l": 40, "r": 40},
            "showlegend": True
        }