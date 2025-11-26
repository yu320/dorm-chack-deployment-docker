import { ref, onMounted, onBeforeUnmount } from 'vue';

export function useDropdown() {
  const isOpen = ref(false);
  const dropdownRef = ref<HTMLElement | null>(null);
  const toggleRef = ref<HTMLElement | null>(null);

  const open = () => {
    isOpen.value = true;
  };

  const close = () => {
    isOpen.value = false;
  };

  const toggle = () => {
    isOpen.value = !isOpen.value;
  };

  const handleClickOutside = (event: MouseEvent) => {
    if (
      dropdownRef.value &&
      !dropdownRef.value.contains(event.target as Node) &&
      toggleRef.value &&
      !toggleRef.value.contains(event.target as Node)
    ) {
      close();
    }
  };

  onMounted(() => {
    document.addEventListener('click', handleClickOutside);
  });

  onBeforeUnmount(() => {
    document.removeEventListener('click', handleClickOutside);
  });

  return {
    isOpen,
    dropdownRef,
    toggleRef,
    open,
    close,
    toggle,
  };
}
