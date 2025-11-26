import { ref, watch, onMounted } from 'vue';

export const useTheme = () => {
  const theme = ref<'light' | 'dark'>('light');

  const setTheme = (newTheme: 'light' | 'dark') => {
    theme.value = newTheme;
    if (process.client) {
      localStorage.setItem('theme', newTheme);
      if (newTheme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  };

  const toggleTheme = () => {
    setTheme(theme.value === 'light' ? 'dark' : 'light');
  };

  onMounted(() => {
    if (process.client) {
      const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
      if (savedTheme) {
        setTheme(savedTheme);
      } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        setTheme('dark');
      }
    }
  });

  return {
    theme,
    toggleTheme,
  };
};