/**
 * Composable for fetching dashboard data based on user role.
 * Encapsulates the API logic to keep the view clean.
 */
export const useHomeData = () => {
  const { isAuthenticated, hasPermission, apiFetch } = useAuth();

  const isAdmin = computed(() => hasPermission('admin:full_access'));

  return useAsyncData('dashboard-data', async () => {
    if (!isAuthenticated.value) return null;

    try {
      if (isAdmin.value) {
        // Fetch Admin Stats and Charts in parallel
        const [stats, charts] = await Promise.all([
          apiFetch('/api/v1/admin/dashboard-stats') as Promise<any>,
          apiFetch('/api/v1/admin/dashboard-charts') as Promise<any>
        ]);

        return {
          ...stats,
          charts
        };
      } else {
        // Fetch Student Data (Latest Inspection)
        const response = await apiFetch('/api/v1/inspections?limit=1') as any;
        return {
          latestInspection: response?.records?.[0] || null
        };
      }
    } catch (error) {
      console.error('Dashboard data fetch failed:', error);
      return null;
    }
  }, {
    watch: [isAuthenticated] // Re-run if auth state changes
  });
};