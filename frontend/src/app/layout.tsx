import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "CartMind — Agentic AI Shopping & Customer Experience",
  description:
    "Production-grade Agentic AI shopping assistant with LangChain ReAct loops, LangGraph sentiment triage on Groq, and real-time product comparisons.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} h-full dark`}>
      <body className="min-h-full bg-[#0f1117] text-[#f8fafc] font-sans antialiased flex flex-col">
        {children}
      </body>
    </html>
  );
}
