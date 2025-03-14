<template>
  <div class="consent-banner">
    <p>
      We use Sentry to send anonymized error reports and improve Lumigator. Do you allow us to
      collect error reports? You can later change your consent from Settings
    </p>
    <div class="actions">
      <PrimeVueButton @click="acceptConsent">Yes</PrimeVueButton>
      <PrimeVueButton @click="declineConsent">No</PrimeVueButton>
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

.consent-banner {
  position: fixed;
  bottom: 0;
  width: 100%;
  background-color: variables.$l-main-bg;
  // background: transparent;
  // border: 1px solid variables.$l-grey-100;
  color: variables.$l-grey-100;
  padding: 10px;
  text-align: center;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}
</style>
