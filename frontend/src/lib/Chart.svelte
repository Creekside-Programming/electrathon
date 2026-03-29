<script lang="ts">
  export const width: string = "500px";
  export const height: string = "500px";

  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';

  let chart: Chart | null = null;
  let canvasEl: HTMLCanvasElement;

  async function fetchAndUpdate() {
    // const res = await fetch(apiEndpoint);
    // const { valueA, valueB } = await res.json();
    const timestamp = new Date().toLocaleTimeString();

    const valueA = 10.0;
    const valueB = 5.0;

    if (chart) {
      chart.data.labels?.push(timestamp);
      chart.data.datasets[0].data.push(valueA);
      chart.data.datasets[1].data.push(valueB);

      const maxPoints = 20;
      if (chart.data.labels!.length > maxPoints) {
        chart.data.labels!.shift();
        chart.data.datasets.forEach(ds => ds.data.shift());
      }

      chart.update();
    }
  }

  onMount(() => {
    chart = new Chart(canvasEl, {
      type: 'line',
      data: {
        labels: ["t1", "t2", "t3", "t4", "t5"], 
        datasets: [
          {
            label: 'volts dummy',
            data: [12.1, 12.5, 12.4, 12.9, 13.1],
            borderColor: 'rgba(75, 192, 192, 1)',
            tension: 0.3
          },
          {
            label: 'amps dummy',
            data: [1.5, 2.3, 5.0, 12.9, 1.0],
            borderColor: 'rgba(255, 99, 132, 1)',
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        animation: false,
        scales: {
          y: { beginAtZero: true }
        }
      }
    });

    fetchAndUpdate();
    const interval = setInterval(fetchAndUpdate, 5000);

    return () => {
      clearInterval(interval);
      chart?.destroy();
    };
  });
</script>

<div style="width: {width}; height: {height};">
  <canvas bind:this={canvasEl}></canvas>
</div>