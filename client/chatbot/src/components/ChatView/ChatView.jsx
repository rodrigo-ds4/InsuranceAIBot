import { useRef, useEffect, useLayoutEffect } from "react";
import ChatBubble from "../ChatBubble/ChatBubble";
import styles from "./styles.module.scss";

const ChatView = ({
  options,
  questions,
  answers,
  newQuestion,
  handleChange,
  handleClick,
  handleOption,
  disabled,
}) => {
  const chatWindowRef = useRef(null);

  const scrollToBottom = () => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  };

  useLayoutEffect(() => {
    scrollToBottom();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [questions, answers]);

  return (
    <div className={styles.chat}>
      <div className={styles.chat_wrap}>
        <div className={styles.chat_actions}>
          <h1>Chatbot</h1>
        </div>
        <div className={styles.chat_window} ref={chatWindowRef}>
          <ChatBubble
            content={
              "Hola! Soy Nicolle, la asistente virtual de Seguros. ¿En qué te puedo ayudar?"
            }
          />
          {disabled && (
            <div className={styles.chat_options}>
              {options.map((option, i) => (
                <button
                  className={styles.chat_options_button}
                  key={`option${i}`}
                  onClick={() => handleOption(option.name, option.code)}
                >
                  {option.name}
                </button>
              ))}
            </div>
          )}
          {questions.map((question, i) => (
            <div key={`answer${i}`}>
              <ChatBubble role="user" content={question} />
              <ChatBubble content={answers[i]} />
            </div>
          ))}
        </div>
        <div className={styles.chat_field}>
          <input
            type="text"
            onChange={(e) => handleChange(e)}
            value={newQuestion}
            disabled={disabled ? "disabled" : ""}
          />
          <input
            type="button"
            onClick={handleClick}
            value="⌲"
            disabled={disabled ? "disabled" : ""}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatView;
