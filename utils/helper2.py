import plotly.express as px
import plotly.colors as colors
import pandas as pd

def generate_plot(y, df, plot_type='line', title='Plot', labels=None, color='#1f77b4'):
    """
    Generate a Plotly graph based on the provided parameters.

    Parameters:
    - y: Data for the y-axis (or values for pie chart)
    - df: DataFrame containing the data
    - plot_type: Type of plot ('line', 'scatter', 'bar', 'area', 'histogram', 'box', 'violin', 'pie', 'heatmap', 'density_contour', 'funnel')
    - title: Title of the plot
    - labels: Dictionary with 'x' and 'y' keys for axis labels
    - color: Color of the plot elements

    Returns:
    - fig: Plotly figure object
    """
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    # Add a month column based on the index
    df['month'] = df.index.month_name()
    
    # Compute monthly averages
    monthly_avg = df.groupby('month')[y].mean().reset_index()
    monthly_avg['month'] = pd.Categorical(monthly_avg['month'], categories=month_order, ordered=True)
    monthly_avg = monthly_avg.sort_values('month')

    # Define color scale
    color_scale = colors.qualitative.Set1
    month_colors = dict(zip(month_order, color_scale[:len(month_order)]))

    if labels is None:
        labels = {'x': 'X-Axis', 'y': 'Y-Axis'}

    if plot_type == 'line':
        fig = px.line(df, x=df.index, y=df[y], color='month', title=title, labels=labels, color_discrete_map=month_colors)
    elif plot_type == 'scatter':
        fig = px.scatter(df, x=df.index, y=df[y], color='month', title=title, labels=labels, color_discrete_map=month_colors)
    elif plot_type == 'area':
        fig = px.area(df, x=df.index, y=df[y], color='month', title=title, labels=labels, color_discrete_map=month_colors)
    elif plot_type == 'bar':
        fig = px.bar(monthly_avg, x='month', y=y, title=title, labels=labels, color='month', color_discrete_map=month_colors, barmode='group')
    elif plot_type == 'histogram':
        fig = px.histogram(df, x=y, nbins=20, title=title, labels=labels, color_discrete_sequence=[color])
    elif plot_type == 'box':
        fig = px.box(df, x='month', y=y, title=title, labels=labels, color='month', color_discrete_map=month_colors)
    elif plot_type == 'violin':
        fig = px.violin(df, x='month', y=y, title=title, labels=labels, color='month', color_discrete_map=month_colors)
    elif plot_type == 'pie':
        fig = px.pie(monthly_avg, values=y, names='month', title=title, color_discrete_map=month_colors)
    elif plot_type == 'heatmap':
        z = df.pivot_table(index='month', columns='month', values=y)
        fig = px.imshow(z, color_continuous_scale='Viridis', title=title)
    elif plot_type == 'density_contour':
        fig = px.density_contour(df, title=title, labels=labels)
        fig.update_traces(contours_coloring="fill", colorscale=[[0, color], [1, color]])
    elif plot_type == 'funnel':
        fig = px.funnel(df, title=title, labels=labels)
    else:
        raise ValueError(f"Unknown plot_type: {plot_type}")

    fig.update_layout(
        title=title,
        xaxis_title=labels.get('x', 'X-Axis'),
        yaxis_title=labels.get('y', 'Y-Axis'),
        height=700,
    )

    return fig

def df_sample_to_bootstrap_cards(df):
    html_table = df.to_html(classes='table table-striped')

    # Wrap the table in a div with overflow styling
    html = f'''
    <div style="overflow-x: auto;">
        {html_table}
    </div>
    '''
    return html