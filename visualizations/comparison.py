#!/usr/bin/env python
# coding: utf-8

"""
Comparison visualization helpers for the cognitive warfare dashboard.
"""

import logging
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional

def create_comparison_plot(df1: pd.DataFrame, df2: pd.DataFrame, viz_type: str) -> go.Figure:
    """
    Create comparison plot based on visualization type.
    
    Args:
        df1: Data for selection 1
        df2: Data for selection 2
        viz_type: Type of visualization ('bar', 'sunburst', 'donut', 'sankey')
        
    Returns:
        go.Figure: Comparison plot
    """
    if viz_type == 'bar':
        return create_bar_comparison(df1, df2)
    elif viz_type == 'sunburst':
        return create_sunburst_comparison(df1, df2)
    elif viz_type == 'donut':
        return create_donut_comparison(df1, df2)
    elif viz_type == 'sankey':
        return create_sankey_comparison(df1, df2)
    else:
        return create_bar_comparison(df1, df2)  # Default

def create_bar_comparison(df1: pd.DataFrame, df2: pd.DataFrame) -> go.Figure:
    """Create side-by-side bar chart comparison."""
    
    if df1.empty and df2.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No data available for comparison",
            height=400
        )
        return fig
    
    # Aggregate by category for both selections
    cats1 = df1.groupby('category')['count'].sum().reset_index() if not df1.empty else pd.DataFrame(columns=['category', 'count'])
    cats2 = df2.groupby('category')['count'].sum().reset_index() if not df2.empty else pd.DataFrame(columns=['category', 'count'])
    
    # Get all unique categories
    all_categories = set()
    if not cats1.empty:
        all_categories.update(cats1['category'].tolist())
    if not cats2.empty:
        all_categories.update(cats2['category'].tolist())
    
    all_categories = sorted(list(all_categories))
    
    # Prepare data for plotting
    counts1 = []
    counts2 = []
    
    for cat in all_categories:
        count1 = cats1[cats1['category'] == cat]['count'].iloc[0] if not cats1.empty and cat in cats1['category'].values else 0
        count2 = cats2[cats2['category'] == cat]['count'].iloc[0] if not cats2.empty and cat in cats2['category'].values else 0
        counts1.append(count1)
        counts2.append(count2)
    
    fig = go.Figure()
    
    # Add bars for selection 1
    fig.add_trace(go.Bar(
        x=all_categories,
        y=counts1,
        name='Selection 1',
        marker_color='#1f77b4',
        hovertemplate='<b>%{x}</b><br>Selection 1: %{y:,}<extra></extra>'
    ))
    
    # Add bars for selection 2
    fig.add_trace(go.Bar(
        x=all_categories,
        y=counts2,
        name='Selection 2',
        marker_color='#ff7f0e',
        hovertemplate='<b>%{x}</b><br>Selection 2: %{y:,}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Category Comparison",
        xaxis_title="Cognitive Warfare Categories",
        yaxis_title="Number of Classifications",
        barmode='group',
        height=500,
        xaxis_tickangle=-45,
        hovermode='x unified'
    )
    
    return fig

def create_sunburst_comparison(df1: pd.DataFrame, df2: pd.DataFrame) -> go.Figure:
    """Create side-by-side sunburst comparison using subplots."""
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'sunburst'}, {'type': 'sunburst'}]],
        subplot_titles=('Selection 1', 'Selection 2')
    )
    
    # Selection 1 sunburst
    if not df1.empty:
        fig.add_trace(
            go.Sunburst(
                labels=df1['sub_subcategory'],
                parents=df1['subcategory'],
                values=df1['count'],
                branchvalues="total",
                name="Selection 1"
            ),
            row=1, col=1
        )
    
    # Selection 2 sunburst
    if not df2.empty:
        fig.add_trace(
            go.Sunburst(
                labels=df2['sub_subcategory'],
                parents=df2['subcategory'],
                values=df2['count'],
                branchvalues="total",
                name="Selection 2"
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        title="Taxonomy Distribution Comparison",
        height=600
    )
    
    return fig

def create_donut_comparison(df1: pd.DataFrame, df2: pd.DataFrame) -> go.Figure:
    """Create donut chart comparison."""
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'pie'}, {'type': 'pie'}]],
        subplot_titles=('Selection 1', 'Selection 2')
    )
    
    # Selection 1 donut
    if not df1.empty:
        cats1 = df1.groupby('category')['count'].sum().reset_index()
        fig.add_trace(
            go.Pie(
                labels=cats1['category'],
                values=cats1['count'],
                hole=0.4,
                name="Selection 1",
                hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}<extra></extra>'
            ),
            row=1, col=1
        )
    
    # Selection 2 donut
    if not df2.empty:
        cats2 = df2.groupby('category')['count'].sum().reset_index()
        fig.add_trace(
            go.Pie(
                labels=cats2['category'],
                values=cats2['count'],
                hole=0.4,
                name="Selection 2",
                hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}<extra></extra>'
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        title="Category Distribution Comparison",
        height=500
    )
    
    return fig

def create_sankey_comparison(df1: pd.DataFrame, df2: pd.DataFrame) -> go.Figure:
    """Create Sankey diagram showing flow between categories."""
    
    if df1.empty or df2.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Sankey diagram requires data from both selections",
            height=400
        )
        return fig
    
    # Aggregate data by category
    cats1 = df1.groupby('category')['count'].sum().reset_index()
    cats2 = df2.groupby('category')['count'].sum().reset_index()
    
    # Create nodes (categories from both selections)
    categories = sorted(list(set(cats1['category'].tolist() + cats2['category'].tolist())))
    
    # Create node labels
    node_labels = []
    node_colors = []
    
    # Add selection 1 nodes
    for cat in categories:
        node_labels.append(f"{cat} (Sel 1)")
        node_colors.append('#1f77b4')
    
    # Add selection 2 nodes  
    for cat in categories:
        node_labels.append(f"{cat} (Sel 2)")
        node_colors.append('#ff7f0e')
    
    # Create links (flows between same categories)
    source = []
    target = []
    value = []
    
    for i, cat in enumerate(categories):
        # Find counts for this category in both selections
        count1 = cats1[cats1['category'] == cat]['count'].iloc[0] if cat in cats1['category'].values else 0
        count2 = cats2[cats2['category'] == cat]['count'].iloc[0] if cat in cats2['category'].values else 0
        
        if count1 > 0 and count2 > 0:
            # Create flow from selection 1 to selection 2
            source.append(i)  # Selection 1 category
            target.append(i + len(categories))  # Selection 2 category
            value.append(min(count1, count2))  # Flow is minimum of both
    
    if not source:  # No common categories
        fig = go.Figure()
        fig.update_layout(
            title="No common categories found for Sankey diagram",
            height=400
        )
        return fig
    
    fig = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = node_labels,
            color = node_colors
        ),
        link = dict(
            source = source,
            target = target,
            value = value,
            color = 'rgba(255,127,14,0.4)'
        ))])
    
    fig.update_layout(
        title="Category Flow Comparison (Sankey Diagram)",
        height=600
    )
    
    return fig

def create_difference_heatmap(df1: pd.DataFrame, df2: pd.DataFrame) -> go.Figure:
    """Create heatmap showing differences between selections."""
    
    if df1.empty or df2.empty:
        fig = go.Figure()
        fig.update_layout(title="Heatmap requires data from both selections", height=400)
        return fig
    
    # Aggregate by category and subcategory
    pivot1 = df1.groupby(['category', 'subcategory'])['count'].sum().reset_index()
    pivot2 = df2.groupby(['category', 'subcategory'])['count'].sum().reset_index()
    
    # Create pivot tables
    pivot1_table = pivot1.pivot(index='category', columns='subcategory', values='count').fillna(0)
    pivot2_table = pivot2.pivot(index='category', columns='subcategory', values='count').fillna(0)
    
    # Ensure both tables have same dimensions
    all_categories = sorted(list(set(pivot1_table.index.tolist() + pivot2_table.index.tolist())))
    all_subcategories = sorted(list(set(pivot1_table.columns.tolist() + pivot2_table.columns.tolist())))
    
    pivot1_table = pivot1_table.reindex(index=all_categories, columns=all_subcategories, fill_value=0)
    pivot2_table = pivot2_table.reindex(index=all_categories, columns=all_subcategories, fill_value=0)
    
    # Calculate difference (percentage change)
    difference = ((pivot2_table - pivot1_table) / (pivot1_table + 1)) * 100  # +1 to avoid division by zero
    
    fig = go.Figure(data=go.Heatmap(
        z=difference.values,
        x=difference.columns,
        y=difference.index,
        colorscale='RdBu',
        zmid=0,
        hovertemplate='<b>%{y} - %{x}</b><br>Difference: %{z:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Percentage Difference Heatmap (Selection 2 vs Selection 1)",
        xaxis_title="Subcategories",
        yaxis_title="Categories",
        height=600
    )
    
    return fig