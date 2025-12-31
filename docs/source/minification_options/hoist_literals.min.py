def validate(arn,props):
	H='Value';G='Type';F='Name';E='ValidationStatus';D='PENDING_VALIDATION';C=False;B='ValidationMethod';A='ResourceRecord'
	if B in props and props[B]=='DNS':
		all_records_created=C
		while not all_records_created:
			all_records_created=True;certificate=acm.describe_certificate(CertificateArn=arn)['Certificate']
			if certificate['Status']!=D:return
			for v in certificate['DomainValidationOptions']:
				if E not in v or A not in v:all_records_created=C;continue
				records=[]
				if v[E]==D:records.append({'Action':'UPSERT','ResourceRecordSet':{F:v[A][F],G:v[A][G],'TTL':60,'ResourceRecords':[{H:v[A][H]}]}})
				if records:response=boto3.client('route53').change_resource_record_sets(HostedZoneId=get_zone_for(v['DomainName'],props),ChangeBatch={'Comment':'Domain validation for %s'%arn,'Changes':records})