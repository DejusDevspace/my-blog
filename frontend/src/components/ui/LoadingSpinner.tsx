/**
 * LoadingSpinner — the single, canonical loading indicator for d3jusdevspace.
 *
 * Use this component everywhere a loading state needs to be shown:
 *  - Route transitions (via app/loading.tsx)
 *  - React Query isPending / isLoading states
 *  - Inline spinners for buttons, form submissions, etc.
 *
 * Props:
 *  - size: "sm" | "md" | "lg" (default "md")
 *  - label: accessible screen-reader text (default "Loading…")
 *  - fullPage: if true, centres the spinner in the full viewport
 */

import styles from "./LoadingSpinner.module.css";

export type SpinnerSize = "sm" | "md" | "lg";

interface LoadingSpinnerProps {
	size?: SpinnerSize;
	label?: string;
	fullPage?: boolean;
}

const sizeMap: Record<SpinnerSize, number> = {
	sm: 20,
	md: 36,
	lg: 56,
};

export default function LoadingSpinner({
	size = "md",
	label = "Loading\u2026",
	fullPage = false,
}: LoadingSpinnerProps) {
	const px = sizeMap[size];

	return (
		<div
			className={`${styles.wrapper} ${fullPage ? styles.fullPage : ""}`}
			role="status"
			aria-label={label}
		>
			<div className={styles.spinner} style={{ width: px, height: px }}>
				{/* Outer orbit ring */}
				<svg viewBox="0 0 50 50" className={styles.ring} aria-hidden="true">
					<circle
						cx="25"
						cy="25"
						r="20"
						fill="none"
						strokeWidth="3"
						className={styles.track}
					/>
					<circle
						cx="25"
						cy="25"
						r="20"
						fill="none"
						strokeWidth="3"
						strokeLinecap="round"
						strokeDasharray="31.4 94.2"
						className={styles.arc}
					/>
				</svg>

				{/* Inner pulse dot */}
				<span className={styles.dot} />
			</div>

			<span className="sr-only">{label}</span>
		</div>
	);
}
