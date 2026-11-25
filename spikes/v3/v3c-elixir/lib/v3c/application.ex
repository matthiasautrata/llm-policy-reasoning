defmodule V3c.Application do
  @moduledoc "Top supervisor: the session state (Agent V3c.State) and V3c.Sup. The SQL boundary (V3c.SQL) is started under it by `V3c.SQL.configure/2`."
  use Application

  @impl true
  def start(_type, _args) do
    Supervisor.start_link([%{id: V3c.State, start: {Agent, :start_link, [&V3c.Store.new/0, [name: V3c.State]]}}, {DynamicSupervisor, name: V3c.Sup, strategy: :one_for_one}], strategy: :one_for_one, name: V3c.Top)
  end
end
