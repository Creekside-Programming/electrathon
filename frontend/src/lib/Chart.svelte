<script lang="ts">
  import { onMount } from "svelte";
  import ChartJS from "chart.js/auto";

  export type ChartMetric = "voltage" | "amperage";

  type Props = {
    width?: string;
    height?: string;
    metric: ChartMetric;
    labels: string[];
    values: number[];
  };

  let { width = "500px", height = "500px", metric, labels, values }: Props =
    $props();

  let canvasEl: HTMLCanvasElement;
  let chart: ChartJS | null = null;

  const maxPoints = 40;

  function styleForMetric(m: ChartMetric) {
    return m === "voltage"
      ? {
          label: "Voltage (V)",
          borderColor: "rgba(75, 192, 192, 1)",
          backgroundColor: "rgba(75, 192, 192, 0.1)",
        }
      : {
          label: "Amperage (A)",
          borderColor: "rgba(255, 99, 132, 1)",
          backgroundColor: "rgba(255, 99, 132, 0.1)",
        };
  }

  function applyData() {
    if (!chart) return;

    const style = styleForMetric(metric);
    const lb = labels.slice(-maxPoints);
    const vals = values.slice(-maxPoints);

    chart.data.labels = lb;
    const ds = chart.data.datasets[0];
    ds.data = vals;
    ds.label = style.label;
    ds.borderColor = style.borderColor;
    ds.backgroundColor = style.backgroundColor;

    chart.update("none");
  }

  onMount(() => {
    const style = styleForMetric(metric);
    chart = new ChartJS(canvasEl, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: style.label,
            data: [],
            borderColor: style.borderColor,
            backgroundColor: style.backgroundColor,
            tension: 0,
            fill: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        scales: {
          y: { beginAtZero: true },
        },
      },
    });

    applyData();

    return () => {
      chart?.destroy();
      chart = null;
    };
  });

  $effect(() => {
    labels;
    values;
    metric;
    applyData();
  });
</script>

<div style:width style:height class="min-h-[200px]">
  <canvas bind:this={canvasEl}></canvas>
</div>
