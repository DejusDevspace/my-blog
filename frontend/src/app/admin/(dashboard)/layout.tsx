import { AdminShell } from "@/components/layout";

export default function DashboardLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return <AdminShell>{children}</AdminShell>;
}
