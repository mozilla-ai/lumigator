<template>
  <div id="app">
    <div class="content-wrapper">
      <div class="l-menu-container">
        <div class="l-menu__top">
          <div class="l-mode">
            <Button
              v-show="false"
              v-tooltip.right="tooltipConfig"
              icon="pi pi-check"
              severity="secondary"
              size="small"
              label="Hybrid"
              aria-label="Logs"
              style="padding:0;background: transparent; border: none; font-weight: 400;gap: 4px"
              iconClass="mode-icon"
              class="l-mode__selector"
            />
          </div>
          <l-menu />
        </div>
        <div class="external-links-container">
          <ul>
            <li>
              <a
                href="https://github.com/mozilla-ai/lumigator"
                target="_blank"
              >GitHub <span class="pi pi-arrow-up-right" />
              </a>
            </li>
            <li>
              <a
                href="https://mozilla-ai.github.io/lumigator/"
                target="_blank"
              >Documentation <span class="pi pi-arrow-up-right" />
              </a>
            </li>

          </ul>
        </div>
      </div>
      <div class="l-main-container">
        <ConfirmDialog></ConfirmDialog>
        <Toast
          position="bottom-right"
          group="br"
        >
          <template #message="slotProps">
            <div
              class="toaster-content"
              :class="slotProps.message.severity"
            >
              <span :class="slotProps.message.messageicon" />
              <div class="toaster-content__text">
                <h4>   {{ slotProps.message.summary }}</h4>
                <p v-if="slotProps.message.detail ">{{ slotProps.message.detail  }}  </p>
              </div>
            </div>
          </template>
        </Toast>
        <router-view v-slot="{ Component }">
          <transition
            name="transition-fade"
            mode="out-in"
          >
            <component
              :is="Component"
              @s-disable-scroll="disableScroll = $event"
            />
          </transition>
        </router-view>
      </div>
      <div class="sliding-panel"
           :class="{ open: showSlidingPanel }"
      >
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import LMenu from '@/components/organisms/LMenu.vue';
import { useDatasetStore } from '@/stores/datasets/store'
import { useExperimentStore } from '@/stores/experiments/store'
import { useSlidePanel } from '@/composables/SlidingPanel';
import ConfirmDialog from 'primevue/confirmdialog';
import Toast from 'primevue/toast';
import Button from 'primevue/button';

const datasetStore = useDatasetStore();
const experimentStore = useExperimentStore();

const tooltipConfig = ref({
  value: `Lumigator is connected to external GPUs.`,
  pt: {
    root: {
      style: {
      background: `transparent`
      }
    },
    text: {
      style: {
      background: `black`,
      }
    },
    arrow: {
      style: {
      ['border-right-color']: `black`
      }
    }
  }
})

const { showSlidingPanel } = useSlidePanel();
onMounted(async () => {
  await experimentStore.loadExperiments();
  await datasetStore.loadDatasets();
})
</script>

<style scoped lang="scss">
#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background-color: $l-main-bg;
  padding: $l-spacing-1;

  .header {
    background-color: $l-main-bg;
  }

  .content-wrapper {
    display: flex;
    gap: 1rem;
    flex: 1;
    overflow: hidden;
  }

  .l-menu-container {
    height: 95vh;
    background-color: $l-main-bg;
    display: flex;
    flex-direction: column;
    justify-content: space-between;

    .l-mode {
      padding-left: $l-spacing-1;

      .l-mode__selector {
        color: $l-menu-item-color;
        font-size: $l-font-size-sm;
      }
    }

    .external-links-container {
      padding: 0 1.5rem;

      a {
        font-size: $l-font-size-sm;
        color: $l-grey-100;
        font-weight: $l-font-weight-normal;

        &:hover {
          color: $white;
        }

        span.pi {
          font-size: $l-font-size-xs;
        }
      }
    }
  }

  .l-main-container {
    flex: 1;
    background-color: $l-card-bg;
    transition: margin-right 0.3s ease-in-out;
    background-color: $l-card-bg;
    border-radius: $l-main-radius;
    display: grid;
    text-align: center;
    border: 1px solid black

  }

  .sliding-panel {
    width: 0;
    background-color: $l-main-bg;
    transition: width 0.3s ease-in-out;
    overflow: hidden;
  }

  .sliding-panel.open {
    width: $l-sliding-panel-size;
    overflow-y: auto;
  }

  .l-main-container {
    transition: flex-grow 0.3s, margin-right 0.3s;
  }

  .sliding-panel.open+.l-main-container {
    margin-right: 0;
  }
}
</style>

<style lang="scss">
  .toaster-content {
    width: 100%;
    display: flex;
    gap: 5px;

    span {
      padding: 5px;
    }

    p {
      font-size: $l-menu-font-size;
    }

    &.error {
      color: $l-grey-100;
      h4 {
        font-weight: $l-font-weight-semibold;
      }
    }
  }

  .mode-icon {
    font-size: $l-font-size-xs!important;
  }
</style>
