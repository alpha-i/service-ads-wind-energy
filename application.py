import logging

import click

from web import create_app

app = create_app('config')


@app.cli.command('create_superuser')
@click.argument('username')
@click.argument('password')
def create_superuser(username, password):
    from core.services.superuser import create_admin
    create_admin(username, password)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True, host=app.config['HOST'], port=app.config['PORT'])
