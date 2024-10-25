<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
const props = defineProps({
  datasets: Array
})
const emit = defineEmits(['dataset-selected', 'remove'])

const formatDate = (dateString) => {
  const date = new Date(dateString);

  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0'); // getMonth() returns 0-11
  const year = String(date.getFullYear()).slice(-2); // Get last two digits of year
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${day}/${month}/${year} - ${hours}:${minutes}`;
}

const onDatasetSelect = (id) => {
	emit('dataset-selected', id)
}

const onRemoveDataset = (id) => {
	emit('dataset-remove', id)
}

</script>

<template>
  <div class="l-datasets">
    <div class="l-datasets__list-container">
      <ul class="l-datasets__list">
        <li v-for="dataset in props.datasets" :key="dataset.id">
          <div
						class="l-datasets__list-card"
						@click="onDatasetSelect(dataset.id)"
					>
            <span> {{ formatDate(dataset.created_at) }}</span>
            <span>File name: {{ dataset.filename }}</span>
            <span>Ground truth: {{ dataset.ground_truth ? '✅ ' : ' ❌' }}</span>
            <span>Size: {{ dataset.size }} kb</span>
          </div>
					<span class="l-datasets__list-remove" @click="onRemoveDataset(dataset.id)">🗑️</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped lang="scss">
.l-datasets {
  $root: &;

  &__list-container {
    display: grid;
  }

  &__list {
    display: flex;
		flex-direction: column;
    flex-wrap: wrap;
    list-style-type: none;

		li {
			display: flex;
			align-items: center;
		}

    &-card {
			cursor: pointer;
      margin: 1rem;
			padding: 1rem;
			box-shadow: 2px 8px 45px rgba(0, 0, 0, 0.15);
      border-radius: 12px;
      overflow: hidden;
      transition: all 0.2s linear;
      display: flex;
      flex-direction: column;
			width: 300px;

      &:hover {
      	box-shadow: 2px 4px 15px rgba(252, 228, 228, 0.401);
        transform: translate3D(0, -2px, 0);
      }
    }
		&-remove {
			cursor: pointer;
			// background:transparent;
		}

  }
}
</style>
