"use client";

import { useEffect, useState, useMemo } from "react";
import { BlockNoteEditor as BlockNoteEditorType } from "@blocknote/core";
import { useCreateBlockNote } from "@blocknote/react";
import { BlockNoteView } from "@blocknote/mantine";
import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";

// TODO: Refactor to use a more flexible theme system (custom theming)
interface BlockNoteEditorProps {
	initialMarkdown?: string;
	onChange: (markdown: string) => void;
	editable?: boolean;
}

export default function BlockNoteEditor({
	initialMarkdown = "",
	onChange,
	editable = true,
}: BlockNoteEditorProps) {
	const [initialContentLoaded, setInitialContentLoaded] = useState(false);

	// Mock file upload function
	const handleUpload = async (file: File) => {
		// Simulate network delay
		await new Promise((resolve) => setTimeout(resolve, 1500));

		// Return a mock placeholder URL using the file name or a generic placeholder
		return `https://placehold.co/800x400/162440/00e5ff.png?text=${encodeURIComponent(file.name)}`;
	};

	// Create the editor instance.
	const editor = useCreateBlockNote({
		uploadFile: handleUpload,
	});

	// Load initial markdown into the editor.
	useEffect(() => {
		async function loadMarkdown() {
			if (initialMarkdown) {
				const blocks = await editor.tryParseMarkdownToBlocks(initialMarkdown);
				editor.replaceBlocks(editor.document, blocks);
			}
			setInitialContentLoaded(true);
		}

		if (!initialContentLoaded && editor) {
			loadMarkdown();
		}
	}, [editor, initialMarkdown, initialContentLoaded]);

	// Listen for changes and convert back to markdown.
	const handleChange = async () => {
		const markdown = await editor.blocksToMarkdownLossy(editor.document);
		onChange(markdown);
	};

	if (!initialContentLoaded) {
		return (
			<div className="flex h-32 items-center justify-center text-text-tertiary">
				<span className="font-mono text-sm animate-pulse">
					Loading editor...
				</span>
			</div>
		);
	}

	return (
		<div className="blocknote-wrapper relative min-h-125">
			<BlockNoteView
				editor={editor}
				editable={editable}
				onChange={handleChange}
				theme="dark" // We will use 'dark' for the cyberpunk aesthetic, but BlockNote supports theming.
				className="min-h-full"
			/>
		</div>
	);
}
