import boto3
import datetime as dt
import pandas as pd

# Create CloudWatch client
cloudwatch_client = boto3.client('cloudwatch','us-east-1')

# Initialize parameters
loadbalancer = 'app/my-load-balancer/0406285615e79d85'
targetgroup1 = 'targetgroup/target-cluster-1/cab25a14a6222f11'
targetgroup2 = 'targetgroup/target-cluster-2/be64b91feed2f0b7'
metrics = ['TargetResponseTime', 'RequestCount', 'HealthyHostCount', 'UnHealthyHostCount', 'TargetConnectionErrorCount', 'RequestCountPerTarget', 'HTTPCode_Target_2XX_Count', 'HTTPCode_Target_3XX_Count', 'HTTPCode_Target_4XX_Count', 'HTTPCode_Target_5XX_Count']
statistics = ['Average','Sum']

# Create a function to get_metrics using paginator and get_metric_data
def function_metric_data(id, metricname, targetgroupvalue, loadbalancervalue, stat):
    paginator=cloudwatch_client.get_paginator('get_metric_data')
    for response in paginator.paginate(
        MetricDataQueries=[
            {
                'Id': id,
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': metricname,
                        'Dimensions': [
                                {
                                    'Name':'TargetGroup',
                                    'Value':targetgroupvalue
                                },
                                {
                                    'Name':'LoadBalancer',
                                    'Value':loadbalancervalue
                                },
                        ]
                    },        
                    'Period': 60,
                    'Stat': stat,
                    #'Unit': 'Seconds'
                },
                'ReturnData': True
            },
        ],
        StartTime=dt.datetime(2022, 10, 12, 0), #tzinfo=pytz.timezone('EST')),
        EndTime=dt.datetime(2022, 10, 14, 23), #tzinfo=pytz.timezone('EST')),
        ScanBy='TimestampDescending'
        ):

        # Print result as a Dataframe
        print(f'\n Result for request on {metricname}, statistics: {stat}, for cluster: {targetgroupvalue}')
        result = response['MetricDataResults'][0]
        del result[list(result.keys())[-1]] # Keep columns "id", "label", "timestamps" and "values"
        tbl_result = pd.DataFrame(result)
        
        return print(tbl_result)

# Get all metrics for cluster No 1
#for metric in metrics[0:2]:
    #for statistic in statistics:
        #function_metric_data('rqt_cluster1', metric, targetgroup1, loadbalancer, statistic)

# Get all metrics for cluster No 2
for metric in metrics:
    for statistic in statistics:
        function_metric_data('rqt_cluster2', metric, targetgroup2, loadbalancer, statistic)




   