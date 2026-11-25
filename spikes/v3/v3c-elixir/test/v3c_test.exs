defmodule V3cTest do
  use ExUnit.Case
  alias V3c.{EDN, Model}

  @root Path.expand("../../../..", __DIR__)
  defp read(f), do: EDN.read!(File.read!(Path.join(@root, "spikes/v3/shared/" <> f)))

  test "slice and extension conform" do
    assert Model.errors(read("slice.edn")) == []
    assert Model.errors(read("extension.edn")) == []
  end

  test "the 12 negatives are rejected" do
    s = read("slice.edn")
    rejected = for {name, f} <- Model.negatives(), Model.errors(f.(s)) != [], do: name
    assert length(Model.negatives()) == 12
    assert length(rejected) == 12
  end
end
