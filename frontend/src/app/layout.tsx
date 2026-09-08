import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IP-SAKTI Sahayak",
  description:
    "Multilingual AI-powered decision-support for Ayurveda Intellectual Property and regulatory guidance. Decision-support only — not legal advice.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
