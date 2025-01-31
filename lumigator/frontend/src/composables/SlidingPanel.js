import { ref } from 'vue'

/**
 * A ref that indicates whether the sliding panel is shown or not.
 * Manipulate sidePanel's behaviour from any component
 */
const showSlidingPanel = ref(false);

/**
 * A composable function that provides functionality to toggle the sliding panel.
 */
export function useSlidePanel() {
  /**
   * Toggles the visibility of the sliding panel.
   */
  function togglePanel() {
    showSlidingPanel.value = !showSlidingPanel.value;
  }

  return {
    showSlidingPanel,
    togglePanel
  };
}
