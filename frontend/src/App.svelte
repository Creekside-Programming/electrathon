<script lang="ts">
  import { onDestroy } from "svelte";
  import Chart from "./lib/Chart.svelte";

  const defaultApiUrl = "http://localhost:8000";

  let apiEndpoint = $state(defaultApiUrl);

  function hostPortFromApiUrl(url: string): string {
    try {
      const u = new URL(url);
      return u.port ? `${u.hostname}:${u.port}` : u.hostname;
    } catch {
      return "localhost:8000";
    }
  }

  let endpointInput = $state(hostPortFromApiUrl(defaultApiUrl));

  function normalizeEndpoint(raw: string): string | null {
    const t = raw.trim();
    if (!t) return null;
    const candidate = /^https?:\/\//i.test(t) ? t : `http://${t}`;
    try {
      const u = new URL(candidate);
      if (!u.hostname) return null;
      return candidate;
    } catch {
      return null;
    }
  }

  /** `http(s)://host[:port]` → `ws(s)://host[:port]/ws` */
  function toWebSocketUrl(httpBase: string): string {
    const u = new URL("/ws", httpBase);
    u.protocol = u.protocol === "https:" ? "wss:" : "ws:";
    return u.toString();
  }

  let parsedEndpoint = $derived(normalizeEndpoint(endpointInput));
  let endpointInvalidHint =
    $derived(parsedEndpoint === null && endpointInput.trim().length > 0);

  type ConnectionState = "disconnected" | "handshake" | "live" | "error";

  let connectionState = $state<ConnectionState>("disconnected");
  let connectionError = $state<string | null>(null);
  let ws = $state<WebSocket | null>(null);

  function closeWebSocket() {
    ws?.close();
    ws = null;
  }

  onDestroy(closeWebSocket);

  async function connect() {
    const base = normalizeEndpoint(endpointInput);
    if (!base) return;

    connectionError = null;
    connectionState = "handshake";
    closeWebSocket();

    const healthUrl = new URL("/are_you_alive", base).href;
    try {
      const res = await fetch(healthUrl, { method: "GET" });
      if (!res.ok) {
        connectionState = "error";
        connectionError = `Server returned ${res.status}`;
        return;
      }
    } catch (e) {
      connectionState = "error";
      connectionError = e instanceof Error ? e.message : "Could not reach the server";
      return;
    }

    const socket = new WebSocket(toWebSocketUrl(base));
    let opened = false;

    socket.addEventListener("open", () => {
      opened = true;
      ws = socket;
      apiEndpoint = base;
      connectionState = "live";
    });

    socket.addEventListener("message", (e) => {
      console.log("Received message:", e.data);
    });

    socket.addEventListener("error", () => {
      if (!opened) {
        connectionState = "error";
        connectionError = "WebSocket error";
      }
    });

    socket.addEventListener("close", () => {
      if (ws === socket) {
        ws = null;
      }
      if (!opened) {
        connectionState = "error";
        connectionError ??= "WebSocket closed before opening";
      } else if (connectionState === "live") {
        connectionState = "disconnected";
        connectionError = "Connection closed";
      }
    });
  }

  let handshakeBusy = $derived(connectionState === "handshake");

  let connectionStatusLabel = $derived.by(() => { //? do we REALLY need this?
    switch (connectionState) {
      case "handshake":
        return "Connecting";
      case "live":
        return "Connected";
      case "error":
        return "Connection error";
      default:
        return "Disconnected";
    }
  });

  type BatteryStatus = {
    voltage: number;
    amperage: number;
  };

  type BatteryMessage = {
    type: "battery";
    data: BatteryStatus[];
  };

  function isBatteryMessage(msg: any): msg is BatteryMessage {
    return (
      msg?.type === "battery" &&
      Array.isArray(msg.data) &&
      msg.data.every(
        (m: any) =>
          typeof m.voltage === "number" &&
          typeof m.amperage === "number"
      )
    );
  }
</script>

<main>
  <div class="navbar bg-base-100 shadow-sm">
    <div class="flex-1">
      <h1 class="text-lg">Electrathon Dashboard</h1>
    </div>

    <div class="flex gap-4 items-center">
      <div
        class="inline-grid *:[grid-area:1/1]"
        aria-label={connectionStatusLabel}
        title={connectionStatusLabel}
      >
        {#if connectionState === "handshake"}
          <div class="status status-warning status-md animate-ping"></div>
          <div class="status status-warning status-md"></div>
        {:else if connectionState === "live"}
          <div class="status status-success status-md animate-ping"></div>
          <div class="status status-success status-md"></div>
        {:else if connectionState === "error"}
          <div class="status status-error status-md animate-ping"></div>
          <div class="status status-error status-md"></div>
        {:else}
          <div class="status status-neutral status-md"></div>
        {/if}
      </div>
      <form
        class="join"
        onsubmit={(e) => {
          e.preventDefault();
          connect();
        }}
      >
        <div>
          <label class="input validator join-item" class:input-error={endpointInvalidHint}>
            <svg
              class="opacity-50"
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 640 640"
              aria-hidden="true"
            >
              <path
                d="M544 269.8C529.2 279.6 512.2 287.5 494.5 293.8C447.5 310.6 385.8 320 320 320C254.2 320 192.4 310.5 145.5 293.8C127.9 287.5 110.8 279.6 96 269.8L96 352C96 396.2 196.3 432 320 432C443.7 432 544 396.2 544 352L544 269.8zM544 192L544 144C544 99.8 443.7 64 320 64C196.3 64 96 99.8 96 144L96 192C96 236.2 196.3 272 320 272C443.7 272 544 236.2 544 192zM494.5 453.8C447.6 470.5 385.9 480 320 480C254.1 480 192.4 470.5 145.5 453.8C127.9 447.5 110.8 439.6 96 429.8L96 496C96 540.2 196.3 576 320 576C443.7 576 544 540.2 544 496L544 429.8C529.2 439.6 512.2 447.5 494.5 453.8z"
              />
            </svg>
            <input
              name="endpoint"
              type="text"
              placeholder="localhost:8000"
              autocomplete="url"
              bind:value={endpointInput}
              aria-invalid={endpointInvalidHint}
              required
            />
          </label>
          <div class="validator-hint" class:hidden={!endpointInvalidHint}>
            Enter a valid host:port
          </div>
          {#if connectionError}
            <div class="validator-hint text-error mt-1 max-w-xs">{connectionError}</div>
          {/if}
        </div>
        <button
          type="submit"
          class="btn btn-neutral join-item"
          disabled={handshakeBusy}
        >
          Connect
        </button>
      </form>
    </div>
  </div>
  <div class="m-4"> <!-- content -->
    <div role="tablist" class="tabs tabs-lift ml-2">  
      <input type="radio" name="my_tabs_3" class="tab ml-4" aria-label="Battery" checked={true} />
      <div class="tab-content bg-base-100 border-base-300 rounded">
        <div class="flex">
          <div class="p-4">
            <h2 class="text-xl mb-1">Voltage</h2>
            <hr class="border-base-300">
            <Chart width="300px" height="500px" />
          </div>
          <div class="p-4">
            <h2 class="text-xl mb-1">Amperage</h2>
            <hr class="border-base-300">
            <Chart width="300px" height="500px" />
          </div>
        </div>
      </div>

      <input type="radio" name="my_tabs_3" class="tab" aria-label="TAB 2" />
      <div class="tab-content bg-base-100 border-base-300 p-6">Tab content 2</div>

      <input type="radio" name="my_tabs_3" class="tab" aria-label="TAB 3" />
      <div class="tab-content bg-base-100 border-base-300 p-6">Tab content 3</div>
    </div>
  </div>
</main>