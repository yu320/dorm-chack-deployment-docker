import { useAuth } from '~/composables/useAuth'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.directive('permission', {
    mounted(el, binding) {
      const { hasPermission } = useAuth()
      const permission = binding.value

      if (!hasPermission(permission)) {
        // Remove the element from the DOM if permission is denied
        if (el.parentNode) {
          el.parentNode.removeChild(el)
        }
      }
    },
    // Handle updates if permissions change dynamically (e.g. user switches role without refresh)
    updated(el, binding) {
      const { hasPermission } = useAuth()
      const permission = binding.value

      if (!hasPermission(permission)) {
         if (el.parentNode) {
          el.parentNode.removeChild(el)
        }
      } else {
          // If permission is granted but element was removed? 
          // Vue directives on removed elements don't trigger update easily.
          // Usually re-render handles this. 
          // For simple cases, removing is enough.
      }
    }
  })
})
