<template>
  <div class="consent-banner">
    <div class="container">
      <PrimeVueButton
        class="close-button"
        icon="pi pi-times"
        severity="secondary"
        variant="text"
        raised
        rounded
        aria-label="Cancel"
      ></PrimeVueButton>
      <div class="content-wrapper">
        <h4 class="header">Data Usage</h4>
        <p class="text">
          To help improve Lumigator, you can choose to share completely anonymized usage data. We do
          not profile you or track your location or web activity. Do you allow us to collect this
          data? You can always change your choice in Settings.
        </p>
        <div class="actions">
          <PrimeVueButton size="small" severity="secondary" @click="declineConsent" rounded
            >No</PrimeVueButton
          >
          <PrimeVueButton size="small" @click="acceptConsent" rounded>Yes</PrimeVueButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Button } from 'primevue'

export default {
  name: 'ConsentBanner',
  emits: ['accept', 'reject'],
  components: {
    PrimeVueButton: Button,
  },
  setup(_props, { emit }) {
    function acceptConsent() {
      emit('accept')
    }

    function declineConsent() {
      emit('reject')
    }

    return {
      acceptConsent,
      declineConsent,
    }
  },
}
</script>

<style scoped lang="scss">
@use '@/styles/variables';
@use '@/styles/mixins';

.consent-banner {
  position: fixed;
  bottom: 0;
  color: variables.$l-grey-100;
  text-align: center;

  display: flex;
  width: 100%;
  padding: 0.5rem;
  justify-content: center;
  align-items: center;

  border-top: 0.5px solid variables.$border-stroke;
  background: variables.$black;
}

.container {
  position: relative;
  width: 100%;
  display: flex;
  justify-content: center;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 31.75rem;
  padding: 0.5rem 0rem;
  align-items: center;
}

.header {
  @include mixins.paragraph-2;
  color: variables.$white;
}

.text {
  color: variables.$l-grey-100;

  @include mixins.paragraph;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.close-button {
  position: absolute;
  margin-right: 2rem;
  top: 0;
  right: 0;
}
</style>
