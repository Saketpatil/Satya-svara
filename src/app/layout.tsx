import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { Toaster } from "react-hot-toast";

export const metadata: Metadata = {
  title: "SatyaSvara | The Fake Audio Detector",
  description:
    "Satya-Svara is an advanced deepfake audio detection system leveraging CNN and RNN models to identify fake audio with precision. Featuring a sleek and responsive Next.js frontend, it empowers users to distinguish authentic voices from manipulated audio in the digital age. Stay ahead in combating misinformation with cutting-edge technology and seamless usability.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`antialiased`}>
        <Header />
        <Toaster />
        {children}
        <Footer />
      </body>
    </html>
  );
}
