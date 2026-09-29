import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import CinematicBackground from "@/components/background/CinematicBackground";

const inter = Inter({
    subsets: ["latin"],
    display: 'swap',
    variable: '--font-inter',
});

export const metadata: Metadata = {
    title: "MAVILON AI Recommendation - Discover Stories with Intelligence",
    description: "An intelligent movie and anime recommendation system powered by AI. Discover content based on mood, taste, genre, and story preference.",
    keywords: ["movies", "anime", "AI", "recommendations", "discovery", "cinematic"],
    authors: [{ name: "MAVILON AI Recommendation" }],
    openGraph: {
        title: "MAVILON AI Recommendation - Discover Stories with Intelligence",
        description: "AI-powered cinematic discovery platform for movies and anime",
        type: "website",
    },
};

import { AppContextProvider } from "@/lib/context/app-context";
import ChatWidget from "@/components/ui/ChatWidget";

// ... constants ...

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" className={inter.variable} suppressHydrationWarning>
            <body className={`${inter.className} antialiased`} suppressHydrationWarning>
                <AppContextProvider>
                    <CinematicBackground />
                    <div className="relative z-10">
                        {children}
                    </div>
                    <ChatWidget />
                </AppContextProvider>
            </body>
        </html>
    );
}
