import { useEffect, useRef, useState } from "react";
import { sendAssistantMessage, type AssistantChatMessage } from "../api";
import { matchFaq } from "../assistantFaq";
import { loadAssistantMessages, saveAssistantMessages } from "../guideStorage";
import type { Messages } from "../i18n";
import { extractGesture, type SentinelPose } from "../sentinelPose";
import { NamedCopy } from "./SentinelBuddy";

type Props = {
  t: Messages;
  lang: string;
  onBack: () => void;
  onBusyChange?: (busy: boolean) => void;
  onPoseChange?: (pose: SentinelPose | null) => void;
  onPointAccount?: () => void;
};

const MAX_HISTORY_SENT = 16;
const MAX_INPUT_CHARS = 500;

/** Free-form AI chat, shown inside the guide sheet when the assistant is enabled. */
export function AssistantChat({ t, lang, onBack, onBusyChange, onPoseChange, onPointAccount }: Props) {
  const [messages, setMessages] = useState<AssistantChatMessage[]>(loadAssistantMessages);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(false);
  const listRef = useRef<HTMLDivElement | null>(null);
  const accountTimer = useRef<number>(0);

  useEffect(() => {
    saveAssistantMessages(messages);
  }, [messages]);

  useEffect(() => {
    onBusyChange?.(sending);
    return () => onBusyChange?.(false);
  }, [sending, onBusyChange]);

  useEffect(() => {
    return () => window.clearTimeout(accountTimer.current);
  }, []);

  const scrollToBottom = () => {
    requestAnimationFrame(() => {
      listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
    });
  };

  const send = async () => {
    const text = input.trim();
    if (!text || sending) return;

    const history = messages.slice(-MAX_HISTORY_SENT);
    const nextMessages: AssistantChatMessage[] = [...messages, { role: "user", content: text }];
    setMessages(nextMessages);
    setInput("");
    setError(false);

    const cannedReply = matchFaq(text, lang, { hasHistory: messages.length > 0 });
    if (cannedReply) {
      const parsed = extractGesture(cannedReply);
      onPoseChange?.(parsed.pose);
      setMessages((prev) => [...prev, { role: "assistant", content: parsed.text }]);
      scrollToBottom();
      if (parsed.pose === "account") {
        window.clearTimeout(accountTimer.current);
        accountTimer.current = window.setTimeout(() => onPointAccount?.(), 1400);
      }
      return;
    }

    setSending(true);
    scrollToBottom();

    try {
      const reply = await sendAssistantMessage(text, lang, history);
      const parsed = extractGesture(reply);
      onPoseChange?.(parsed.pose);
      setMessages((prev) => [...prev, { role: "assistant", content: parsed.text }]);
      if (parsed.pose === "account") {
        window.clearTimeout(accountTimer.current);
        accountTimer.current = window.setTimeout(() => onPointAccount?.(), 1400);
      }
    } catch {
      setError(true);
    } finally {
      setSending(false);
      scrollToBottom();
    }
  };

  return (
    <div className="assistant-chat">
      <div className="assistant-chat-messages" ref={listRef}>
        <div className="assistant-bubble assistant-bubble-assistant">
          <NamedCopy text={t.assistantIntro} name={t.sentinelName} />
        </div>
        {messages.map((message, index) => (
          <div
            key={index}
            className={`assistant-bubble assistant-bubble-${message.role}`}
          >
            {message.content}
          </div>
        ))}
        {sending && (
          <div className="assistant-bubble assistant-bubble-assistant assistant-bubble-pending">
            <span className="assistant-typing" aria-label={t.assistantThinking}>
              <span />
              <span />
              <span />
            </span>
          </div>
        )}
        {error && (
          <div className="assistant-bubble assistant-bubble-assistant assistant-bubble-error">
            {t.assistantError}
          </div>
        )}
      </div>

      <form
        className="assistant-chat-form"
        onSubmit={(event) => {
          event.preventDefault();
          void send();
        }}
      >
        <input
          type="text"
          className="assistant-chat-input"
          value={input}
          maxLength={MAX_INPUT_CHARS}
          placeholder={t.assistantPlaceholder}
          onChange={(event) => setInput(event.target.value)}
          disabled={sending}
        />
        <button type="submit" className="assistant-chat-send" disabled={sending || !input.trim()}>
          {t.assistantSend}
        </button>
      </form>

      <button type="button" className="guide-skip assistant-chat-back" onClick={onBack}>
        {t.assistantBack}
      </button>
    </div>
  );
}
