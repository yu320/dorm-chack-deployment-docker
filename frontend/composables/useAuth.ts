import { ref, computed, watch } from 'vue'

// This is a simplified user type, you can expand it based on your `schemas.py`
interface User {
  username: string;
  email: string; // Add email to User interface
  roles: { name: string }[];
  permissions: string[];
  student?: { // Make student optional as it might not always be present
    student_id_number: string;
    full_name: string; // Also include full_name for consistency
  };
}

export const useAuth = () => {
  // const token = useCookie<string | null>('auth_token'); // Removed, token is HttpOnly
  const user = useState<User | null>('user', () => null); // Initialize with null
  const config = useRuntimeConfig();

  // Watch user state for logging
  // watch(user, (newUser) => {
  //   console.log('Auth: User changed:', newUser ? 'present' : 'null');
  //   if (newUser) {
  //     console.log('Auth: User details:', JSON.stringify(newUser, null, 2));
  //   }
  // }, { immediate: true, deep: true });

  const apiFetch = (url: string, options: any = {}) => {
    // HttpOnly cookie is automatically sent by the browser, no need to add Authorization header manually
    return $fetch(url, {
      baseURL: config.public.apiBase, // Use the configured API base URL
      credentials: 'include', // Ensure cookies are sent with requests
      ...options,
    });
  }

  const login = async (username: string, password: string) => {
    // console.log('Auth: Attempting login...');
    try {
      // Use URLSearchParams to properly encode the form data
      const params = new URLSearchParams();
      params.append('grant_type', 'password');
      params.append('username', username);
      params.append('password', password);

      // This request gets the token and, more importantly, sets the HttpOnly cookie
      await $fetch('/api/v1/token', {
        baseURL: config.public.apiBase,
        method: 'POST',
        body: params,
        credentials: 'include', // Ensure cookies are set and sent
        // headers: { 'Content-Type': 'application/x-www-form-urlencoded' } // $fetch sets this automatically for URLSearchParams
      });

      // After the cookie is set, fetch the user details from the /users/me endpoint
      const success = await fetchUser();
      return success;

    } catch (error: any) {
      console.error('Auth: Login failed:', error);
      if (error.response) {
        console.error('Auth: Error response:', error.response._data);
      }
      user.value = null; // Clear user on login failure
      return false;
    }
  };

  const fetchUser = async () => {
    // console.log('Auth: Attempting fetchUser...');
    // If user is already set, or if we have an HttpOnly cookie,
    // the backend will return user info for /users/me.
    // If not authenticated, /users/me will return 401, which will be caught.
    try {
      const fetchedUser = await apiFetch('/api/v1/users/me/') as User;
      user.value = fetchedUser;
      // console.log('Auth: fetchUser successful. User set.');
      return true;
    } catch (error: any) {
      // console.error('Auth: Failed to fetch user (possibly unauthenticated):', error);
      if (error.response && error.response.status !== 401) {
        console.error('Auth: Failed to fetch user:', error);
      }
      user.value = null; // Clear user if fetching fails
      return false;
    }
  };

  const logout = async () => {
    // console.log('Auth: Logging out...');
    try {
      // Call backend logout endpoint to clear HttpOnly cookie
      await apiFetch('/api/v1/logout', {
        method: 'POST',
      });
      user.value = null; // Clear user locally
      // console.log('Auth: Logout complete. User cleared.');
    } catch (error) {
      // console.error('Auth: Logout failed:', error);
      // Even if backend logout fails, clear local user state for consistency
      user.value = null;
    }
  };

  const register = async (username: string, password: string, studentIdNumber: string, email: string, bedNumber: string) => {
    // console.log('Auth: Attempting registration...');
    try {
      const data = await $fetch('/api/v1/register', { // Updated path to /api/v1/register
        baseURL: config.public.apiBase,
        method: 'POST',
        body: { username, password, student_id_number: studentIdNumber, email, bed_number: bedNumber },
      });
      // console.log('Auth: Registration successful. Data:', data);
      return true;
    } catch (error) {
      // console.error('Auth: Registration failed:', error);
      throw error; // Re-throw to allow component to handle specific errors
    }
  };

  const hasPermission = (permission: string) => {
    if (!user.value || !user.value.permissions) {
      return false;
    }
    // An admin with 'admin:full_access' should be able to access everything.
    return user.value.permissions.includes('admin:full_access') || user.value.permissions.includes(permission);
  }

  const isAuthenticated = computed(() => {
    // Authentication status is now based on whether a user object is present and valid
    const authenticated = !!user.value;
    // console.log('Auth: isAuthenticated computed based on user:', authenticated);
    return authenticated;
  });

  return {
    user, // Removed token from exposed properties
    login,
    logout,
    fetchUser,
    isAuthenticated,
    hasPermission,
    apiFetch,
  };
};
