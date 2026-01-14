<script lang="ts">
  let apiEndpoint: string = "http://localhost:8000";

  import Chart from './lib/Chart.svelte';
</script>

<main>
  <h1>Electrathon Dashboard</h1>

  <label for="endpointInput">API Endpoint</label>
  <input id="endpointInput" bind:value={apiEndpoint} />

  <Chart width="500px" height="500px" apiEndpoint={apiEndpoint} />
</main>