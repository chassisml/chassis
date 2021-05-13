import json
import os
import sys
from urllib.parse import urljoin, urlsplit
from urllib.request import urlopen
from urllib.error import HTTPError

import click

STATUS_ROUTE = 'status'
RUN_ROUTE = 'run'


class ModelException(Exception):
    pass


def get_status(url):
    status_url = urljoin(url, STATUS_ROUTE)

    try:
        print('Calling: GET %s' % (status_url,))
        response = urlopen(status_url)
    except HTTPError as ex:
        response = ex
    except ValueError:
        raise ModelException('Invalid model url: %s' % (url,))
    except IOError:
        raise ModelException('Unable to connect to model url: %s' % (url,))

    try:
        response_json = json.load(response)
    except json.JSONDecodeError:
        raise ModelException('Model returned invalid json from: %s' % (status_url,))

    print('Received JSON: %s' % response_json)

    if response.status != 200:
        raise ModelException('Model returned non-success status code: %s' % (response.status,))


def post_job(url, input, output):
    run_url = urljoin(url, RUN_ROUTE)

    try:
        body = {
            'type': 'file',
            'input': input,
            'output': output,
        }
        print('Calling: POST %s' % (run_url,))
        print('  %s' % (body,))
        response = urlopen(run_url, data=json.dumps(body, ensure_ascii=True).encode('ascii'))
    except HTTPError as ex:
        response = ex
    except ValueError:
        raise ModelException('Invalid model url: %s' % (url,))
    except IOError:
        raise ModelException('Unable to connect to model url: %s' % (url,))

    try:
        response_json = json.load(response)
    except json.JSONDecodeError:
        raise ModelException('Model returned invalid json from: %s' % (run_url,))

    print('Received JSON: %s' % (response_json,))

    if response.status != 200:
        raise ModelException('Model returned non-success status code: %s' % (response.status,))

    print('Output should have been written to: %s' % (output,))


def validate_url(ctx, param, value):
    split = urlsplit(value)
    if not split.scheme:
        value = 'http://' + value
    return value


def validate_input_dir(ctx, param, value):
    if not os.path.isdir(value):
        raise click.BadParameter('input must be an existing directory')
    return value


def validate_output_dir(ctx, param, value):
    if os.path.exists(value) and not os.path.isdir(value):
        raise click.BadParameter('output must be a directory')
    return value


@click.command()
@click.option('--url', prompt='Model url', help='model url', callback=validate_url, required=True)
@click.option('--input', '-i', prompt='Input', help='path of input directory',
              callback=validate_input_dir, required=True)
@click.option('--output', '-o', prompt='Output', help='path of output directory',
              callback=validate_output_dir, required=True)
def main(url, input, output):
    """Runs a job using a packaged model application.

    The filesystem path for the model input and output should be absolute paths in the model application's filesystem.
    This means when running Docker containers the file paths must account for how volumes were mounted in the
    model container. For example if the model was run with:

    `docker run -v /home/user/data:/data my-model`

    then an input located on the host at `/home/user/data/input` would be run using the container's equivalent
    location `/data/input`.
    """
    try:
        get_status(url)
        post_job(url, input, output)
    except ModelException as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main(auto_envvar_prefix='PSC_MODEL')
