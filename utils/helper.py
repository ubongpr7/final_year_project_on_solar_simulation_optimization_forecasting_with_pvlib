import plotly.express as px
import plotly.colors as colors
import pandas as pd
from scipy.stats import linregress


def df_sample_to_bootstrap_cards(df):
    html_table = df.sample(n=12).to_html(classes='table table-striped')

    # Wrap the table in a div with overflow styling
    html = f'''
    <div style="overflow-x: auto;">
        {html_table}
        Shape: {df.shape}
    </div>
    '''
    return html



def generate_correlation_plot_with_regression(x_col, y_col, df, plot_type='scatter', location=None, color='#1f77b4'):
    """
    Generate a Plotly scatter plot with a correlation line (regression line).

    Parameters:
    - x_col: Column name for the x-axis.
    - y_col: Column name for the y-axis.
    - df: DataFrame containing the data.
    - plot_type: Type of plot ('scatter' with regression line).
    - color: Color of the scatter plot elements.

    Returns:
    - fig: Plotly figure object with a regression line.
    """
    if plot_type != 'scatter':
        raise ValueError("Currently only 'scatter' plot with regression line is supported.")
    
    # Scatter plot
    fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col} for {location}")
    
    # Calculate linear regression
    x = df[x_col]
    y = df[y_col]
    slope, intercept, r_value, p_value, std_err = linregress(x, y)

    # Calculate the regression line
    regression_line = slope * x + intercept
    
    # Add the regression line to the scatter plot
    fig.add_traces(px.line(df, x=x_col, y=regression_line).data)
    
    # Customize the layout
    fig.update_layout(
        title=f"{y_col.title()} vs {x_col.title()} with Regression Line for {location}",
        xaxis_title=x_col,
        yaxis_title=y_col,
        height=600
    )

    return fig


def generate_plot(y, df, plot_type='line',location=None, labels=None, color='#1f77b4'):
    """
    Generate a Plotly graph based on the provided parameters.

    Parameters:
    - y: Data for the y-axis (or values for pie chart)
    - df: DataFrame containing the data
    - plot_type: Type of plot ('line', 'scatter', 'bar', 'area', 'histogram', 'box', 'violin', 'pie', 'density_contour', 'funnel')
    - color: Color of the plot elements

    Returns:
    - fig: Plotly figure object
    """
    # Assigning month names based on the index
    df['month'] = df.index.month_name()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)

    # Create a dictionary mapping month names to colors
    color_scale = colors.qualitative.Set1
    month_colors = dict(zip(df['month'].unique(), color_scale))

    # Calculate monthly average once
    # monthly_avg = df.groupby('month')[y].mean().reset_index()
    monthly_avg = df.groupby('month', observed=False)[y].mean().reset_index()

    # Titles and labels based on the plot type and y variable
    title_dict = {
        'line': f"Trend of {y.title()} Over Time ",
        'scatter': f"Scatter Plot of {y.title()} Over Time",
        'area': f"Cumulative {y.title()} Over Time",
        'bar': f"Monthly Average {y.title()}",
        'histogram': f"Distribution of {y.title()}",
        'box': f"Monthly Distribution of {y.title()}",
        'violin': f"Monthly Distribution of {y.title()}",
        'pie': f"Proportion of Monthly Average {y.title()}",
        'heatmap': f"Heatmap of {y.title()} by Month",
        'density_contour': f"Density Contour of {y.title()} Over Time",
        'funnel': f"Funnel Plot of {y.title()} Over Time"
    }

    label_dict = {
        'line': {'x': 'Date', 'y': f'{y.title()}'},
        'scatter': {'x': 'Date', 'y': f'{y.title()}'},
        'area': {'x': 'Date', 'y': f'Cumulative {y.title()}'},
        'bar': {'x': 'Month', 'y': f'Average {y.title()}'},
        'histogram': {'x': f'{y.title()}', 'y': f'Frequency of Occurence  of {y.title()}'},
        'box': {'x': 'Month', 'y': f'{y.title()}'},
        'violin': {'x': 'Month', 'y': f'{y.title()}'},
        'pie': {'x': 'Month', 'y': f'Proportion of {y.title()}'},
        'heatmap': {'x': 'Month', 'y': 'Month'},
        'density_contour': {'x': 'Date', 'y': f'{y.title()}'},
        'funnel': {'x': 'Date', 'y': f'{y.title()}'}
    }

    title = title_dict.get(plot_type, f"{y.title()} vs Time for {location}")
    labels = label_dict.get(plot_type, {'x': 'Date', 'y': y.title()})

    # Create plots
    if plot_type == 'line':
        fig = px.line(df, x=df.index, y=df[y], title=title, labels=labels)
        fig.update_traces(line=dict(color=color))
    elif plot_type == 'scatter':
        fig = px.scatter(df, x=df.index, y=df[y], color='month', color_discrete_map=month_colors, title=title, labels=labels)
    elif plot_type == 'area':
        fig = px.area(df, x=df.index, y=df[y], title=title, labels=labels)
        fig.update_traces(line=dict(color=color))
    elif plot_type == 'bar':
        fig = px.bar(monthly_avg, x='month',color='month', color_discrete_map=month_colors, y=y, title=title, labels=labels)
        # fig.update_traces(line=dict(color=color))

    elif plot_type == 'histogram':
        fig = px.histogram(df, x=y, nbins=20, title=title, labels=labels)
    elif plot_type == 'box':
        fig = px.box(df, x='month', y=y, color='month', color_discrete_map=month_colors, title=title, labels=labels)
    elif plot_type == 'violin':
        fig = px.violin(df, x='month', y=y, color='month', color_discrete_map=month_colors, title=title, labels=labels)
    elif plot_type == 'pie':
        fig = px.pie(monthly_avg, values=y, names='month', title=title)
    elif plot_type == 'heatmap':
        z = df.pivot_table(index='month', columns='month', values=y)
        fig = px.imshow(z, color_continuous_scale='Viridis', title=title)
    elif plot_type == 'density_contour':
        fig = px.density_contour(df, x=df.index, y=df[y], title=title, labels=labels)
        fig.update_traces(contours_coloring="fill", colorscale=[[0, color], [1, color]])
    elif plot_type == 'funnel':
        fig = px.funnel(df, x=df.index, y=df[y], title=title, labels=labels)
        fig.update_traces(marker=dict(color=color))
    else:
        raise ValueError(f"Unknown plot_type: {plot_type}")

    # Update layout
    fig.update_layout(
        title=f"{title} for {location} \n Source: Open-Meteo",
        xaxis_title=labels.get('x', 'X-Axis'),
        yaxis_title=labels.get('y', 'Y-Axis'),
        height=600,
    )

    return fig
