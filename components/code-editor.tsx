"use client";

import { useEffect, useState } from "react";
import { Editor } from "@monaco-editor/react";

interface CodeEditorProps {
	code: string;
	onChange: (code: string) => void;
}

export default function CodeEditor({ code, onChange }: CodeEditorProps) {
	const [mounted, setMounted] = useState(false);

	useEffect(() => {
		setMounted(true);
	}, []);

	if (!mounted) {
		return (
			<div className="w-full h-[500px] border border-border rounded-md bg-muted flex items-center justify-center">
				Loading editor...
			</div>
		);
	}

	return (
		<div className="border border-border rounded-md overflow-hidden h-[500px]">
			<Editor
				height="100%"
				defaultLanguage="python"
				value={code}
				onChange={(value) => onChange(value || "")}
				options={{
					minimap: { enabled: false },
					fontSize: 14,
					scrollBeyondLastLine: false,
					automaticLayout: true,
					tabSize: 4,
					insertSpaces: true,
				}}
				theme="vs-dark"
			/>
		</div>
	);
}
