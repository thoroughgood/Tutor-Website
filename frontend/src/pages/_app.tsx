import "@/styles/globals.css"
import type { AppProps } from "next/app"
import Layout from "./_layout"
import { ThemeProvider } from "@/components/themeProvider"
import UserProvider from "@/components/userProvider"
import { QueryClient, QueryClientProvider } from "react-query"

const queryClient = new QueryClient()

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="light"
      enableSystem
      disableTransitionOnChange
    >
      <QueryClientProvider client={queryClient}>
        <UserProvider>
          <Layout>
            <Component {...pageProps} />
          </Layout>
        </UserProvider>
      </QueryClientProvider>
    </ThemeProvider>
  )
}
