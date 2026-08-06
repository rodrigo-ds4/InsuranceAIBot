import { useEffect, useRef } from "react";
import ChatBubble from "../ChatBubble/ChatBubble";
import styles from "./styles.module.scss";

const ChatView = ({
  options,
  messages,
  draft,
  choosingPolicy,
  typing,
  onDraftChange,
  onSend,
  onSelectPolicy,
  onRestart,
}) => {
  const windowRef = useRef(null);

  useEffect(() => {
    const el = windowRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, typing]);

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className={styles.window}>
      <header className={styles.header}>
        <div className={styles.brand}>
          <span className={styles.avatar}>N</span>
          <div>
            <h1>Nicolle</h1>
            <p>Asistente de seguros</p>
          </div>
        </div>
        {!choosingPolicy && (
          <button className={styles.restart} onClick={onRestart} title="Reiniciar">
            Reiniciar
          </button>
        )}
      </header>

      <main className={styles.thread} ref={windowRef}>
        {messages.map((m) => (
          <ChatBubble key={m.id} role={m.role} content={m.content} />
        ))}

        {choosingPolicy && !typing && (
          <div className={styles.chips}>
            <p className={styles.hint}>Pólizas disponibles</p>
            {options.map((opt) => (
              <button
                key={opt.code}
                className={styles.chip}
                onClick={() => onSelectPolicy(opt.code)}
              >
                {opt.name}
              </button>
            ))}
          </div>
        )}

        {typing && <div className={styles.typing}><span /><span /><span /></div>}
      </main>

      <footer className={styles.composer}>
        <input
          type="text"
          value={draft}
          placeholder="Hacé una pregunta sobre la póliza…"
          disabled={choosingPolicy}
          onChange={(e) => onDraftChange(e.target.value)}
          onKeyDown={handleKey}
        />
        <button disabled={choosingPolicy || !draft.trim()} onClick={onSend}>
          Enviar
        </button>
      </footer>
    </div>
  );
};

export default ChatView;