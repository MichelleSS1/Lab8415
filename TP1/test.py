from datetime import datetime
import pytz
import boto3

client = boto3.client('cloudwatch', 'us-east-1')

paginator = client.get_paginator('get_metric_data')

for response in paginator.paginate(
    MetricDataQueries=[
        {
            'Id': 'tg_resp_time',
            'MetricStat': {
                'Metric': {
                    'Namespace': 'AWS/ApplicationELB',
                    'MetricName': 'TargetResponseTime',
                    'Dimensions': [
                        {
                            'Name': 'TargetGroup',
                            'Value': 'targetgroup/target-cluster-2/94589eaa500e6cfe'
                        },
                        {
                            'Name': 'LoadBalancer',
                            'Value': 'app/my-load-balancer/17219850b38e9411'
                        },
                    ]
                },
                'Period': 60,
                'Stat': 'Sum',
                # 'Unit': 'Seconds'|'Microseconds'|'Milliseconds'|'Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'|'Terabytes'|'Bits'|'Kilobits'|'Megabits'|'Gigabits'|'Terabits'|'Percent'|'Count'|'Bytes/Second'|'Kilobytes/Second'|'Megabytes/Second'|'Gigabytes/Second'|'Terabytes/Second'|'Bits/Second'|'Kilobits/Second'|'Megabits/Second'|'Gigabits/Second'|'Terabits/Second'|'Count/Second'|'None'
            },
            # 'Expression': 'string',
            # 'Label': 'string',
            'ReturnData': True,
            # 'Period': 123,
            # 'AccountId': 'string'
        },
    ],
    StartTime=datetime(2022, 10, 11, 0, tzinfo=pytz.timezone('EST')),
    EndTime=datetime(2022, 10, 11, 23, tzinfo=pytz.timezone('EST')),
    # NextToken='string',
    ScanBy='TimestampAscending',
    # MaxDatapoints=123,
    # LabelOptions={
    #     'Timezone': 'string'
    # }
    ):
    print(response['MetricDataResults'])

# # List metrics through the pagination interface
# paginator = client.get_paginator('list_metrics')
# for response in paginator.paginate():
#     print(response['Metrics'])