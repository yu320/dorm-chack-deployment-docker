import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import TheHeader from '~/components/layout/TheHeader.vue';
import { createTestingPinia } from '@pinia/testing';
import { useAuth } from '~/composables/useAuth';
import { useI18n } from 'vue-i18n';

// Mock useI18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    locale: ref('en'),
    t: (key: string) => key, // Simple mock: returns the key itself
  }),
}));

describe('TheHeader', () => {
  it('renders correctly when not authenticated', () => {
    const wrapper = mount(TheHeader, {
      global: {
        plugins: [createTestingPinia()],
        stubs: {
          NuxtLink: { template: '<a><slot /></a>' }, // Stub NuxtLink
        },
      },
    });

    // Mock useAuth to return unauthenticated state
    const auth = useAuth();
    auth.isAuthenticated.value = false;
    auth.user.value = null;

    expect(wrapper.text()).toContain('header.title');
    expect(wrapper.text()).toContain('login.signIn'); // Should show login button
    expect(wrapper.text()).not.toContain('header.logout'); // Should not show logout button
  });

  it('renders correctly when authenticated', async () => {
    const wrapper = mount(TheHeader, {
      global: {
        plugins: [createTestingPinia()],
        stubs: {
          NuxtLink: { template: '<a><slot /></a>' }, // Stub NuxtLink
        },
      },
    });

    // Mock useAuth to return authenticated state
    const auth = useAuth();
    auth.isAuthenticated.value = true;
    auth.user.value = { username: 'testuser', email: 'test@example.com', full_name: 'Test User', roles: [], permissions: [] };

    await wrapper.vm.$nextTick(); // Wait for reactivity

    expect(wrapper.text()).toContain('header.title');
    expect(wrapper.text()).toContain('header.welcome, testuser'); // Should show welcome message with username
    expect(wrapper.text()).toContain('header.logout'); // Should show logout button
    expect(wrapper.text()).not.toContain('login.signIn'); // Should not show login button
  });
});