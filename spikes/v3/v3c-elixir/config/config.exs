import Config
config :logger, level: :warning
# stdout carries the JSON result
config :logger, :default_handler, config: [type: :standard_error]
# adbc 0.12.1 pins DuckDB 1.5.1, which cannot read slice.duckdb (written by DuckDB 2.0.1); 2.0 ships tar.gz assets
config :adbc, :drivers, [
  {:duckdb, version: "2.0.1", url: "https://github.com/duckdb/duckdb/releases/download/v2.0.1/duckdb-shared-libs-osx-universal.tar.gz"},
  :postgresql
]
