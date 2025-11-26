import { useAuth } from '~/composables/useAuth';
import { useLocalePath } from '#imports';

export default defineNuxtRouteMiddleware(async (to, from) => {
  const { isAuthenticated, fetchUser, user, hasPermission } = useAuth();
  const localePath = useLocalePath();

  // Define public route names (the part before ___en or ___zh)
  const publicRouteNames = ['login', 'register', 'forgot-password', 'reset-password'];

  // Construct a regex to check if the route name starts with any of the public route names
  const isPublicRoute = publicRouteNames.some(name => to.name?.toString().startsWith(name));

  // If user object doesn't exist, try to fetch it.
  // This is crucial for handling page reloads or direct navigation.
  if (!user.value) {
    await fetchUser();
  }

  // If the user is authenticated
  if (isAuthenticated.value) {
    // If they are trying to access a public route (like login), redirect them to the homepage.
    if (isPublicRoute) {
      return navigateTo(localePath('/'));
    }

    // Check for route-specific permissions defined in page metadata
    const requiredPermission = to.meta.permission as string;
    
    // If a permission is required but the user doesn't have it, redirect.
    // In a more complex app, you might redirect to a dedicated '403 Forbidden' page.
    if (requiredPermission && !hasPermission(requiredPermission)) {
      // You can also show a notification to the user before redirecting.
      // const { showSnackbar } = useSnackbar();
      // showSnackbar('You do not have permission to access this page.', 'error');
      return navigateTo(localePath('/')); // Redirect to a safe page like home/dashboard
    }

  } else { // If the user is not authenticated
    // And if the route is not public, redirect them to the login page.
    if (!isPublicRoute) {
      return navigateTo(localePath('/login'));
    }
  }
  
  // If none of the above conditions are met, allow navigation.
});