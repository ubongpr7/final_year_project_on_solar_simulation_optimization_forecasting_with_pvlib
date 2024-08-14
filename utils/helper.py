import pandas as pd
import plotly.express as px
import plotly.colors as colors

def generate_plot(y, df, plot_type='line', title=None, labels=None, color='#1f77b4'):
    """
    Generate a Plotly graph based on the provided parameters with dynamic titles and labels.

    Parameters:
    - y: Data for the y-axis (or values for pie chart)
    - plot_type: Type of plot ('line', 'scatter', 'bar', 'area', 'histogram', 'box', 'violin', 'pie', 'density_contour', 'funnel')
    - title: Title of the plot (Optional)
    - labels: Dictionary with 'x' and 'y' keys for axis labels (Optional)
    - color: Color of the plot elements

    Returns:
    - fig: Plotly figure object
    """
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    # Add a month column
    df['month'] = df.index.month_name()

    # Convert the 'month' column to a categorical type with the proper order
    df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)

    # Sort the DataFrame by the categorical month column
    df_sorted = df.sort_values('month')

    monthly_avg = df_sorted.groupby('month')[y].mean().reset_index()

    color_scale = colors.qualitative.Set1
    month_colors = dict(zip(df_sorted['month'].unique(), color_scale))

    # Generate titles and labels based on the plot type and y variable
    if title is None:
        title = f'{plot_type.capitalize()} of {y}'

    if labels is None:
        labels = {'x': 'Date', 'y': y.capitalize()}

    # Modify labels based on the plot type
    if plot_type == 'line':
        title = f'Time Series of {y}'
        labels = {'x': 'Date', 'y': y.capitalize()}

    elif plot_type == 'scatter':
        title = f'Scatter Plot of {y} by Month'
        labels = {'x': 'Date', 'y': y.capitalize()}

    elif plot_type == 'area':
        title = f'Cumulative Area of {y} Over Time'
        labels = {'x': 'Date', 'y': f'Cumulative {y.capitalize()}'}

    elif plot_type == 'bar':
        title = f'Bar Plot of {y} Over Time'
        labels = {'x': 'Date', 'y': y.capitalize()}

    elif plot_type == 'histogram':
        title = f'Histogram of {y}'
        labels = {'x': y.capitalize(), 'y': 'Frequency'}

    elif plot_type == 'box':
        title = f'Box Plot of {y} by Month'
        labels = {'x': 'Month', 'y': y.capitalize()}

    elif plot_type == 'violin':
        title = f'Violin Plot of {y} by Month'
        labels = {'x': 'Month', 'y': y.capitalize()}

    elif plot_type == 'pie':
        title = f'Pie Chart of {y} by Month'
        labels = {'x': 'Month', 'y': y.capitalize()}

    elif plot_type == 'heatmap':
        title = f'Heatmap of {y}'
        labels = {'x': 'Month', 'y': 'Month'}

    elif plot_type == 'density_contour':
        title = f'Density Contour Plot of {y}'
        labels = {'x': 'X-Axis', 'y': y.capitalize()}

    elif plot_type == 'funnel':
        title = f'Funnel Plot of {y}'
        labels = {'x': 'X-Axis', 'y': y.capitalize()}

    else:
        raise ValueError(f"Unknown plot_type: {plot_type}")
    
    # Generate the appropriate plot based on the plot type
    if plot_type == 'line':
        fig = px.line(df_sorted, x=df_sorted.index, y=df_sorted[y], title=title, labels=labels)
        fig.update_traces(line=dict(color=color))

    elif plot_type == 'scatter':
        fig = px.scatter(df_sorted, x=df_sorted.index, y=df_sorted[y], color='month', color_discrete_sequence=color_scale, title=title, labels=labels)

    elif plot_type == 'area':
        fig = px.area(df_sorted, x=df_sorted.index, y=df_sorted[y], title=title, labels=labels)
        fig.update_traces(line=dict(color=color))

    elif plot_type == 'bar':
        fig = px.bar(df_sorted, x=df_sorted.index, y=df_sorted[y], title=title, labels=labels, barmode='group')
        fig.update_traces(marker=dict(color=color))

    elif plot_type == 'histogram':
        fig = px.histogram(df_sorted, x=y, nbins=20, title=title, labels=labels)

    elif plot_type == 'box':
        fig = px.box(df_sorted, x='month', y=y, color='month', color_discrete_sequence=color_scale, title=title, labels=labels)

    elif plot_type == 'violin':
        fig = px.violin(df_sorted, x='month', y=y, color='month', color_discrete_sequence=color_scale, title=title, labels=labels)

    elif plot_type == 'pie':
        fig = px.pie(monthly_avg, values=y, names='month', title=title)

    elif plot_type == 'heatmap':
        z = df_sorted.pivot(index='month', columns='month', values=y)
        fig = px.imshow(z, color_continuous_scale='Viridis', title=title)

    elif plot_type == 'density_contour':
        fig = px.density_contour(df_sorted, title=title, labels=labels)
        fig.update_traces(contours_coloring="fill", colorscale=[[0, color], [1, color]])

    elif plot_type == 'funnel':
        fig = px.funnel(df_sorted, title=title, labels=labels)
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
