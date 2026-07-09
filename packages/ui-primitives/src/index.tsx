import { JSX, splitProps } from "solid-js";

export interface ButtonProps extends JSX.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline";
}

export function Button(props: ButtonProps) {
  const [local, others] = splitProps(props, ["variant", "class", "children"]);

  const baseClass = "px-4 py-2 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";

  const variantClasses = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    secondary: "bg-gray-800 text-white hover:bg-gray-900 focus:ring-gray-700",
    outline: "border border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-gray-500"
  };

  const computedClass = () => {
    const variant = local.variant || "primary";
    return `${baseClass} ${variantClasses[variant]} ${local.class || ""}`.trim();
  };

  return (
    <button class={computedClass()} {...others}>
      {local.children}
    </button>
  );
}

export interface PriceFormatterProps {
  amount: number;
  currency?: string;
  locale?: string;
}

export function PriceFormatter(props: PriceFormatterProps) {
  const formattedPrice = () => {
    return new Intl.NumberFormat(props.locale || "en-US", {
      style: "currency",
      currency: props.currency || "USD",
    }).format(props.amount);
  };

  return <span class="font-semibold text-gray-900">{formattedPrice()}</span>;
}
