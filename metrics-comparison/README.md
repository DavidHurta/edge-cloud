# Visualizing Metrics Comparisons Across Technologies

Meanwhile, a Prometheus server gathers metrics, and GitHub Actions exports a subset of metrics to a MySQL database; it is necessary to visualize the collected metrics for comparison.

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
