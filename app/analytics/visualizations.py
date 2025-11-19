"""
Visualizations Module
Creates charts and graphs for analytics
"""

import json


def create_visualization(chart_type, data, title="", options=None):
    """
    Create visualization configuration for Chart.js
    
    Args:
        chart_type: 'bar', 'line', 'pie', 'doughnut', 'radar'
        data: Dictionary with labels and datasets
        title: Chart title
        options: Additional chart options
    
    Returns:
        JSON configuration for Chart.js
    """
    try:
        config = {
            'type': chart_type,
            'data': data,
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'title': {
                        'display': bool(title),
                        'text': title,
                        'font': {
                            'size': 16,
                            'weight': 'bold'
                        }
                    },
                    'legend': {
                        'display': True,
                        'position': 'bottom'
                    }
                }
            }
        }
        
        # Add custom options
        if options:
            config['options'].update(options)
        
        return json.dumps(config)
    except Exception as e:
        print(f"Error creating visualization: {e}")
        return json.dumps({})


def create_program_type_chart(program_types_data):
    """Create pie chart for program types distribution"""
    labels = list(program_types_data.keys())
    values = list(program_types_data.values())
    
    data = {
        'labels': labels,
        'datasets': [{
            'data': values,
            'backgroundColor': [
                '#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', 
                '#EF4444', '#6366F1', '#EC4899', '#14B8A6'
            ],
            'borderWidth': 2,
            'borderColor': '#FFFFFF'
        }]
    }
    
    return create_visualization('doughnut', data, 'Program Types Distribution')


def create_monthly_trend_chart(monthly_data):
    """Create line chart for monthly trends"""
    labels = [item['month'] for item in monthly_data]
    values = [item['count'] for item in monthly_data]
    
    data = {
        'labels': labels,
        'datasets': [{
            'label': 'Programs',
            'data': values,
            'borderColor': '#3B82F6',
            'backgroundColor': 'rgba(59, 130, 246, 0.1)',
            'tension': 0.4,
            'fill': True
        }]
    }
    
    options = {
        'scales': {
            'y': {
                'beginAtZero': True,
                'ticks': {
                    'stepSize': 1
                }
            }
        }
    }
    
    return create_visualization('line', data, 'Monthly Program Trend', options)


def create_toli_comparison_chart(comparison_data):
    """Create bar chart for toli comparison"""
    data = {
        'labels': comparison_data['labels'],
        'datasets': [
            {
                'label': 'Programs',
                'data': comparison_data['programs'],
                'backgroundColor': '#3B82F6',
                'borderRadius': 5
            },
            {
                'label': 'Engagement Score',
                'data': comparison_data['engagement'],
                'backgroundColor': '#10B981',
                'borderRadius': 5
            }
        ]
    }
    
    options = {
        'scales': {
            'y': {
                'beginAtZero': True
            }
        }
    }
    
    return create_visualization('bar', data, 'Toli Performance Comparison', options)


def create_engagement_chart(engagement_data):
    """Create doughnut chart for member engagement"""
    data = {
        'labels': ['Highly Engaged', 'Moderately Engaged', 'Low Engaged', 'Inactive'],
        'datasets': [{
            'data': [
                engagement_data.get('highly_engaged', 0),
                engagement_data.get('moderately_engaged', 0),
                engagement_data.get('low_engaged', 0),
                engagement_data.get('inactive', 0)
            ],
            'backgroundColor': ['#10B981', '#3B82F6', '#F59E0B', '#EF4444'],
            'borderWidth': 2,
            'borderColor': '#FFFFFF'
        }]
    }
    
    return create_visualization('doughnut', data, 'Member Engagement Distribution')


def create_geographic_chart(geo_data):
    """Create bar chart for geographic distribution"""
    # Get top 10 states by program count
    sorted_states = sorted(
        geo_data.items(),
        key=lambda x: x[1]['total_programs'],
        reverse=True
    )[:10]
    
    labels = [state for state, _ in sorted_states]
    programs = [data['total_programs'] for _, data in sorted_states]
    participants = [data['total_participants'] for _, data in sorted_states]
    
    data = {
        'labels': labels,
        'datasets': [
            {
                'label': 'Programs',
                'data': programs,
                'backgroundColor': '#3B82F6',
                'borderRadius': 5
            },
            {
                'label': 'Participants',
                'data': participants,
                'backgroundColor': '#10B981',
                'borderRadius': 5,
                'yAxisID': 'y1'
            }
        ]
    }
    
    options = {
        'scales': {
            'y': {
                'type': 'linear',
                'display': True,
                'position': 'left',
                'beginAtZero': True
            },
            'y1': {
                'type': 'linear',
                'display': True,
                'position': 'right',
                'beginAtZero': True,
                'grid': {
                    'drawOnChartArea': False
                }
            }
        }
    }
    
    return create_visualization('bar', data, 'Geographic Distribution', options)


def create_weekly_breakdown_chart(weekly_data):
    """Create bar chart for weekly breakdown"""
    labels = list(weekly_data.keys())
    values = list(weekly_data.values())
    
    data = {
        'labels': labels,
        'datasets': [{
            'label': 'Programs',
            'data': values,
            'backgroundColor': '#8B5CF6',
            'borderRadius': 5
        }]
    }
    
    return create_visualization('bar', data, 'Weekly Program Breakdown')


def create_location_effectiveness_chart(location_data):
    """Create horizontal bar chart for location effectiveness"""
    # Get top 10 locations
    sorted_locations = sorted(
        location_data.items(),
        key=lambda x: x[1]['effectiveness_score'],
        reverse=True
    )[:10]
    
    labels = [loc for loc, _ in sorted_locations]
    scores = [data['effectiveness_score'] for _, data in sorted_locations]
    
    data = {
        'labels': labels,
        'datasets': [{
            'label': 'Effectiveness Score',
            'data': scores,
            'backgroundColor': '#10B981',
            'borderRadius': 5
        }]
    }
    
    options = {
        'indexAxis': 'y',
        'scales': {
            'x': {
                'beginAtZero': True
            }
        }
    }
    
    return create_visualization('bar', data, 'Location Effectiveness', options)


# Plotly-based visualizations (for more advanced charts)
def create_plotly_heatmap(data, title="Activity Heatmap"):
    """Create heatmap using Plotly"""
    try:
        import plotly.graph_objects as go
        
        fig = go.Figure(data=go.Heatmap(
            z=data.get('values', []),
            x=data.get('x_labels', []),
            y=data.get('y_labels', []),
            colorscale='Viridis'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=data.get('x_title', 'X Axis'),
            yaxis_title=data.get('y_title', 'Y Axis')
        )
        
        return fig.to_json()
    except ImportError:
        print("Plotly not installed. Install with: pip install plotly")
        return json.dumps({})
    except Exception as e:
        print(f"Error creating heatmap: {e}")
        return json.dumps({})


def create_plotly_scatter(data, title="Scatter Plot"):
    """Create scatter plot using Plotly"""
    try:
        import plotly.graph_objects as go
        
        fig = go.Figure(data=go.Scatter(
            x=data.get('x', []),
            y=data.get('y', []),
            mode='markers',
            marker=dict(
                size=data.get('sizes', 10),
                color=data.get('colors', '#3B82F6'),
                opacity=0.7
            ),
            text=data.get('labels', []),
            hovertemplate='<b>%{text}</b><br>X: %{x}<br>Y: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=data.get('x_title', 'X Axis'),
            yaxis_title=data.get('y_title', 'Y Axis'),
            hovermode='closest'
        )
        
        return fig.to_json()
    except ImportError:
        print("Plotly not installed. Install with: pip install plotly")
        return json.dumps({})
    except Exception as e:
        print(f"Error creating scatter plot: {e}")
        return json.dumps({})
