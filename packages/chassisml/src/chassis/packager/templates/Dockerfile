FROM balenalib/{{ arch }}-debian-python:{{ python_version }}-build AS build

{% if needs_cross_compiling -%}
RUN [ "cross-build-start" ]
{%- endif %}

# Copy requirements file and pip install.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

{% if needs_cross_compiling -%}
RUN [ "cross-build-end" ]
{%- endif %}

FROM balenalib/{{ arch }}-debian-python:{{ python_version }}-run

WORKDIR /app

COPY --from=build /usr/local/lib/python{{ python_version }}/site-packages /usr/local/lib/python{{ python_version }}/site-packages

# Copy the entrypoint file and gRPC server implementation.
COPY entrypoint.py ./

# Copy app folder.
COPY chassis chassis

# Copy the app and data
COPY data data

CMD ["python3", "entrypoint.py"]