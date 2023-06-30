import { useRef, useEffect, useLayoutEffect } from "react";
import ChatBubble from "../ChatBubble/ChatBubble";
import styles from "./styles.module.scss";

const ChatView = ({
  questions,
  answers,
  newQuestion,
  handleChange,
  handleClick,
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
        <div className={styles.chat_window} ref={chatWindowRef}>
          <ChatBubble
            content={
              "Hola! Soy Nicolle, la asistente virtual de Seguros. ¿En qué te puedo ayudar?"
            }
          />
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
          />
          <input type="button" onClick={handleClick} value="⌲" />
        </div>
      </div>
    </div>
  );
};

export default ChatView;
