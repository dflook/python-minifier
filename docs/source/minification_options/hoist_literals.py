def validate(arn, props):
    if 'ValidationMethod' in props and props['ValidationMethod'] == 'DNS':

        all_records_created = False
        while not all_records_created:
            all_records_created = True

            certificate = acm.describe_certificate(CertificateArn=arn)['Certificate']

            if certificate['Status'] != 'PENDING_VALIDATION':
                return

            for v in certificate['DomainValidationOptions']:

                if 'ValidationStatus' not in v or 'ResourceRecord' not in v:
                    all_records_created = False
                    continue

                records = []
                if v['ValidationStatus'] == 'PENDING_VALIDATION':
                    records.append({
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': v['ResourceRecord']['Name'],
                            'Type': v['ResourceRecord']['Type'],
                            'TTL': 60,
                            'ResourceRecords': [{
                                'Value': v['ResourceRecord']['Value']
                            }]
                        }
                    })

                if records:
                    response = boto3.client('route53').change_resource_record_sets(
                        HostedZoneId=get_zone_for(v['DomainName'], props),
                        ChangeBatch={
                            'Comment': 'Domain validation for %s' % arn,
                            'Changes': records
                        }
                    )
