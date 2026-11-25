defmodule V3c.MixProject do
  use Mix.Project

  def project do
    [
      app: :v3c,
      version: "0.1.0",
      elixir: "~> 1.20",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      extra_applications: [:logger],
      mod: {V3c.Application, []}
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:ex_datalog, "== 0.5.0"},
      {:adbc, "== 0.12.1"},
      {:nimble_parsec, "~> 1.4"},
      {:jason, "~> 1.4"}
    ]
  end
end
