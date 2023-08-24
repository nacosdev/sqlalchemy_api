## Get Started!

Ready to contribute? 

1. Fork the `sqlalchemy_api` repo on GitHub.
2. Clone your fork locally

    ```
    $ git clone git@github.com:<your username>/sqlalchemy_api.git
    ```

3. Install [`Hatch`](https://hatch.pypa.io/latest/install/) for project management:

    ```bash
    $ pip install hatch
    ```

4. Create a branch for local development:

    ```bash
    $ git checkout -b name-fix-or-feature
    ```

    Now you can make your changes locally.

5. Apply linting and formatting, if not already done:

    ```bash
    $ hatch run lint:format
    ```

6. When you're done making changes, check that your changes pass the tests:

    ```
    $ hatch run lint:check
    $ hatch run test:test
    ```

7. Commit your changes and push your branch to GitHub:

    ```
    $ git add .
    $ git commit -m "Description of the your changes."
    $ git push origin name-fix-or-feature
    ```

8. Submit a pull request through the GitHub website.

There is a docker compose file to run postgresql locally if needed, the following command will do it.
```bash
$ docker-compose up -d
```
Connection string for the database is `postgresql://postgres:postgres@localhost:5432/postgres`

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.md.
3. The pull request should work for Python 3.7, 3.8, 3.9, 3.10, 3.11. Details in
   https://github.com/nacosdev/sqlalchemy_api/actions.