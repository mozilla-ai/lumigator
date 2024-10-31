<template>
  <nav class="l-main-menu-container">
    <Menu :model="items">
      <template #start>
        <div class="l-main-menu__logo">🐊 Lumigator</div>
      </template>
      <template #item="{ item }">
        <router-link :to="item.route" class="l-main-menu__link" :disabled="item.disabled">
          <span :class="item.icon" />
          <span ripple>{{ item.label }} </span>
        </router-link>
      </template>
    </Menu>
  </nav>
</template>

<script setup>
import { ref } from 'vue';
import Menu from 'primevue/menu';
import { useRouter } from 'vue-router';
const router = useRouter();

// const menuItems = ref([
//   { label: 'Datasets', icon: 'pi pi-fw pi-database', route: '/datasets' },
//   { label: 'Experiments', icon: 'pi pi-fw pi-chart-line', route: '/experiments' },
//   { label: 'Groundtruth Generation', icon: 'pi pi-fw pi-pencil', route: '/groundtruth-generation' },
//   { label: 'Documentation', icon: 'pi pi-fw pi-book', route: '/documentation' },
//   { label: 'Logs', icon: 'pi pi-fw pi-file', route: '/logs' },
//   { label: 'API Explorer', icon: 'pi pi-fw pi-compass', route: '/api-explorer' },
//   { label: 'Settings', icon: 'pi pi-fw pi-cog', route: '/settings' },
// ]);
const items = ref([
  {
    label: 'Router Link',
    icon: 'pi pi-palette',
    route: '/theming/unstyled',
    disabled: false,
  },
  {
    label: 'Programmatic',
    disabled: true,
    icon: 'pi pi-link',
    command: () => {
      router.push('/introduction');
    },
  },
  {
    label: 'External',
    icon: 'pi pi-home',
    disabled: false,
    url: 'https://vuejs.org/',
  },
]);
</script>

<style scoped lang="scss">
.l-main-menu-container {
  background-color: $l-menu-bg;
  padding: 0;
}

.l-main-menu {
  width: 100%;
  border: none;

  &__logo {
    height: 6rem;
    will-change: filter;
    transition: filter 300ms;
    font-family: 'Zilla Slab', sans-serif;
    font-size: 30px;
    text-wrap: nowrap;
    font-weight: 400;
    cursor: default;
  }
  .logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
  }

  &__link {
    padding: $l-spacing-1;
    display: flex;
    gap: $l-spacing-1;
    align-items: center;
    color: $l-menu-item-color;

    :hover,:focus {
      background-color: $l-menu-bg;
    }
  }
}
.l-main-menu__link:hover span {
  color: $white;
}
</style>
