import { ConfiguradorApp } from './configurador/ConfiguradorApp'
import { OptotiposApp } from './optotipos/OptotiposApp'

export function App() {
  const route = window.location.hash.toLowerCase()
  if (route.includes('configurador')) {
    return <ConfiguradorApp />
  }
  return <OptotiposApp />
}
