<template>
  <nav class="l-main-menu-container">
    <Menu :model="menuItems">
      <template #start>
        <div class="l-main-menu__logo">
          <img src="@/assets/lumigator.svg" alt="lumigator-logo" />
        </div>
      </template>
      <template #item="{ item }">
        <router-link
          :to="item.path"
          class="l-main-menu__link"
          :disabled="item.isDisabled"
          @click="showSlidingPanel = false"
        >
          <span :class="item.icon"></span>
          <span ripple class="l-main-menu__link-label">{{ item.name }} </span>
        </router-link>
      </template>
    </Menu>
  </nav>
</template>

<script lang="ts" setup>
import Menu from 'primevue/menu'
import { useSlidePanel } from '@/composables/useSlidePanel'
const { showSlidingPanel } = useSlidePanel()

const menuItems = [
  {
    path: '/datasets',
    name: 'datasets',
    icon: 'pi pi-dataset',
    isDisabled: false,
  },
  {
    path: '/experiments',
    name: 'experiments',
    icon: 'pi pi-experiments',
    isDisabled: false,
  },
  {
    path: '/settings',
    name: 'settings',
    icon: 'pi pi-cog',
    isDisabled: false,
  },
]
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.l-main-menu-container {
  background-color: $l-menu-bg;
  padding: 0;
}

.l-main-menu {
  &__logo {
    height: 5rem;
    will-change: filter;
    transition: filter 300ms;
    font-family: 'Zilla Slab', sans-serif;
    font-size: 1.5em;
    text-wrap: nowrap;
    font-weight: 500;
    cursor: default;
    display: flex;
    padding: calc($l-spacing-1 / 2);
    padding-top: 0;
    align-items: center;

    img {
      height: 1.5em;
    }
  }
  .logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
  }

  &__link {
    padding: calc($l-spacing-1 / 2) $l-spacing-1;
    display: flex;
    gap: calc($l-spacing-1 / 2);
    align-items: center;
    color: $l-menu-item-color;
    text-transform: capitalize;

    :hover,
    :focus {
      background-color: $l-menu-bg;
    }

    &-label {
      font-size: $l-menu-font-size;
      font-weight: $l-font-weight-normal;
    }
  }
}

.l-main-menu__link.router-link-active,
.l-main-menu__link:hover span {
  color: $white;
}
</style>
