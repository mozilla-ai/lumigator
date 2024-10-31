import { definePreset } from '@primevue/themes';
import Aura from '@primevue/themes/aura';

const LumiPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '#f8f8f8',
      100: '#f2f2f2',
      200: '#e0e0e0',
      300: '#cccccc',
      400: '#b8b8b8',
      500: '#a0a0a0',
      600: '#8a8a8a',
      700: '#6e6e6e',
      800: '#4d4d4d',
      900: '#2a2a2a',
      950: '#1a1a1a',
    },
    colorScheme: {
      light: {},
      dark: {
        primary: {
          color: '#E0C414',
          inverseColor: '#E0C414',
          hoverColor: 'red',
          activeColor: '#f2f2f2',
        },
      },
    },
  },
});

export default LumiPreset
