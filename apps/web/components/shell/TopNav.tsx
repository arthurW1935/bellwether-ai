"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/cn";

export function TopNav() {
  const pathname = usePathname();

  const links = [
    { name: "Brief", href: "/brief" },
    { name: "Watchlist", href: "/watchlist" },
    { name: "Discover", href: "/discover" },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
        <Link href="/" className="font-semibold tracking-tight text-slate-100">
          Bellwether
        </Link>
        <nav className="flex items-center space-x-1">
          {links.map((link) => {
            const isActive = pathname?.startsWith(link.href);
            const isBrief = link.href === "/brief";

            return (
              <Link
                key={link.name}
                href={link.href}
                className={cn(
                  "px-3 py-1.5 text-sm font-medium transition-colors rounded-lg",
                  isActive
                    ? "bg-slate-800/50 text-violet-400"
                    : isBrief
                      ? "text-slate-300 hover:text-slate-100"
                      : "text-slate-400 hover:text-slate-100"
                )}
              >
                {link.name}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
