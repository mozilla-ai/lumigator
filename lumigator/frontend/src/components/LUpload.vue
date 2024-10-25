<script setup>
import { ref } from 'vue';
import http from '@/services/http/index.js';
const emit = defineEmits(['dataset-upload']);
const fileName = ref(''); // State to hold the name of the selected file
const selectedFile = ref();

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    fileName.value = file.name; // Update the fileName ref
    selectedFile.value = file;
  } else {
    fileName.value = '';
  }
};

const uploadFile = async () => {
  if (!selectedFile.value) {
    return; // No file selected
  }

  try {
    // Create a new FormData object and append the selected file and the required format
    const formData = new FormData();
    formData.append('dataset', selectedFile.value); // Attach the file
    formData.append('format', 'experiment'); // Specify the format as required

    const response = await http.post('datasets/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    console.log('File uploaded successfully:', response.data);
    emit('dataset-upload');
    fileName.value = null;
    selectedFile.value = null;
  } catch (error) {
    console.error('Error uploading the file:', error);
  }
};
</script>
<template>
  <div class="actions-container">
    <label
			v-if="!fileName"
			for="file-input"
			class="upload-label">
			Choose a Dataset file
		</label>
    <input id="file-input" type="file" @change="handleFileChange" />
    <button
			v-if="fileName"
			@click="uploadFile()"
			class="confirm-btn"
			>
				Confirm
		</button>
    <p
			v-if="fileName"
			class="file-name"
		>
      Selected file: <span>{{ fileName }}
		</span>
    </p>
  </div>
</template>

<style scoped>
.actions-container {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* Add your styles here */
/* Hide the actual file input element */
#file-input {
  display: none;
}

/* Style the label that acts as a button */
.upload-label,
.confirm-btn {
  display: inline-block;
  padding: 10px 20px;
  color: white;
  background-color: #e0c414;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  max-width: 200px;
}

.confirm-btn {
  background-color: #007bff;
}

.upload-label:hover {
  box-shadow: 2px 8px 45px rgba(0, 0, 0, 0.15);
  background-color: #bca50d;
}

/* Optional - style the file name display */
.file-name {
  margin-left: 10px;
  font-size: 0.9em;
  color: #e1dddde9;

  span {
    font-weight: bold;
  }
}
</style>
