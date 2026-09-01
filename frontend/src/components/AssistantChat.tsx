import { useEffect, useRef, useState } from "react";
import { sendSentinelaTurn, type AssistantChatMessage } from "../api";
import { matchFaq } from "../assistantFaq";
import { loadAssistantMessages, saveAssistantMessages } from "../guideStorage";
import type { Messages } from "../i18n";
import {
  formatSentinelaSay,
  sentinelaChipLabel,
  SENTINELA_CHIP_ACTIONS,
  type SentinelaAction,
  type SentinelaUiContext,
} from "../sentinela";
import { extractGesture, type SentinelPose } from "../sentinelPose";
import { NamedCopy } from "./SentinelBuddy";

type ChatRow = AssistantChatMessage & { chips?: string[] };

type Props = {
  t: Messages;
  lang: string;
  uiContext: SentinelaUiContext;
  onBack: () => void;
  onBusyChange?: (busy: boolean) => void;
  onPoseChange?: (pose: SentinelPose | null) => void;
  onPointAccount?: () => void;
  onExecuteActions: (actions: SentinelaAction[]) => Promise<{ n: number }>;
};

const MAX_INPUT_CHARS = 500;

/** Sentinela chat: FAQ for facts, then a turn that moves the UI. */
export function AssistantChat({
  t,
  lang,
  uiContext,
  onBack,
  onBusyChange,
  onPoseChange,
  onPointAccount,
  onExecuteActions,
}: Props) {
  const [messages, setMessages] = useState<ChatRow[]>(loadAssistantMessages);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(false);
  const listRef = useRef<HTMLDivElement | null>(null);
  const accountTimer = useRef<number>(0);

  useEffect(() => {
    saveAssistantMessages(messages.map(({ role, content }) => ({ role, content })));
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

  const finishTurn = async (actions: SentinelaAction[], sayId: string, slots: Record<string, string>, chips: string[]) => {
    const pose: SentinelPose =
      actions.some((item) => item.type === "compose_alert" || item.type === "point_to")
        ? "account"
        : actions.some((item) => item.type === "apply_filters" || item.type === "run_search")
          ? "search"
          : "think";
    onPoseChange?.(pose);
    const { n } = await onExecuteActions(actions);
    const resolvedId = sayId === "filtered" && n === 0 ? "empty" : sayId;
    const resolvedChips =
      resolvedId === "empty" ? ["create_alert"] : chips;
    const say = formatSentinelaSay(t, resolvedId as Parameters<typeof formatSentinelaSay>[1], slots, n);
    setMessages((prev) => [...prev, { role: "assistant", content: say, chips: resolvedChips }]);
    if (pose === "account") {
      window.clearTimeout(accountTimer.current);
      accountTimer.current = window.setTimeout(() => onPointAccount?.(), 1400);
    }
  };

  const send = async (raw?: string) => {
    const text = (raw ?? input).trim();
    if (!text || sending) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setError(false);
    setSending(true);
    scrollToBottom();

    const cannedReply = matchFaq(text, lang, { hasHistory: messages.length > 0 });
    const looksLikeSearch = /\d|[àáé]|mapa|carte|karte|map|avis|alert|primero|premier|first|ginebra|geneve|zurich|piso|logement|wohnung|empleo|job|travail/i.test(
      text,
    );
    if (cannedReply && !looksLikeSearch) {
      const parsed = extractGesture(cannedReply);
      onPoseChange?.(parsed.pose);
      setMessages((prev) => [...prev, { role: "assistant", content: parsed.text }]);
      if (parsed.pose === "account") {
        window.clearTimeout(accountTimer.current);
        accountTimer.current = window.setTimeout(() => onPointAccount?.(), 1400);
      }
      setSending(false);
      scrollToBottom();
      return;
    }

    try {
      const turn = await sendSentinelaTurn({
        message: text,
        locale: lang,
        ui_context: uiContext,
      });
      await finishTurn(turn.actions, turn.say_id, turn.slots, turn.chips);
    } catch {
      setError(true);
    } finally {
      setSending(false);
      scrollToBottom();
    }
  };

  const onChip = async (id: string) => {
    const label = sentinelaChipLabel(t, id);
    const actions = SENTINELA_CHIP_ACTIONS[id];
    if (!actions) {
      void send(label);
      return;
    }
    setMessages((prev) => [...prev, { role: "user", content: label }]);
    setSending(true);
    try {
      const sayId =
        id === "create_alert" ? "alert" : id === "on_map" ? "map" : id === "see_first" ? "open_first" : "out_of_scope";
      await finishTurn(actions, sayId, {}, []);
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
          <div key={index}>
            <div className={`assistant-bubble assistant-bubble-${message.role}`}>{message.content}</div>
            {message.role === "assistant" && message.chips?.length ? (
              <div className="assistant-turn-chips">
                {message.chips.map((chip) => (
                  <button
                    key={chip}
                    type="button"
                    className="chip active"
                    disabled={sending}
                    onClick={() => void onChip(chip)}
                  >
                    {sentinelaChipLabel(t, chip)}
                  </button>
                ))}
              </div>
            ) : null}
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
