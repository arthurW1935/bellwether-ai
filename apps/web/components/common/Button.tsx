import React from "react";
import { cn } from "@/lib/cn";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md";
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", children, disabled, ...rest }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled}
        className={cn(
          "rounded-lg font-medium transition-colors inline-flex items-center justify-center",
          {
            "opacity-50 cursor-not-allowed": disabled,
            
            // Variants
            "bg-violet-500 text-white hover:bg-violet-600": variant === "primary",
            "bg-slate-800 text-slate-100 hover:bg-slate-700 border border-slate-700": variant === "secondary",
            "text-slate-300 hover:bg-slate-800": variant === "ghost",

            // Sizes
            "px-3 py-1.5 text-sm": size === "sm",
            "px-4 py-2 text-sm": size === "md",
          },
          className
        )}
        {...rest}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
