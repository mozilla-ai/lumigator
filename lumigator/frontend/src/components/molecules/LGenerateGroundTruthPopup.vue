<template>
  <div v-if="visible" class="popup-backdrop">
    <div class="popup">
      <div class="popup-header">
        <h3>Generate Ground Truth</h3>
      </div>
      <div class="popup-body">
        <p>
          Ground truth will be generated using
          <strong>
            <a href="https://huggingface.co/facebook/bart-large-cnn" target="_blank"
              >BART</a
            > </strong
          >, Lumigator's reference model for this task.
        </p>
        <p>
          Since result quality can vary substantially depending on your dataset, we recommend
          reviewing the output before using it as ground truth for your experiments.
        </p>
        <p>Processing time depends on your compute power.</p>
      </div>
      <div class="popup-footer">
        <Button
          label="Cancel"
          class="popup-button cancel"
          severity="secondary"
          outlined
          rounded
          @click="close"
        />
        <Button
          label="Start Generating"
          class="popup-button generate"
          severity="warning"
          rounded
          @click="accept"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { defineProps, defineEmits } from 'vue'
import Button from 'primevue/button'

// Define the props
const props = defineProps({
  visible: {
    type: Boolean,
    required: true,
  },
  dataset: {
    type: Object,
    required: true,
  },
})

// Define the emitted events
const emit = defineEmits(['close', 'accept'])

// Methods
function close() {
  emit('close')
}

function accept() {
  emit('accept', props.dataset)
}
</script>

<style scoped>
.popup-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.popup {
  background: #1e1e1e;
  color: #fff;
  border-radius: 8px;
  width: 580px;
  max-width: 90%;
  padding: 1.5rem;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.popup-icon {
  font-size: 2rem;
  margin-right: 0.5rem;
  color: #f39c12;
}

.popup-body {
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

.popup-footer {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}
</style>
