import pandas as pd
import numpy as np

class WhatIfSimulator:

    def __init__(self):
        pass

    # ── DETECT SCENARIO TYPE ───────────────────────────────
    def detect_scenario(self, scenario_text):
        """Detect what type of what-if scenario is being asked"""
        text = scenario_text.lower()

        if any(word in text for word in ['price', 'pricing', 'cost']):
            return 'price_change'
        elif any(word in text for word in ['discount', 'promotion', 'sale']):
            return 'discount_change'
        elif any(word in text for word in ['remove', 'stop', 'eliminate', 'discontinue']):
            return 'product_removal'
        elif any(word in text for word in ['expand', 'add', 'new region', 'new market']):
            return 'market_expansion'
        elif any(word in text for word in ['shipping', 'delivery', 'logistics']):
            return 'shipping_change'
        elif any(word in text for word in ['customer', 'retention', 'churn']):
            return 'customer_change'
        else:
            return 'general'

    # ── PRICE CHANGE SIMULATION ────────────────────────────
    def simulate_price_change(self, df, pct_change):
        """Simulate impact of a price change"""
        cols_lower = {col.lower(): col for col in df.columns}

        if 'sales' not in cols_lower:
            return None

        sales_col = cols_lower['sales']
        profit_col = cols_lower.get('profit')

        current_revenue = df[sales_col].sum()
        current_profit = df[profit_col].sum() if profit_col else None

        # Price elasticity assumption: -0.5 to -1.5 for retail
        elasticity = -1.0
        volume_change = pct_change * elasticity
        net_revenue_change = pct_change + volume_change

        new_revenue = current_revenue * (1 + net_revenue_change / 100)
        revenue_impact = new_revenue - current_revenue

        result = {
            "scenario": f"{pct_change:+.0f}% price change",
            "current_revenue": current_revenue,
            "estimated_new_revenue": new_revenue,
            "revenue_impact": revenue_impact,
            "volume_change_estimate": volume_change,
            "net_revenue_change": net_revenue_change
        }

        if current_profit and profit_col:
            profit_margin = current_profit / current_revenue
            new_profit = new_revenue * (profit_margin * (1 + pct_change/200))
            result['current_profit'] = current_profit
            result['estimated_new_profit'] = new_profit
            result['profit_impact'] = new_profit - current_profit

        return result

    # ── PRODUCT REMOVAL SIMULATION ─────────────────────────
    def simulate_product_removal(self, df, product_name):
        """Simulate removing a product or category"""
        cols_lower = {col.lower(): col for col in df.columns}

        results = {}
        for col_lower, col in cols_lower.items():
            if any(word in col_lower for word in
                   ['category', 'sub-category', 'product']):
                matches = df[df[col].str.contains(
                    product_name, case=False, na=False)]
                if len(matches) > 0:
                    sales_col = cols_lower.get('sales')
                    profit_col = cols_lower.get('profit')

                    if sales_col:
                        removed_revenue = matches[sales_col].sum()
                        total_revenue = df[sales_col].sum()
                        results['removed_revenue'] = removed_revenue
                        results['revenue_impact_pct'] = (
                            removed_revenue / total_revenue * 100)
                        results['remaining_revenue'] = (
                            total_revenue - removed_revenue)

                    if profit_col:
                        removed_profit = matches[profit_col].sum()
                        total_profit = df[profit_col].sum()
                        results['removed_profit'] = removed_profit
                        results['profit_impact'] = removed_profit
                        results['net_profit_change'] = -removed_profit

                    results['affected_orders'] = len(matches)
                    results['product'] = product_name
                    break

        return results if results else None

    # ── QUICK STATS FOR CONTEXT ────────────────────────────
    def get_quick_stats(self, df):
        """Get quick stats to provide context for simulations"""
        cols_lower = {col.lower(): col for col in df.columns}
        stats = {}

        if 'sales' in cols_lower:
            col = cols_lower['sales']
            stats['total_revenue'] = df[col].sum()
            stats['avg_order_value'] = df[col].mean()

        if 'profit' in cols_lower:
            col = cols_lower['profit']
            stats['total_profit'] = df[col].sum()
            if 'total_revenue' in stats:
                stats['profit_margin'] = (
                    stats['total_profit'] / stats['total_revenue'] * 100)

        stats['total_orders'] = len(df)

        return stats