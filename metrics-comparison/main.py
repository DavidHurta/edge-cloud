#
# A python application to generate reports of metrics that are gathered in a MySQL database.
#
# Author: David Hurta
#

"""
Module providing tooling to generate reports of metrics
that are gathered in a running MySQL database.

Required environment variables are:
DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE
"""

import logging
import os
import sys
from datetime import datetime

import numpy
import pandas
import seaborn
import scipy.stats
import sqlalchemy
import scikit_posthocs
import matplotlib.pyplot as plt

from matplotlib.colors import Colormap
from pandas.io.formats.style import Styler
from statannotations.Annotator import Annotator

TABLE = "metrics"

TYPE_NODES_CPU = "nodes_cpu"
TYPE_NODES_MEMORY = "nodes_memory"
TYPE_CONTAINERS_CPU = "containers_cpu"
TYPE_CONTAINERS_MEMORY = "containers_memory"
TYPE_ALL = [TYPE_NODES_CPU, TYPE_NODES_MEMORY, TYPE_CONTAINERS_CPU, TYPE_CONTAINERS_MEMORY]

NODE_NAMES = ["control-plane", "cloud", "edge", "infra"]
CONTAINERS_NAMES = [
    "app-cloud",
    "kafka-cloud",
    "app-edge",
    "app-sensor",
    "kafka-edge",
    "kafka-ui",
    "kafka-mirror",
]

ORDER_OF_TECHNOLOGIES = ["k3s", "microk8s", "kubernetes", "kubeedge"]

ANNOTATIONS = {
    TYPE_NODES_CPU: {
        "x": "Technology",
        "y": "[%]",
        "filename": "node-cpu-usage",
        "title": "Node CPU Usage",
    },
    TYPE_NODES_MEMORY: {
        "x": "Technology",
        "y": "[%]",
        "filename": "node-memory-usage",
        "title": "Node Memory Usage",
    },
    TYPE_CONTAINERS_CPU: {
        "x": "Technology",
        "y": "[millicores]",
        "filename": "container-cpu-usage",
        "title": "Container CPU Usage",
    },
    TYPE_CONTAINERS_MEMORY: {
        "x": "Technology",
        "y": "[MB]",
        "filename": "container-memory-usage",
        "title": "Container Memory Usage",
    },
}


def get_database_connection() -> sqlalchemy.Engine:
    """
    get_database_connection returns an engine instance, which is
    usable in the `pandas.read_sql` function as a connection.
    """
    try:
        user = os.environ['DB_USER']
        password = os.environ['DB_PASSWORD']
        host = os.environ['DB_HOST']
        port = os.environ['DB_PORT']
        database = os.environ['DB_DATABASE']
    except KeyError:
        logging.error("one of the following environment variables is not set: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE")
        sys.exit(1)
    return sqlalchemy.create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")


def custom_styler(styler: Styler, cmap: Colormap, caption: str) -> Styler:
    """
    custom_styler returns a pre-defined custom styler. Background
    gradient to visualize minimal and maximal values across rows is applied.

    Args:
        styler (Styler): styler to be modified.
        cmap (Colormap): color map to be applied for a background gradient.
        caption (str): caption to be applied.

    Returns:
        Styler: modified styler.
    """
    styler.format(precision=3)
    styler.set_caption(caption)
    styler.background_gradient(cmap=cmap, axis='columns')
    styler.set_table_styles([
        {'selector': 'caption', 'props': 'font-family: monospace;'},
        {'selector': 'th.col_heading', 'props': 'font-family: monospace;'},
        {'selector': 'th.row_heading', 'props': 'font-family: monospace; text-align: left;'},
    ])
    styler.set_properties(**{
        'font-family': 'monospace',
        'width': '8em',
        'text-align': 'center',
    })
    return styler


def generate_summaries_statistical_measurements(dataframe: pandas.DataFrame, directory: str):
    """generate_summaries_statistical_measurements generates HTML summaries of statistical measurements.

    Args:
        dataframe (pandas.DataFrame): The data of the metrics.
        directory (str): Desired directory for the reports.
    """
    groupby = dataframe.groupby(['Technology', "Source", "MetricType"])['Value']
    medians = groupby.median()
    std = groupby.std()  # Standard Variance
    mad = groupby.apply(lambda x: (x - x.median()).abs().median())  # Median Absolute Deviation

    for source in NODE_NAMES + CONTAINERS_NAMES:
        for i, metric_type in enumerate(TYPE_ALL):
            if (metric_type in [TYPE_NODES_CPU, TYPE_NODES_MEMORY] and source in CONTAINERS_NAMES) or \
               (metric_type in [TYPE_CONTAINERS_CPU, TYPE_CONTAINERS_MEMORY] and source in NODE_NAMES):
                continue
            df = dataframe.loc[dataframe['MetricType'] == metric_type]
            x_orig = df.loc[df['Source'].isin([source])]
            x = x_orig.groupby(["Technology", "Source"])["Value"]

            print(f"**************** {metric_type}-{source} ****************")

            # Calculate Kruskal-Wallis H-test
            groups = [group.values for _, group in x]

            is_data_normal = True
            for group in groups:
                h_value, p_value = scipy.stats.shapiro(group)
                print(f"SHAPIRO={h_value:.3f}, p={p_value:.3f}")
                if p_value > 0.05:
                    print(f"Group {i}: Data looks normal.")
                else:
                    is_data_normal = False
                    print(f"Group {i}: Data does NOT look normal.")

            is_equal_variance = True
            h_value, p_value = scipy.stats.levene(*groups)
            print(f"LEVENE={h_value:.3f}, p={p_value:.3f}")
            if p_value > 0.05:
                print(f"Group {i}: Data do have equal variance.")
            else:
                is_equal_variance = False
                print(f"Group {i}: Data do NOT have equal variance.")

            title_suffix = ""
            if is_data_normal and is_equal_variance:
                h_value, p_value = scipy.stats.f_oneway(*groups)
                print(f"H={h_value:.3f}, p={p_value:.3f}")
                title_suffix = "One-way ANOVA"
            else:
                h_value, p_value = scipy.stats.kruskal(*groups)
                title_suffix = "Kruskal-Wallis"
                print(f"H={h_value:.3f}, p={p_value:.3f}")

            # Check for significance
            skip_posthoc = False
            if p_value > 0.05:
                print("No significant difference - skipping posthoc tests")
                title_suffix = f"No Significant Difference Among the Groups — {title_suffix}"
                skip_posthoc = True

            # Calculate Post Hoc test
            if skip_posthoc:
                seaborn.set_theme(rc={'axes.facecolor': seaborn.xkcd_rgb['light rose'], 'figure.facecolor': seaborn.xkcd_rgb['light rose']})
                ax = seaborn.boxplot(data=x_orig, x="Technology", y="Value", order=ORDER_OF_TECHNOLOGIES)
            else:
                seaborn.set_theme()

                if is_data_normal and is_equal_variance:
                    posthoc = scikit_posthocs.posthoc_tukey_hsd(x_orig, val_col='Value', group_col='Technology')
                    title_suffix += " + Tukey HSD"
                    print(posthoc)
                else:
                    posthoc = scikit_posthocs.posthoc_dunn(x_orig, val_col='Value', group_col='Technology', p_adjust='bonferroni')
                    title_suffix += " + Dunn"
                    print(posthoc)

                # Extract pairs and p-values of the pairs for the statannotations.annotator
                # Based on https://blog.4dcu.be/programming/2021/12/30/Posthoc-Statannotations.html by Sebastian Proost
                remove = numpy.tril(numpy.ones(posthoc.shape), k=0).astype("bool")
                posthoc[remove] = numpy.nan
                posthoc_molten = posthoc.melt(ignore_index=False).reset_index().dropna()
                pairs = [(i[1]["index"], i[1]["variable"]) for i in posthoc_molten.iterrows()]
                p_values = [i[1]["value"] for i in posthoc_molten.iterrows()]

                # Generate box plot graph
                ax = seaborn.boxplot(data=x_orig, x="Technology", y="Value", order=ORDER_OF_TECHNOLOGIES)

                # Annotate p-values
                annotator = Annotator(
                    ax, pairs, data=df, x="Technology", y="Value", order=ORDER_OF_TECHNOLOGIES
                )
                annotator.configure(text_format="simple", loc="inside", hide_non_significant=True)
                annotator.set_pvalues_and_annotate(p_values)

            # Annotate figure
            annot = ANNOTATIONS[metric_type]
            plt.title(f"{annot['title']} — {source}\n({title_suffix})")
            plt.xlabel(annot['x'])
            plt.ylabel(annot['y'])
            plt.tight_layout()
            plt.savefig(f"{directory}/statistics-{annot['filename']}-{source}.pdf")
            plt.close()

    cmap = seaborn.diverging_palette(130, 10, as_cmap=True)
    with open(f"{directory}/summary.html", "w", encoding="utf-8") as file:
        for metric_type in [TYPE_NODES_CPU, TYPE_NODES_MEMORY, TYPE_CONTAINERS_CPU, TYPE_CONTAINERS_MEMORY]:
            for data, type_str in [(medians, "Median"), (mad, "Median Absolute Deviation"), (std, "Standard Deviation")]:
                df = data.reset_index()
                df = df.loc[df['MetricType'] == metric_type]
                df = df.loc[df['Source'].isin(CONTAINERS_NAMES + NODE_NAMES)]
                df = df.drop(columns=['MetricType'])
                df = df.pivot(index='Source', columns='Technology', values='Value')
                df = df.rename_axis(None, axis=0)
                df = df.rename_axis(None, axis=1)
                df = df.loc[:, ORDER_OF_TECHNOLOGIES]

                if metric_type in [TYPE_NODES_CPU, TYPE_NODES_MEMORY]:
                    df = df.reindex(axis="index", level=0, labels=NODE_NAMES)
                elif metric_type in [TYPE_CONTAINERS_CPU, TYPE_CONTAINERS_MEMORY]:
                    df = df.reindex(axis="index", level=0, labels=CONTAINERS_NAMES)

                if metric_type == TYPE_NODES_CPU:
                    custom_styler(df.style, cmap, f"Nodes CPU Usage [%] — {type_str}").to_html(file)
                elif metric_type == TYPE_NODES_MEMORY:
                    custom_styler(df.style, cmap, f"Nodes Memory Usage [%] — {type_str}").to_html(file)
                elif metric_type == TYPE_CONTAINERS_CPU:
                    custom_styler(df.style, cmap, f"Containers CPU Usage [millicores] — {type_str}").to_html(file)
                elif metric_type == TYPE_CONTAINERS_MEMORY:
                    custom_styler(df.style, cmap, f"Containers Memory Usage [MB] — {type_str}").to_html(file)

                file.write("<br>")  # Add a new line to separate better the written tables


def generate_statistical_reports(dataframe: pandas.DataFrame, directory: str):
    """generate_statistical_reports executes statistical tests to generate reports
        using box plots and p-values of corresponding comparison tests.

    Args:
        dataframe (pandas.DataFrame): The data of the metrics.
        directory (str): Desired directory for the reports.
    """
    for source in NODE_NAMES + CONTAINERS_NAMES:
        for i, metric_type in enumerate(TYPE_ALL):
            if (metric_type in [TYPE_NODES_CPU, TYPE_NODES_MEMORY] and source in CONTAINERS_NAMES) or \
               (metric_type in [TYPE_CONTAINERS_CPU, TYPE_CONTAINERS_MEMORY] and source in NODE_NAMES):
                continue
            df = dataframe.loc[dataframe['MetricType'] == metric_type]
            x_orig = df.loc[df['Source'].isin([source])]
            x = x_orig.groupby(["Technology", "Source"])["Value"]

            print(f"**************** {metric_type}-{source} ****************")

            # Calculate Kruskal-Wallis H-test
            groups = [group.values for _, group in x]

            is_data_normal = True
            for group in groups:
                h_value, p_value = scipy.stats.shapiro(group)
                print(f"SHAPIRO={h_value:.3f}, p={p_value:.3f}")
                if p_value > 0.05:
                    print(f"Group {i}: Data looks normal.")
                else:
                    is_data_normal = False
                    print(f"Group {i}: Data does NOT look normal.")

            is_equal_variance = True
            h_value, p_value = scipy.stats.levene(*groups)
            print(f"LEVENE={h_value:.3f}, p={p_value:.3f}")
            if p_value > 0.05:
                print(f"Group {i}: Data do have equal variance.")
            else:
                is_equal_variance = False
                print(f"Group {i}: Data do NOT have equal variance.")

            title_suffix = ""
            if is_data_normal and is_equal_variance:
                h_value, p_value = scipy.stats.f_oneway(*groups)
                print(f"H={h_value:.3f}, p={p_value:.3f}")
                title_suffix = "One-way ANOVA"
            else:
                h_value, p_value = scipy.stats.kruskal(*groups)
                title_suffix = "Kruskal-Wallis"
                print(f"H={h_value:.3f}, p={p_value:.3f}")

            # Check for significance
            skip_posthoc = False
            if p_value > 0.05:
                print("No significant difference - skipping posthoc tests")
                title_suffix = f"No Significant Difference Among the Groups — {title_suffix}"
                skip_posthoc = True

            # Calculate Post Hoc test
            if skip_posthoc:
                seaborn.set_theme(rc={'axes.facecolor': seaborn.xkcd_rgb['light rose'], 'figure.facecolor': seaborn.xkcd_rgb['light rose']})
                ax = seaborn.boxplot(data=x_orig, x="Technology", y="Value", order=ORDER_OF_TECHNOLOGIES)
            else:
                seaborn.set_theme()

                if is_data_normal and is_equal_variance:
                    posthoc = scikit_posthocs.posthoc_tukey_hsd(x_orig, val_col='Value', group_col='Technology')
                    title_suffix += " + Tukey HSD"
                    print(posthoc)
                else:
                    posthoc = scikit_posthocs.posthoc_dunn(x_orig, val_col='Value', group_col='Technology', p_adjust='bonferroni')
                    title_suffix += " + Dunn"
                    print(posthoc)

                # Extract pairs and p-values of the pairs for the statannotations.annotator
                # Based on https://blog.4dcu.be/programming/2021/12/30/Posthoc-Statannotations.html by Sebastian Proost
                remove = numpy.tril(numpy.ones(posthoc.shape), k=0).astype("bool")
                posthoc[remove] = numpy.nan
                posthoc_molten = posthoc.melt(ignore_index=False).reset_index().dropna()
                pairs = [(i[1]["index"], i[1]["variable"]) for i in posthoc_molten.iterrows()]
                p_values = [i[1]["value"] for i in posthoc_molten.iterrows()]

                # Generate box plot graph
                ax = seaborn.boxplot(data=x_orig, x="Technology", y="Value", order=ORDER_OF_TECHNOLOGIES)

                # Annotate p-values
                annotator = Annotator(
                    ax, pairs, data=df, x="Technology", y="Value", order=ORDER_OF_TECHNOLOGIES
                )
                annotator.configure(text_format="simple", loc="inside", hide_non_significant=True)
                annotator.set_pvalues_and_annotate(p_values)

            # Annotate figure
            annot = ANNOTATIONS[metric_type]
            plt.title(f"{annot['title']} — {source}\n({title_suffix})")
            plt.xlabel(annot['x'])
            plt.ylabel(annot['y'])
            plt.tight_layout()
            plt.savefig(f"{directory}/statistics-{annot['filename']}-{source}.pdf")
            plt.close()


def generate_reports(connection: sqlalchemy.Engine, directory: str):
    """
    generate_reports generates reports from a MySQL database data into a directory.

    Arguments:
        connection (sqlalchemy.Engine): Connection instance to the MySQL database.
        directory (str): Desired directory for the reports.
    """
    for name in NODE_NAMES:
        # Nodes CPU Usage
        query = f"SELECT * FROM {TABLE} WHERE SOURCE='{name}' AND METRICTYPE='{TYPE_NODES_CPU}'"
        dataframe = pandas.read_sql(query, con=connection)

        seaborn.boxplot(x="Technology", y="Value", data=dataframe, order=ORDER_OF_TECHNOLOGIES)
        plt.title(f"{name.title()} Node CPU Usage")
        plt.xlabel("Technology")
        plt.ylabel("[%]")
        plt.savefig(f"{directory}/node-cpu-{name}.pdf")
        plt.close()

        # Nodes Memory Usage
        query = f"SELECT * FROM {TABLE} WHERE SOURCE='{name}' AND METRICTYPE='{TYPE_NODES_MEMORY}'"
        dataframe = pandas.read_sql(query, con=connection)

        seaborn.boxplot(x="Technology", y="Value", data=dataframe, order=ORDER_OF_TECHNOLOGIES)
        plt.title(f"{name.title()} Node Memory Usage")
        plt.xlabel("Technology")
        plt.ylabel("[%]")
        plt.savefig(f"{directory}/node-memory-{name}.pdf")
        plt.close()

    for name in CONTAINERS_NAMES:
        # Containers CPU Usage
        query = f"SELECT * FROM {TABLE} WHERE SOURCE='{name}' AND METRICTYPE='{TYPE_CONTAINERS_CPU}'"
        dataframe = pandas.read_sql(query, con=connection)

        seaborn.boxplot(x="Technology", y="Value", data=dataframe, order=ORDER_OF_TECHNOLOGIES)
        plt.title(f"{name.title()} Application CPU Usage")
        plt.xlabel("Technology")
        plt.ylabel("[millicores]")
        plt.savefig(f"{directory}/container-cpu-{name}.pdf")
        plt.close()

        # Containers Memory Usage
        query = f"SELECT * FROM {TABLE} WHERE SOURCE='{name}' AND METRICTYPE='{TYPE_CONTAINERS_MEMORY}'"
        dataframe = pandas.read_sql(query, con=connection)

        seaborn.boxplot(x="Technology", y="Value", data=dataframe, order=ORDER_OF_TECHNOLOGIES)
        plt.title(f"{name.title()} Application Memory Usage")
        plt.xlabel("Technology")
        plt.ylabel("[MB]")
        plt.savefig(f"{directory}/container-memory-{name}.pdf")
        plt.close()


def main():
    """
    main generates reports of metrics to a local directory.
    """
    connection = get_database_connection()

    directory = os.path.join("_output", datetime.now().isoformat())
    if not os.path.isdir(directory):
        os.makedirs(directory)
    else:
        logging.warning("The directory %s already exists!", directory)
        sys.exit(1)

    generate_reports(connection, directory)

    query = f"SELECT * FROM {TABLE}"
    dataframe = pandas.read_sql(query, con=connection)
    generate_statistical_reports(dataframe, directory)
    generate_summaries_statistical_measurements(dataframe, directory)


if __name__ == "__main__":
    main()
