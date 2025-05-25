#!/usr/bin/env python
# coding: utf-8

"""
Sunburst visualization for Cognitive Warfare Dashboard
-------------------------------------------------------
Creates sunburst charts exactly matching RUW app formatting and colors.
"""

import logging
from typing import Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

logger = logging.getLogger(__name__)

# Exact color scheme matching RUW app
CATEGORY_COLORS = {
    'Conceptual Foundations': '#1f77b4',  # blue
    'Cognitive Target Domain': '#ff7f0e',  # orange  
    'Operational Scope': '#2ca02c',  # green
    'Counter-Measures': '#d62728',  # red
    'Historical Dimension': '#9467bd',  # purple
    'Related Concepts': '#8c564b'  # brown
}

def create_sunburst_chart(df: pd.DataFrame, title: str = "Taxonomy Distribution") -> go.Figure:
    """
    Create a sunburst chart exactly matching RUW app formatting.
    
    Args:
        df: DataFrame with category, subcategory, sub_subcategory, count columns
        title: Chart title
        
    Returns:
        go.Figure: Configured sunburst chart
    """
    try:
        if df.empty:
            # Return empty figure with RUW styling
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                height=700,
                showlegend=False,
                paper_bgcolor='white',
                plot_bgcolor='white',
                title=dict(text=title, x=0.5, font=dict(size=16))
            )
            return fig
        
        # Prepare data for sunburst exactly like RUW
        ids = []
        labels = []
        parents = []
        values = []
        colors = []
        
        # Add root
        ids.append("root")
        labels.append("Total")
        parents.append("")
        values.append(df['count'].sum())
        colors.append('#13376f')  # RUW theme color
        
        # Add categories (level 1)
        category_totals = df.groupby('category')['count'].sum()
        for category in category_totals.index:
            ids.append(category)
            labels.append(category)
            parents.append("root")
            values.append(category_totals[category])
            # Use exact RUW colors
            colors.append(CATEGORY_COLORS.get(category, '#13376f'))
        
        # Add subcategories (level 2) 
        subcategory_data = df.groupby(['category', 'subcategory'])['count'].sum().reset_index()
        for _, row in subcategory_data.iterrows():
            if pd.notna(row['subcategory']) and row['subcategory'] != '':
                subcategory_id = f"{row['category']} - {row['subcategory']}"
                ids.append(subcategory_id)
                labels.append(row['subcategory'])
                parents.append(row['category'])
                values.append(row['count'])
                # Lighter shade of parent category color
                base_color = CATEGORY_COLORS.get(row['category'], '#13376f')
                colors.append(base_color + '80')  # Add transparency like RUW
        
        # Add sub-subcategories (level 3)
        for _, row in df.iterrows():
            if pd.notna(row['sub_subcategory']) and row['sub_subcategory'] != '' and row['sub_subcategory'] != 'Other':
                sub_subcategory_id = f"{row['category']} - {row['subcategory']} - {row['sub_subcategory']}"
                parent_id = f"{row['category']} - {row['subcategory']}" if pd.notna(row['subcategory']) else row['category']
                
                ids.append(sub_subcategory_id)
                labels.append(row['sub_subcategory'])
                parents.append(parent_id)
                values.append(row['count'])
                # Even lighter shade
                base_color = CATEGORY_COLORS.get(row['category'], '#13376f')
                colors.append(base_color + '60')  # More transparency like RUW
        
        # Create sunburst with exact RUW configuration
        fig = go.Figure(go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(
                colors=colors,
                line=dict(color="white", width=2)
            ),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percentParent}<extra></extra>',
            maxdepth=3
        ))
        
        # Update layout to match RUW exactly
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=18, color='#13376f')
            ),
            height=700,
            font=dict(size=12),
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(t=60, l=0, r=0, b=0)
        )
        
        logger.info(f"Created sunburst chart with {len(df)} data points")
        return fig
        
    except Exception as e:
        logger.error(f"Error creating sunburst chart: {e}")
        # Return error figure
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating chart: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="red")
        )
        fig.update_layout(
            height=700,
            showlegend=False,
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        return fig


def get_sunburst_drill_down_data(df: pd.DataFrame, selected_path: str) -> pd.DataFrame:
    """
    Get filtered data for sunburst drill-down exactly like RUW.
    
    Args:
        df: Original dataframe
        selected_path: Selected path from sunburst click
        
    Returns:
        pd.DataFrame: Filtered dataframe for the selected segment
    """
    try:
        if not selected_path or selected_path == "Total":
            return df
        
        # Parse the hierarchical path
        path_parts = selected_path.split(' - ')
        
        if len(path_parts) == 1:
            # Category level
            return df[df['category'] == path_parts[0]]
        elif len(path_parts) == 2:
            # Subcategory level
            return df[(df['category'] == path_parts[0]) & 
                     (df['subcategory'] == path_parts[1])]
        elif len(path_parts) == 3:
            # Sub-subcategory level
            return df[(df['category'] == path_parts[0]) & 
                     (df['subcategory'] == path_parts[1]) &
                     (df['sub_subcategory'] == path_parts[2])]
        
        return df
        
    except Exception as e:
        logger.error(f"Error in sunburst drill-down: {e}")
        return df