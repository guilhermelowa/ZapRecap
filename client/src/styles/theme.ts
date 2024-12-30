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