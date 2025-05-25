#!/usr/bin/env python
# coding: utf-8

"""
Burst visualization helpers for the cognitive warfare dashboard.
"""

import logging
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any
import numpy as np

def create_burst_timeline(timeline_df: pd.DataFrame, burst_results: List[Dict]) -> go.Figure:
    """
    Create timeline visualization showing detected bursts.
    
    Args:
        timeline_df: Timeline data
        burst_results: Detected bursts
        
    Returns:
        go.Figure: Timeline chart with burst markers
    """
    fig = go.Figure()
    
    # Add line for each category
    categories = timeline_df['category'].unique()
    colors = px.colors.qualitative.Set1
    
    for i, category in enumerate(categories):
        cat_data = timeline_df[timeline_df['category'] == category].sort_values('period')
        color = colors[i % len(colors)]
        
        fig.add_trace(go.Scatter(
            x=cat_data['period'],
            y=cat_data['count'],
            mode='lines+markers',
            name=category,
            line=dict(color=color, width=2),
            marker=dict(size=6),
            hovertemplate=f'<b>{category}</b><br>Date: %{{x}}<br>Count: %{{y:,}}<extra></extra>'
        ))
    
    # Add burst markers
    if burst_results:
        burst_periods = [burst['period'] for burst in burst_results]
        burst_counts = [burst['count'] for burst in burst_results]
        burst_categories = [burst['category'] for burst in burst_results]
        burst_intensities = [burst['intensity'] for burst in burst_results]
        
        fig.add_trace(go.Scatter(
            x=burst_periods,
            y=burst_counts,
            mode='markers',
            name='Detected Bursts',
            marker=dict(
                size=[min(15 + intensity * 5, 30) for intensity in burst_intensities],
                color='red',
                symbol='star',
                line=dict(width=2, color='darkred'),
                opacity=0.8
            ),
            hovertemplate='<b>BURST DETECTED</b><br>Category: %{text}<br>Date: %{x}<br>Count: %{y:,}<br>Intensity: %{customdata:.2f}<extra></extra>',
            text=burst_categories,
            customdata=burst_intensities
        ))
    
    fig.update_layout(
        title="Temporal Burst Analysis - Cognitive Warfare Categories",
        xaxis_title="Time Period",
        yaxis_title="Number of Classifications",
        height=600,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_burst_heatmap(timeline_df: pd.DataFrame, burst_results: List[Dict]) -> go.Figure:
    """
    Create heatmap showing burst intensity across categories and time.
    
    Args:
        timeline_df: Timeline data
        burst_results: Detected bursts
        
    Returns:
        go.Figure: Heatmap visualization
    """
    # Create pivot table for all data
    pivot_df = timeline_df.pivot(index='category', columns='period', values='count').fillna(0)
    
    # Create burst intensity matrix
    burst_matrix = pd.DataFrame(
        0.0, 
        index=pivot_df.index, 
        columns=pivot_df.columns
    )
    
    # Fill in burst intensities
    for burst in burst_results:
        category = burst['category']
        period = burst['period']
        intensity = burst['intensity']
        
        if category in burst_matrix.index:
            # Find closest period if exact match not found
            try:
                burst_matrix.loc[category, period] = intensity
            except KeyError:
                # Find closest time period
                closest_period = min(burst_matrix.columns, 
                                   key=lambda x: abs((x - period).total_seconds()))
                burst_matrix.loc[category, closest_period] = intensity
    
    # Format column labels for better display
    col_labels = [col.strftime('%Y-%m') if hasattr(col, 'strftime') else str(col) 
                  for col in burst_matrix.columns]
    
    fig = go.Figure(data=go.Heatmap(
        z=burst_matrix.values,
        x=col_labels,
        y=burst_matrix.index,
        colorscale='Reds',
        zmid=0,
        colorbar=dict(title="Burst Intensity"),
        hovertemplate='<b>%{y}</b><br>Period: %{x}<br>Burst Intensity: %{z:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Burst Intensity Heatmap",
        xaxis_title="Time Period",
        yaxis_title="Cognitive Warfare Categories",
        height=500,
        xaxis=dict(tickangle=45)
    )
    
    return fig

def create_burst_summary_chart(burst_results: List[Dict]) -> go.Figure:
    """
    Create summary chart showing burst characteristics.
    
    Args:
        burst_results: Detected bursts
        
    Returns:
        go.Figure: Summary chart
    """
    if not burst_results:
        fig = go.Figure()
        fig.update_layout(
            title="No bursts detected",
            height=400
        )
        return fig
    
    # Create subplot with multiple charts
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Burst Intensity by Category',
            'Burst Count Over Time',
            'Duration vs Intensity',
            'Top Burst Categories'
        ),
        specs=[[{'type': 'bar'}, {'type': 'scatter'}],
               [{'type': 'scatter'}, {'type': 'pie'}]]
    )
    
    # Prepare data
    df_bursts = pd.DataFrame(burst_results)
    
    # 1. Burst intensity by category
    cat_intensity = df_bursts.groupby('category')['intensity'].mean().sort_values(ascending=False)
    fig.add_trace(
        go.Bar(x=cat_intensity.index, y=cat_intensity.values, name="Avg Intensity"),
        row=1, col=1
    )
    
    # 2. Burst count over time
    df_bursts['period_str'] = df_bursts['period'].dt.strftime('%Y-%m')
    time_counts = df_bursts['period_str'].value_counts().sort_index()
    fig.add_trace(
        go.Scatter(x=time_counts.index, y=time_counts.values, mode='lines+markers', name="Burst Count"),
        row=1, col=2
    )
    
    # 3. Duration vs Intensity scatter
    fig.add_trace(
        go.Scatter(
            x=df_bursts.get('duration', [1] * len(df_bursts)),
            y=df_bursts['intensity'],
            mode='markers',
            marker=dict(size=8, opacity=0.7),
            text=df_bursts['category'],
            name="Duration vs Intensity"
        ),
        row=2, col=1
    )
    
    # 4. Top categories pie chart
    top_categories = df_bursts['category'].value_counts().head(5)
    fig.add_trace(
        go.Pie(labels=top_categories.index, values=top_categories.values, name="Top Categories"),
        row=2, col=2
    )
    
    fig.update_layout(
        title="Burst Analysis Summary",
        height=800,
        showlegend=False
    )
    
    return fig

def create_category_comparison_chart(timeline_df: pd.DataFrame, burst_results: List[Dict]) -> go.Figure:
    """
    Create comparison chart showing normal vs burst periods for each category.
    
    Args:
        timeline_df: Timeline data
        burst_results: Detected bursts
        
    Returns:
        go.Figure: Category comparison chart
    """
    categories = timeline_df['category'].unique()
    fig = make_subplots(
        rows=len(categories), cols=1,
        subplot_titles=[f"{cat} Activity" for cat in categories],
        shared_xaxes=True,
        vertical_spacing=0.02
    )
    
    for i, category in enumerate(categories):
        cat_data = timeline_df[timeline_df['category'] == category].sort_values('period')
        cat_bursts = [b for b in burst_results if b['category'] == category]
        
        # Add normal activity line
        fig.add_trace(
            go.Scatter(
                x=cat_data['period'],
                y=cat_data['count'],
                mode='lines',
                name=f"{category} Normal",
                line=dict(color='blue', width=1),
                showlegend=(i == 0)
            ),
            row=i+1, col=1
        )
        
        # Add burst markers
        if cat_bursts:
            burst_periods = [b['period'] for b in cat_bursts]
            burst_counts = [b['count'] for b in cat_bursts]
            
            fig.add_trace(
                go.Scatter(
                    x=burst_periods,
                    y=burst_counts,
                    mode='markers',
                    name=f"{category} Bursts",
                    marker=dict(size=10, color='red', symbol='star'),
                    showlegend=(i == 0)
                ),
                row=i+1, col=1
            )
    
    fig.update_layout(
        title="Category-wise Burst Detection",
        height=200 * len(categories),
        xaxis_title="Time Period"
    )
    
    return fig

def create_burst_strength_distribution(burst_results: List[Dict]) -> go.Figure:
    """
    Create distribution chart of burst strengths.
    
    Args:
        burst_results: Detected bursts
        
    Returns:
        go.Figure: Distribution chart
    """
    if not burst_results:
        fig = go.Figure()
        fig.update_layout(title="No bursts to analyze", height=400)
        return fig
    
    intensities = [burst['intensity'] for burst in burst_results]
    
    fig = go.Figure()
    
    # Add histogram
    fig.add_trace(go.Histogram(
        x=intensities,
        nbinsx=20,
        name="Burst Intensity Distribution",
        marker_color='steelblue',
        opacity=0.7
    ))
    
    # Add mean line
    mean_intensity = np.mean(intensities)
    fig.add_vline(
        x=mean_intensity,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: {mean_intensity:.2f}"
    )
    
    fig.update_layout(
        title="Distribution of Burst Intensities",
        xaxis_title="Burst Intensity",
        yaxis_title="Frequency",
        height=400
    )
    
    return fig