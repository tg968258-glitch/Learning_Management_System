import * as Icons from "lucide-react";
import type { LucideProps } from "lucide-react";
import type { ComponentType } from "react";

export function Icon({
  name,
  ...props
}: LucideProps & {
  name: string;
}) {
  const IconComponent = Icons[name as keyof typeof Icons] as ComponentType<LucideProps> | undefined;

  if (!IconComponent) {
    return null;
  }

  return <IconComponent {...props} />;
}
