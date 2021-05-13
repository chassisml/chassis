import os

from flask import Flask

from ._api import api


class MainFlask(Flask):
    """Flask subclass adding a `main` function."""

    def main(self, args=None):
        """Parse host, port, and debug from command line and run the Flask development server."""
        import argparse

        parser = argparse.ArgumentParser(description='development server')
        parser.add_argument('--host', '-H', default=os.environ.get('PSC_MODEL_HOST'), help='host')
        parser.add_argument('--port', '-p', default=os.environ.get('PSC_MODEL_PORT'), help='port')
        parser.add_argument('--no-debug', action='store_false', dest='debug',
                            default=os.environ.get('PSC_MODEL_DEBUG', True), help='turn off debug mode')
        args = parser.parse_args()

        self.run(debug=args.debug, host=args.host, port=args.port)


def create_app(model_factory=None, shutdown_function=None):
    """Create an instance of the Flask app configured with the given `model_factory`. This value may
    alternatively be specified through the `PSC_MODEL_FACTORY` environment variable.

    The `model_factory` should be a callable object (or a dotted string import path to a callable object)
    that returns an instance of a class that implements the `ModelBase` abstract base class. This will
    usually be the model class itself or a function returning an instance of the model class.

    For example:
    ```
    # mymodel.py
    class Model(ModelBase):
        def __init__(self, config=None):
            ...
        def run(self, input_path, output_path)
            ...

    # app.py
    app = create_app(Model)

    # or
    def configure_model_instance():
        return Model(config='foo')
    app = create_app(configure_model_instance)

    # or
    app = create_app('mymodel.Model')

    # or
    os.environ['PSC_MODEL_FACTORY'] = 'mymodel.Model'
    app = create_app()
    ```

    A `shutdown_function` may also be provided or configured through the `PSC_SHUTDOWN_FUNCTION`
    environment variable. If specified, this function will be called to terminate the application
    server process in place of the default function which sends a `SIGTERM` signal to the process
    group. This should not need to be set if your webserver shuts down and returns an exit code of
    on 0 `SIGTERM` such as Gunicorn, but it is webserver dependent.

    For example, the Waitress webserver will not shut down cleanly on `SIGTERM`. However, you may
    use the `interrupt_main` function from the standard library `_thread` module to shut down the
    single process server with exit code 0:

    ```
    # app.py
    from _thread import interrupt_main
    app = create_app(MyModel, shutdown_function=interrupt_main)

    from waitress import serve
    serve(app, listen='*:%s' % os.environ.get('PSC_MODEL_PORT', '8080'))
    ```

    Other webservers may require different approaches to shutdown cleanly.
    """
    if model_factory is None:
        model_factory = os.environ.get('PSC_MODEL_FACTORY')
    if not model_factory:
        raise ValueError('model_factory must be provided or the PSC_MODEL_FACTORY environment variable must be set')

    if shutdown_function is None:
        shutdown_function = os.environ.get('PSC_SHUTDOWN_FUNCTION')

    # set the `import_name` to the app package root http://flask.pocoo.org/docs/1.0/api/#application-object
    import_name = __name__.rsplit(".", 1)[0]
    app = MainFlask(import_name)
    app.register_blueprint(api)

    app.config['PSC_MODEL_FACTORY'] = model_factory
    if shutdown_function:
        app.config['PSC_SHUTDOWN_FUNCTION'] = shutdown_function

    return app
