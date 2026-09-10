import type { ButtonHTMLAttributes, ReactNode } from "react";

export function Button({
  children,
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  variant?: "primary" | "secondary";
}) {
  const base = variant === "primary" ? "primary-button" : "secondary-button";

  return (
    <button
      className={`${base} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
