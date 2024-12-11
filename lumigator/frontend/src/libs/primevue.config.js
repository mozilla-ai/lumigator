import { definePreset } from '@primevue/themes';
import Aura from '@primevue/themes/aura';

const LumiPreset = definePreset(Aura, {
  semantic: {
    colorScheme: {
      light: {},
      dark: {
        primary: {
          color: '#E0C414',
          inverseColor: '#E0C414',
          hoverColor: '#FFF646',
          activeColor: '#E0C414',
          lgFontSize: '14px',
				},
      },
    },
  },
});

export default LumiPreset
