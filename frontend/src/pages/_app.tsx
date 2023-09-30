import "@/styles/globals.css"
import type { AppProps } from "next/app"
import Layout from "./_layout"
import { ThemeProvider } from "@/components/themeProvider"
import UserProvider from "@/components/UserProvider"

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <UserProvider>
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </UserProvider>
    </ThemeProvider>
  )
}
