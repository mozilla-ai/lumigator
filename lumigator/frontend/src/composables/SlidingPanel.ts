import { ref } from 'vue';

const showSlidingPanel = ref(false);

export function useSlidePanel() {
  function togglePanel() {
    showSlidingPanel.value = !showSlidingPanel.value;
  }

  return {
    showSlidingPanel,
    togglePanel
  };
}
