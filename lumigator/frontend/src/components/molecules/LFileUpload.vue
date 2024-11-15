<template>
  <div class="l-upload">
    <input
      ref="input"
      type="file"
      style="display: none"
      @change="handleFileChange"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useConfirm } from "primevue/useconfirm";


const props = defineProps({
  entity: String
})

const emit = defineEmits(['l-file-upload']);

const input = ref(null)
const selectedFile = ref();
const fileName = ref(''); // State to hold the name of the selected file
const confirm = useConfirm();

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    fileName.value = file.name;
    selectedFile.value = file;
    confirmUpload();
  } else {
    fileName.value = '';
  }
};

function confirmUpload() {
  confirm.require({
    message: `${fileName.value}? `,
    header: `Confirm  ${props.entity} upload`,
    icon: 'pi pi-upload',
    rejectProps: {
      label: 'Cancel',
      severity: 'secondary',
      outlined: true
    },
    acceptProps: {
      label: 'Upload'
    },
    accept:() => {
      uploadConfirmed();
    },
    reject: () => {
      cancelUpload();
    },
    close: false
  })
}

function reset() {
  input.value.value = null;
  selectedFile.value = null;
  fileName.value = '';
}

function cancelUpload() {
  // Clear the file input and reset state
  reset();
}

function uploadConfirmed() {
  emit('l-file-upload', selectedFile.value);
  reset();
}

defineExpose({
  input
})
</script>
