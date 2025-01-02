export const COLORS = {
    whatsappGreen: '#25D366',
    whatsappLightGreen: '#25D366',
    whatsappDarkGreen: '#128C7E',
    lightGray: '#FFFFFF'
};

export const CHART_OPTIONS = {
    scales: {
      x: {
        ticks: {
          color: COLORS.lightGray
        }
      },
      y: {
        ticks: {
          color: COLORS.lightGray
        }
      }
    },
    plugins: {
      legend: {
        labels: {
          color: COLORS.lightGray
        }
      }
    }
  };

export const HEATMAP_OPTIONS = {
  responsive: true,
  scales: {
      y: {
          reverse: true,
          beginAtZero: true,
          min: 0,
          max: 6,
          type: 'linear' as const,
          labels: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
          offset: true,
          ticks: {
            stepSize: 1,
            callback: (value: number) => ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][Math.floor(value)]
          }
      },
      x: {
          type: 'category' as const,
          min:37,
          max: 52,
          labels: Array.from({ length: 53 }, (_, i) => `W${i + 1}`),
          offset: true
      }
  },
  plugins: {
      legend: {
          display: false
      },
      tooltip: {
          callbacks: {
              label: (context: any) => `Value: ${context.raw.v.toFixed(2)}`
          }
      }
  }
};