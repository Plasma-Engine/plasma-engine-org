import { MantineTheme, createTheme, MantineColorsTuple } from '@mantine/core';

// Custom color palette for Plasma Engine
const plasmaBlue: MantineColorsTuple = [
  '#e3f2fd',
  '#bbdefb',
  '#90caf9',
  '#64b5f6',
  '#42a5f5',
  '#2196f3',
  '#1e88e5',
  '#1976d2',
  '#1565c0',
  '#0d47a1'
];

const plasmaPurple: MantineColorsTuple = [
  '#f3e5f5',
  '#e1bee7',
  '#ce93d8',
  '#ba68c8',
  '#ab47bc',
  '#9c27b0',
  '#8e24aa',
  '#7b1fa2',
  '#6a1b9a',
  '#4a148c'
];

const plasmaTeal: MantineColorsTuple = [
  '#e0f2f1',
  '#b2dfdb',
  '#80cbc4',
  '#4db6ac',
  '#26a69a',
  '#009688',
  '#00897b',
  '#00796b',
  '#00695c',
  '#004d40'
];

const plasmaOrange: MantineColorsTuple = [
  '#fff3e0',
  '#ffe0b2',
  '#ffcc02',
  '#ffb74d',
  '#ffa726',
  '#ff9800',
  '#fb8c00',
  '#f57c00',
  '#ef6c00',
  '#e65100'
];

export const theme = createTheme({
  colorScheme: 'auto',
  primaryColor: 'plasma-blue',
  colors: {
    'plasma-blue': plasmaBlue,
    'plasma-purple': plasmaPurple,
    'plasma-teal': plasmaTeal,
    'plasma-orange': plasmaOrange,
  },
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
  fontFamilyMonospace: 'JetBrains Mono, Consolas, Monaco, monospace',
  headings: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
    fontWeight: '600',
    sizes: {
      h1: { fontSize: '2.5rem', lineHeight: '1.2' },
      h2: { fontSize: '2rem', lineHeight: '1.3' },
      h3: { fontSize: '1.5rem', lineHeight: '1.4' },
      h4: { fontSize: '1.25rem', lineHeight: '1.4' },
      h5: { fontSize: '1.125rem', lineHeight: '1.5' },
      h6: { fontSize: '1rem', lineHeight: '1.5' },
    },
  },
  radius: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '20px',
  },
  spacing: {
    xs: '8px',
    sm: '12px',
    md: '16px',
    lg: '20px',
    xl: '24px',
  },
  shadows: {
    xs: '0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1)',
    sm: '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  },
  components: {
    Button: {
      defaultProps: {
        size: 'md',
      },
      styles: {
        root: {
          fontWeight: 500,
          transition: 'all 0.2s ease',
        },
      },
    },
    Card: {
      defaultProps: {
        shadow: 'sm',
        radius: 'md',
        withBorder: true,
      },
      styles: {
        root: {
          transition: 'all 0.2s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          },
        },
      },
    },
    Paper: {
      defaultProps: {
        shadow: 'sm',
        radius: 'md',
      },
    },
    Modal: {
      defaultProps: {
        centered: true,
        overlayProps: {
          backgroundOpacity: 0.55,
          blur: 3,
        },
      },
    },
    TextInput: {
      styles: {
        input: {
          fontSize: '14px',
          '&:focus': {
            borderColor: 'var(--mantine-color-plasma-blue-5)',
          },
        },
      },
    },
    PasswordInput: {
      styles: {
        input: {
          fontSize: '14px',
          '&:focus': {
            borderColor: 'var(--mantine-color-plasma-blue-5)',
          },
        },
      },
    },
    Select: {
      styles: {
        input: {
          fontSize: '14px',
          '&:focus': {
            borderColor: 'var(--mantine-color-plasma-blue-5)',
          },
        },
      },
    },
    Textarea: {
      styles: {
        input: {
          fontSize: '14px',
          '&:focus': {
            borderColor: 'var(--mantine-color-plasma-blue-5)',
          },
        },
      },
    },
    NavLink: {
      styles: {
        root: {
          borderRadius: '8px',
          fontWeight: 500,
          '&[data-active]': {
            backgroundColor: 'var(--mantine-color-plasma-blue-1)',
            color: 'var(--mantine-color-plasma-blue-7)',
            '&:hover': {
              backgroundColor: 'var(--mantine-color-plasma-blue-2)',
            },
          },
          '&:hover': {
            backgroundColor: 'var(--mantine-color-gray-1)',
          },
        },
      },
    },
    Badge: {
      styles: {
        root: {
          fontWeight: 500,
        },
      },
    },
    Notification: {
      styles: {
        root: {
          borderRadius: '12px',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        },
      },
    },
    Spotlight: {
      styles: {
        search: {
          fontSize: '16px',
        },
      },
    },
  },
  other: {
    // Custom properties for the app
    gradients: {
      plasma: 'linear-gradient(135deg, #2196f3 0%, #9c27b0 100%)',
      success: 'linear-gradient(135deg, #009688 0%, #4caf50 100%)',
      warning: 'linear-gradient(135deg, #ff9800 0%, #ffc107 100%)',
      danger: 'linear-gradient(135deg, #f44336 0%, #e91e63 100%)',
    },
    animations: {
      fadeIn: 'fadeIn 0.3s ease-in-out',
      slideIn: 'slideInUp 0.4s ease-out',
      bounce: 'bounce 0.6s ease-in-out',
    },
  },
});

// Dark theme overrides
export const darkTheme = createTheme({
  ...theme,
  colorScheme: 'dark',
  colors: {
    ...theme.colors,
    dark: [
      '#d5d7e0',
      '#acaebf',
      '#8c8fa3',
      '#666980',
      '#4d4f66',
      '#34354a',
      '#2b2c3d',
      '#1d1e30',
      '#0c0d21',
      '#01010a',
    ],
  },
  components: {
    ...theme.components,
    Card: {
      ...theme.components?.Card,
      styles: {
        root: {
          ...theme.components?.Card?.styles?.root,
          backgroundColor: 'var(--mantine-color-dark-7)',
          borderColor: 'var(--mantine-color-dark-6)',
        },
      },
    },
    Paper: {
      ...theme.components?.Paper,
      styles: {
        root: {
          backgroundColor: 'var(--mantine-color-dark-7)',
        },
      },
    },
    NavLink: {
      ...theme.components?.NavLink,
      styles: {
        root: {
          ...theme.components?.NavLink?.styles?.root,
          '&[data-active]': {
            backgroundColor: 'var(--mantine-color-plasma-blue-9)',
            color: 'var(--mantine-color-plasma-blue-2)',
            '&:hover': {
              backgroundColor: 'var(--mantine-color-plasma-blue-8)',
            },
          },
          '&:hover': {
            backgroundColor: 'var(--mantine-color-dark-6)',
          },
        },
      },
    },
  },
});

// CSS-in-JS styles for global animations
export const globalStyles = `
  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes slideInUp {
    from {
      opacity: 0;
      transform: translate3d(0, 100%, 0);
    }
    to {
      opacity: 1;
      transform: translate3d(0, 0, 0);
    }
  }

  @keyframes bounce {
    0%, 20%, 53%, 80%, 100% {
      animation-timing-function: cubic-bezier(0.215, 0.610, 0.355, 1.000);
      transform: translate3d(0, 0, 0);
    }
    40%, 43% {
      animation-timing-function: cubic-bezier(0.755, 0.050, 0.855, 0.060);
      transform: translate3d(0, -30px, 0);
    }
    70% {
      animation-timing-function: cubic-bezier(0.755, 0.050, 0.855, 0.060);
      transform: translate3d(0, -15px, 0);
    }
    90% {
      transform: translate3d(0, -4px, 0);
    }
  }

  .gradient-text {
    background: linear-gradient(135deg, #2196f3 0%, #9c27b0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .glass-morphism {
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .hover-lift {
    transition: all 0.2s ease;
  }

  .hover-lift:hover {
    transform: translateY(-4px);
  }
`;

export type PlasmaTheme = typeof theme;