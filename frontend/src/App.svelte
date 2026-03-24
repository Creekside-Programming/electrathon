<script lang="ts">
  let apiEndpoint: string = "http://localhost:8000";

  import Chart from './lib/Chart.svelte';
</script>

<main>
  <div class="navbar bg-base-100 shadow-sm">
    <div class="flex-1">
      <h1 class="text-lg">Electrathon Dashboard</h1>
    </div>

    <div class="flex gap-4">
      <span class="loading loading-spinner loading-md"></span> <!-- https://daisyui.com/components/status/ ??? -->
      <!-- <label class="text-sm" for="endpointInput">API Endpoint</label> -->
      <input class="input" id="endpointInput" bind:value={apiEndpoint} />
    </div>
  </div>
  <div class="m-4"> <!-- content -->
    <div role="tablist" class="tabs tabs-lift ml-2">  
      <input type="radio" name="my_tabs_3" class="tab ml-4" aria-label="Battery" checked={true} />
      <div class="tab-content">
        <div class="bg-base-100 border border-gray-300 rounded">
          <Chart width="500px" height="500px" apiEndpoint={apiEndpoint} />
        </div>
      </div>

      <input type="radio" name="my_tabs_3" class="tab" aria-label="TAB 2" />
      <div class="tab-content bg-base-100 border-base-300 p-6">Tab content 2</div>

      <input type="radio" name="my_tabs_3" class="tab" aria-label="TAB 3" />
      <div class="tab-content bg-base-100 border-base-300 p-6">Tab content 3</div>
    </div>
  </div>
</main>