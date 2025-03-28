<template>
  <div class="wrapper">
    <div class="header">
      <div class="header-actions">
        <Button
          severity="secondary"
          rounded
          :disabled="true"
          icon="pi pi-download"
          label="Download Results"
          @click="handleDownloadResultsClicked"
        ></Button>
        <Button
          severity="danger"
          rounded
          label="Delete Experiment"
          icon="pi pi-trash"
          @click="handleDeleteExperimentClicked"
        ></Button>
      </div>
    </div>
    <div class="body-wrapper">
      <div class="field" @click="copyToClipboard(experiment.id)">
        <h6 class="field-title">Experiment id</h6>
        <div
          style="
            display: flex;
            gap: 0.5rem;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
          "
        >
          <p class="field-value">{{ experiment.id }}</p>
          <i
            v-tooltip="'Copy ID'"
            :class="isCopied ? 'pi pi-check' : 'pi pi-clone'"
            style="font-size: 14px; padding-left: 3px"
          ></i>
        </div>
      </div>
      <div class="field">
        <h6 class="field-title">title</h6>
        <p class="field-value">{{ experiment.name }}</p>
      </div>
      <div class="field">
        <h6 class="field-title">description</h6>
        <p class="field-value">{{ experiment.description }}</p>
      </div>
      <div class="field">
        <h6 class="field-title">dataset</h6>
        <p class="field-value">{{ experiment.dataset }}</p>
      </div>
      <div class="field">
        <h6 class="field-title">Maximum samples</h6>
        <p class="field-value">{{ experiment.max_samples }}</p>
      </div>
      <div class="field">
        <h6 class="field-title">use-case</h6>
        <p class="field-value">{{ experiment.task_definition.task }}</p>
      </div>
      <div class="field">
        <h6 class="field-title">created</h6>
        <p class="field-value">{{ experiment.created_at }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getAxiosError } from '@/helpers/getAxiosError'
import { experimentsService } from '@/sdk/experimentsService'
import type { Experiment } from '@/types/Experiment'
import { useMutation } from '@tanstack/vue-query'
import { Button, useConfirm, useToast } from 'primevue'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps<{
  experiment: Experiment
}>()

const confirm = useConfirm()

const isCopied = ref(false)

const copyToClipboard = async (longString: string) => {
  isCopied.value = true
  setTimeout(() => {
    isCopied.value = false
  }, 3000)
  await navigator.clipboard.writeText(longString)
}

const toast = useToast()
const router = useRouter()

const deleteExperimentMutation = useMutation({
  mutationFn: experimentsService.deleteExperiment,
  onMutate: () => {
    toast.add({
      group: 'br',
      severity: 'info',
      summary: 'Deleting experiment',
      detail: 'Deleting experiment',
      life: 3000,
    })
  },
  onError: (error) => {
    toast.add({
      group: 'br',
      severity: 'error',
      summary: 'Error deleting experiment',
      detail: getAxiosError(error),
    })
  },
  onSuccess: () => {
    toast.add({
      group: 'br',
      severity: 'success',
      summary: 'Experiment deleted',
      detail: 'Experiment deleted',
      life: 3000,
    })
    router.push('/experiments')
  },
})

const handleDownloadResultsClicked = () => {
  console.log('Download Results clicked')
}

const handleDeleteExperimentClicked = () => {
  confirm.require({
    message: `This will permanently delete the experiment and all its model runs.`,
    header: `Delete  Experiment?`,
    icon: 'pi pi-info-circle',
    rejectLabel: 'Cancel',
    rejectProps: {
      label: 'Cancel',
      severity: 'secondary',
      // style: 'color: #fff; background-color: #363636; border: none; border-radius: 46px;',
      outlined: true,
    },
    acceptProps: {
      label: 'Delete Experiment',
      // style: 'color: #fff; background-color: #9F1A1C; border: none; border-radius: 46px; ',
      severity: 'danger',
    },
    accept: () => {
      deleteExperimentMutation.mutate(props.experiment.id)
    },
    reject: () => {},
  })
}
</script>

<style lang="scss" scoped>
@use '@/styles/mixins.scss';

.header {
  display: flex;
  justify-content: flex-end;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.wrapper {
  display: flex;
  gap: 1.5rem;
  flex-direction: column;
}

.body-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2.44rem;
}

.field-title {
  color: var(--l-grey-200);
  @include mixins.captions-caps;
}

.field-value {
  color: var(--White, #fff);
  font-size: 0.875rem;
}

.field {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}
</style>
