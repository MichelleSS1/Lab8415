import os
import sys
import re
import boto3
import datetime as dt
import pandas as pd
import pytz
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from log8415_utils.infra_utils import get_infra_info

# Create CloudWatch client
cloudwatch_client = boto3.client('cloudwatch')

CLUSTER1_QUERY_ID = 'rqt_cluster1'
CLUSTER2_QUERY_ID = 'rqt_cluster2'


# Create a function to get_metrics using paginator and get_metric_data
def collect_lb_metric_data(id:str, metric_name:str, target_group:str, load_balancer:str, stat:str):
    """
    Collect Application load balancer cloudwatch metrics from aws within last 24 hours. 
    They will be used to measure and compare each cluster performance. 

    @param id:str                       id of the query
    @param metric_name:str              name of the metric, can be selected from the aws web site (cloudwatch metrics)
    @param target_group_value:str       TargetGroup dimension value, extracted from target group arn
    @param load_balancer_value:str      LoadBalancer dimension value, extracted from the load balancer arn
    @param stat:str                     metric data aggregation over specified period of time, selected from the aws web site (cloudwatch metrics)
    
    """
    now = dt.datetime.now(pytz.timezone("America/Montreal"))

    paginator = cloudwatch_client.get_paginator('get_metric_data')

    for response in paginator.paginate(
        MetricDataQueries=[
            {
                'Id': id,
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': metric_name,
                        'Dimensions': [
                            {
                                'Name': 'TargetGroup',
                                'Value': target_group
                            },
                            {
                                'Name': 'LoadBalancer',
                                'Value': load_balancer
                            },
                        ]
                    },        
                    'Period': 60,
                    'Stat': stat,
                },
                'ReturnData': True
            },
        ],
        StartTime=now - dt.timedelta(days=1), # Last 24 hours
        EndTime=now,
        ScanBy='TimestampAscending'
    ):
        result_df = pd.DataFrame()
        if len(response['MetricDataResults']) > 0:
            result = response['MetricDataResults'][0]

            # Remove fields 'StatusCode', 'Messages' to keep 'id', 'label', 'timestamps', 'values'
            print(result)
            result.pop('StatusCode')
            result.pop('Messages', '')

            # Convert to dataframe
            result_df = pd.DataFrame(result)
            result_df = result_df.assign(Statistics = stat, Cluster = target_group)

        return result_df

def plot_metric(df:pd.DataFrame, metric_name:str, stat:str):
    """
    Create a graph comparing cluster 1 and cluster 2 over
    a given metric name and a statistic.

    @param df:pd.DataFrame      a dataframe containing values for multiple metrics and statistics
    @param metric_name:str      metric to select from the dataframe
    @param stat:str             statistic to select from the dataframe

    @plot line graph
    """

    # Filter the dataframe based on the parameters
    plot_df = df.loc[(df.Label == metric_name) & (df.Statistics == stat)]

    plot_df.Timestamps = pd.to_datetime(plot_df.Timestamps, utc=True)    

    # Define variables x, y for the graph
    x1 = plot_df[plot_df.Id == CLUSTER1_QUERY_ID].Timestamps
    x2 = plot_df[plot_df.Id == CLUSTER2_QUERY_ID].Timestamps

    y1 = plot_df[plot_df.Id == CLUSTER1_QUERY_ID].Values      
    y2 = plot_df[plot_df.Id == CLUSTER2_QUERY_ID].Values
    
    # Create the graph
    fig, axs = plt.subplots(nrows=1, ncols=2, sharey=True)#, figsize=(8, 4))

    axs[0].set_title('Cluster1')   
    axs[0].plot(x1, y1, 'o-')

    axs[1].set_title('Cluster2')
    axs[1].plot(x2, y2, 'o-')
     
    axs[0].set_ylabel(f'statistic: {stat}')
    
    fig.suptitle(metric_name)
    fig.autofmt_xdate()   
    
    # Configure the x-axis label with Dateformatter(%H:%M)
    xfmt = mdates.DateFormatter('%H:%M')

    if len(x1) == 0:
        axs[0].xaxis.set_visible(False)
    else:
        axs[0].xaxis.set_major_formatter(xfmt)

    if len(x2) == 0:
        axs[1].xaxis.set_visible(False)
    else:
        axs[1].xaxis.set_major_formatter(xfmt)

    # Save plot and show it 
    plt.savefig(os.path.join(sys.path[0], f'plots/{stat}_{metric_name}.png'), bbox_inches='tight')

    # Close the figure window
    plt.close(fig)


if __name__ == '__main__':
    # Retrieve infra information
    infra_info = get_infra_info(os.path.join(sys.path[0], '../infra/infra_info'))

    load_balancer_arn = infra_info.load_balancers_arn[0]
    target1_arn = infra_info.target_groups_arn[0]
    target2_arn = infra_info.target_groups_arn[1]

    # Get dimensions values for metrics data
    load_balancer = re.search('app.*', load_balancer_arn).group()
    target_group_1 = re.search('targetgroup.*', target1_arn).group()
    target_group_2 = re.search('targetgroup.*', target2_arn).group()

    # Metrics to get from cloudwatch
    metrics = [
        'HealthyHostCount', 
    ]


    statistics = ['Average','Sum']

    # Create table for final result
    metrics_df = pd.DataFrame()

    print("Starting metrics extraction")
    # Get all metrics for cluster No 1
    for metric in metrics:
        for statistic in statistics:
            print(f"Pulling {statistic} statistic for {metric} metric from cloudwatch")
            result_df = collect_lb_metric_data(CLUSTER1_QUERY_ID, metric, target_group_1, load_balancer, statistic)
            metrics_df = pd.concat([result_df, metrics_df], axis=0)
            
            result_df = collect_lb_metric_data(CLUSTER2_QUERY_ID, metric, target_group_2, load_balancer, statistic)
            metrics_df = pd.concat([result_df, metrics_df], axis=0)

    print("done\n")

    # Export to csv file
    print("Saving metrics to csv file metrics.csv")
    metrics_df.to_csv(os.path.join(sys.path[0], 'metrics.csv'))

    print("done\n")

    # Plot metrics
    print("Saving metrics plot")
    for metric in metrics:
        for statistic in statistics:
            plot_metric(metrics_df, metric, statistic)

    print("done")