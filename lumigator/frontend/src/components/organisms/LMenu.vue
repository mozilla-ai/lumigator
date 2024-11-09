<template>
  <nav class="l-main-menu-container">
    <Menu :model="routes">
      <template #start>
        <div class="l-main-menu__logo">🐊 Lumigator</div>
      </template>
      <template #item="{ item }">
        <router-link
					:to="item.path"
					class="l-main-menu__link"
					:disabled="item.disabled"
				>
          <span :class="item.icon" />
          <span ripple
						class="l-main-menu__link-label"
					 >{{ item.name }} </span>
        </router-link>
      </template>
    </Menu>
  </nav>
</template>

<script setup>
import Menu from 'primevue/menu';
import { routes } from '@/router'

</script>

<style scoped lang="scss">
.l-main-menu-container {
  background-color: $l-menu-bg;
  padding: 0;
}

.l-main-menu {

  &__logo {
    height: 6rem;
    will-change: filter;
    transition: filter 300ms;
    font-family: 'Zilla Slab', sans-serif;
    font-size: 30px;
    text-wrap: nowrap;
    font-weight: 500;
    cursor: default;
		display: flex;
		align-items: center;
		padding: $l-spacing-1/2;
  }
  .logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
  }

  &__link {
    padding: $l-spacing-1/2 $l-spacing-1;
    display: flex;
    gap: $l-spacing-1/2;
    align-items: center;
    color: $l-menu-item-color;
		text-transform: capitalize;

    :hover,:focus {
      background-color: $l-menu-bg;
			text-shadow: 0px 0px 2px $white;
    }

		&-label {
			font-size: $l-menu-font-size
		}
  }
}

.l-main-menu__link.router-link-active,
.l-main-menu__link:hover span {
  color: $white;
}

</style>
