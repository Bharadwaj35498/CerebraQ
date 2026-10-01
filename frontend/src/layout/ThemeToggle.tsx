import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';
export function ThemeToggle() {
  const [light, setLight] = useState(false);
  useEffect(() => { document.documentElement.classList.toggle('light', light); document.documentElement.classList.toggle('dark', !light); }, [light]);
  return <button className="rounded-input border border-border p-2 text-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-classical" type="button" aria-label={light ? 'Switch to dark theme' : 'Switch to light theme'} onClick={() => setLight(value => !value)}>{light ? <Moon size={18}/> : <Sun size={18}/>}</button>;
}
