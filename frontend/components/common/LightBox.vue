<template>
  <Transition name="lightbox-fade">
    <div 
      v-if="visible" 
      @click.self="close" 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
    >
      <img :src="imageUrl" class="max-w-[90vw] max-h-[90vh] object-contain rounded-lg shadow-2xl" />
      <button @click="close" class="absolute top-4 right-4 text-white text-3xl">&times;</button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
const props = defineProps({
  imageUrl: {
    type: String,
    required: true,
  },
  visible: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(['update:visible']);

const close = () => {
  emit('update:visible', false);
};
</script>

<style>
.lightbox-fade-enter-active,
.lightbox-fade-leave-active {
  transition: opacity 0.3s ease;
}
.lightbox-fade-enter-from,
.lightbox-fade-leave-to {
  opacity: 0;
}
</style>
