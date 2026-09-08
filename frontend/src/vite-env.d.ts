/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_PUBLIC_APP_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module "*.png" {
  const src: string;
  export default src;
}

interface SpeechRecognition extends EventTarget {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
}

interface SpeechRecognitionEvent extends Event {
  results: {
    [index: number]: { [index: number]: { transcript: string }; isFinal: boolean };
    length: number;
  };
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
}

interface Window {
  SpeechRecognition?: { new (): SpeechRecognition };
  webkitSpeechRecognition?: { new (): SpeechRecognition };
}
