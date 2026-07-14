import { cva } from "class-variance-authority";

export const buttonVariants = cva(
  "inline-flex min-h-11 items-center justify-center gap-2 rounded-md px-4 text-sm font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-60",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-[#084b48]",
        secondary: "bg-secondary text-secondary-foreground hover:bg-[#d8efec]",
        outline: "border bg-card hover:bg-muted",
        ghost: "hover:bg-muted",
        destructive: "bg-destructive text-destructive-foreground hover:bg-[#8f1c13]",
      },
      size: { default: "h-11", sm: "h-9 min-h-9 px-3", icon: "size-11 px-0" },
    },
    defaultVariants: { variant: "default", size: "default" },
  },
);
