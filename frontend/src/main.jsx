import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import { ThemeProvider } from 'styled-components'
import { theme } from './theme'
// CSS is now loaded via index.html from public/css/style.css to satisfy deployment requirement
// import './index.css' 

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <App />
    </ThemeProvider>
  </React.StrictMode>,
)
