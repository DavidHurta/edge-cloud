# Visualizing Metrics Comparisons Across Technologies

A Prometheus server gathers metrics, and GitHub Actions exports a subset of the metrics to a MySQL database.
The goal of this application is to to generate summaries of the collected metrics for comparison using
statistical measurements, tests, and data visualization. The generated reports are intended
to be merged using third party tools such as [`pdfjam`](https://github.com/pdfjam/pdfjam).

## Requirements

- [`pipenv`](https://github.com/pypa/pipenv)

## Usage

1. Install dependencies:

    ```sh
    $ pipenv install
    ```

2. Spawn a pipenv shell:

   ```sh
   $ pipenv shell
   ```

3. Set environment variables; for example:

   ```sh
   $ export DB_HOST=example.com
   $ export DB_USER=ADMIN
   $ export DB_PASSWORD=PASSWORD
   $ export DB_PORT=25060
   $ export DB_DATABASE=metrics
   ```

4. Run script:

   ```sh
   $ python main.py
   ```

5. View reports, which were generated in a `_output` subdirectory.
