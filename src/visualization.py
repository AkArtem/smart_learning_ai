import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_sessions_over_time(df, ax=None):
    if df.empty:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'No data', ha='center')
        return fig
    s = df.set_index('start_timestamp').resample('W')['duration_minutes'].sum()
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()
    ax.plot(s.index, s.values, marker='o')
    ax.set_title('Study Minutes per Week')
    ax.set_xlabel('Week')
    ax.set_ylabel('Minutes')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    fig.tight_layout()
    return fig


def plot_focus_distribution(df, ax=None):
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()
    ax.hist(df['focus_level'].dropna(), bins=range(1, 7), align='left', rwidth=0.8)
    ax.set_title('Focus Level Distribution')
    ax.set_xlabel('Focus Level')
    ax.set_ylabel('Count')
    fig.tight_layout()
    return fig


def plot_subject_breakdown(df, ax=None):
    grouped = df.groupby('subject_name')['duration_minutes'].sum()
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()
    if grouped.empty:
        ax.text(0.5, 0.5, 'No data', ha='center')
    else:
        grouped.plot.pie(ax=ax, autopct='%1.1f%%')
    ax.set_ylabel('')
    ax.set_title('Time Spent per Subject')
    fig.tight_layout()
    return fig


def plot_dashboard(df):
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    plot_sessions_over_time(df, axs[0, 0])
    plot_focus_distribution(df, axs[0, 1])
    plot_subject_breakdown(df, axs[1, 0])
    axs[1, 1].axis("off")
    fig.tight_layout()
    return fig