# Python Minifier

Transforms Python source code into it's most compact representation.

python-minifier supports Python 2.6 to 2.7 and Python 3.3 to 3.7.

* [PyPi](https://pypi.org/project/python-minifier/)
* [Documentation](https://dflook.github.io/python-minifier/)
* [Issues](https://github.com/dflook/python-minifier/issues)

As an example, the following python source:

```python
def handler(event, context):
    l.info(event)
    try:
        i_token = hashlib.new('md5', (event['RequestId'] + event['StackId']).encode()).hexdigest()
        props = event['ResourceProperties']

        if event['RequestType'] == 'Create':
            event['PhysicalResourceId'] = 'None'
            event['PhysicalResourceId'] = create_cert(props, i_token)
            add_tags(event['PhysicalResourceId'], props)
            validate(event['PhysicalResourceId'], props)

            if wait_for_issuance(event['PhysicalResourceId'], context):
                event['Status'] = 'SUCCESS'
                return send(event)
            else:
                return reinvoke(event, context)

        elif event['RequestType'] == 'Delete':
            if event['PhysicalResourceId'] != 'None':
                acm.delete_certificate(CertificateArn=event['PhysicalResourceId'])
            event['Status'] = 'SUCCESS'
            return send(event)

        elif event['RequestType'] == 'Update':

            if replace_cert(event):
                event['PhysicalResourceId'] = create_cert(props, i_token)
                add_tags(event['PhysicalResourceId'], props)
                validate(event['PhysicalResourceId'], props)

                if not wait_for_issuance(event['PhysicalResourceId'], context):
                    return reinvoke(event, context)
            else:
                if 'Tags' in event['OldResourceProperties']:
                    acm.remove_tags_from_certificate(CertificateArn=event['PhysicalResourceId'],
                                                     Tags=event['OldResourceProperties']['Tags'])

                add_tags(event['PhysicalResourceId'], props)

            event['Status'] = 'SUCCESS'
            return send(event)
        else:
            raise RuntimeError('Unknown RequestType')

    except Exception as ex:
        l.exception('')
        event['Status'] = 'FAILED'
        event['Reason'] = str(ex)
        return send(event)
```

Becomes:

```python
K='OldResourceProperties'
J='Tags'
I='None'
G='SUCCESS'
F='RequestType'
E='Status'
B='PhysicalResourceId'
def handler(event,context):
	D=context;A=event;l.info(A)
	try:
		H=hashlib.new('md5',(A['RequestId']+A['StackId']).encode()).hexdigest();C=A['ResourceProperties']
		if A[F]=='Create':
			A[B]=I;A[B]=create_cert(C,H);add_tags(A[B],C);validate(A[B],C)
			if wait_for_issuance(A[B],D):A[E]=G;return send(A)
			else:return reinvoke(A,D)
		elif A[F]=='Delete':
			if A[B]!=I:acm.delete_certificate(CertificateArn=A[B])
			A[E]=G;return send(A)
		elif A[F]=='Update':
			if replace_cert(A):
				A[B]=create_cert(C,H);add_tags(A[B],C);validate(A[B],C)
				if not wait_for_issuance(A[B],D):return reinvoke(A,D)
			else:
				if J in A[K]:acm.remove_tags_from_certificate(CertificateArn=A[B],Tags=A[K][J])
				add_tags(A[B],C)
			A[E]=G;return send(A)
		else:raise RuntimeError('Unknown RequestType')
	except Exception as L:l.exception('');A[E]='FAILED';A['Reason']=str(L);return send(A)
```

## Why?

AWS Cloudformation templates may have AWS lambda function source code embedded in them, but only if the function is less 
than 4KiB. I wrote this package so I could write python normally and still embed the module in a template.

## Installation

To install python-minifier use pip:

```bash
$ pip install python-minifier
```

Note that python-minifier depends on the python interpreter for parsing source code, 
so install using a version of python appropriate for your source.

python-minifier runs with and can minify code written for Python 2.6 to 2.7 and Python 3.3 to 3.7.

## Usage

To minify a source file, and write the minified module to stdout:

```bash
$ pyminify hello.py
```

There is also an API. The same example would look like:

```python
import python_minifier

with open('hello.py') as f:
    print(python_minifier.minify(f.read()))
```

Documentation is available at [dflook.github.io/python-minifier/](https://dflook.github.io/python-minifier/)

## License

Available under the MIT License. Full text is in the [LICENSE](LICENSE) file.

Copyright (c) 2018 Daniel Flook
