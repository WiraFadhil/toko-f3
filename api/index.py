from app import app


def handler(environ, start_response):
    environ['SCRIPT_NAME'] = ''
    return app.wsgi_app(environ, start_response)
