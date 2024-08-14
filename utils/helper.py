import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as colors
import pandas as pd

def generate_plot(y, df, plot_type='line', title='Plot', labels=None, color='#1f77b4'):
    """
    Generate a Plotly graph based on the provided parameters.

    Parameters:
    - y: Data for the y-axis (or values for pie chart)
    - plot_type: Type of plot ('line', 'scatter', 'bar', 'area', 'histogram', 'box', 'violin', 'pie', 'density_contour', 'funnel')
    - title: Title of the plot
    - labels: Dictionary with 'x' and 'y' keys for axis labels
    - color: Color of the plot elements

    Returns:
    - fig: Plotly figure object
    """
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    df['month'] = df.index.month_name()
    monthly_avg = df.groupby('month')[y].mean().reset_index()
    monthly_avg['month'] = pd.Categorical(monthly_avg['month'], categories=month_order, ordered=True)
    monthly_avg = monthly_avg.sort_values('month')

    color_scale = colors.qualitative.Set1
    month_colors = dict(zip(df['month'].unique(), color_scale))

    if labels is None:
        labels = {'x': 'X-Axis', 'y': 'Y-Axis'}

    if plot_type == 'line':
        fig = px.line(df, x=df.index, y=df[y], title=title, labels=labels)
        fig.update_traces(line=dict(color=color))

    elif plot_type == 'scatter':
        fig = px.scatter(df, x=df.index, y=df[y], color='month', color_discrete_sequence=color_scale, title=title, labels=labels)

    elif plot_type == 'area':
        fig = px.area(df, x=df.index, y=df[y], title=title, labels=labels)
        fig.update_traces(line=dict(color=color))

    elif plot_type == 'bar':
        fig = px.bar(df, x=df.index, y=df[y], title=title, labels=labels, barmode='group')
        fig.update_traces(marker=dict(color=color))

    elif plot_type == 'histogram':
        fig = px.histogram(df, x=y, nbins=20, title=title, labels=labels)

    elif plot_type == 'box':
        fig = px.box(df, x='month', y=y, color='month', color_discrete_sequence=color_scale, title=title, labels=labels)

    elif plot_type == 'violin':
        fig = px.violin(df, x='month', y=y, color='month', color_discrete_sequence=color_scale, title=title, labels=labels)

    elif plot_type == 'pie':
        fig = px.pie(monthly_avg, values=y, names='month', title=title)

    elif plot_type == 'heatmap':
        z = df.pivot(index='month', columns='month', values=y)
        fig = px.imshow(z, color_continuous_scale='Viridis', title='Heatmap')

    elif plot_type == 'density_contour':
        fig = px.density_contour(df, title=title, labels=labels)
        fig.update_traces(contours_coloring="fill", colorscale=[[0, color], [1, color]])

    elif plot_type == 'funnel':
        fig = px.funnel(df, title=title, labels=labels)
        fig.update_traces(marker=dict(color=color))

    else:
        raise ValueError(f"Unknown plot_type: {plot_type}")
    
    fig.update_layout(
        title=title,
        xaxis_title=labels.get('x', 'X-Axis'),
        yaxis_title=labels.get('y', 'Y-Axis'),
        height=700,
    )

    return fig
