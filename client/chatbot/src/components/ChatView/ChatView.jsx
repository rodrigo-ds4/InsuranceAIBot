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
      <div id="chatWindow" ref={chatWindowRef} className={styles.chat_wrap}>
        <ChatBubble
          content={
            "Hola, soy el asistente virtual de Seguros. ¿En qué te puedo ayudar?"
          }
        />
        {questions.map((question, i) => (
          <div key={`answer${i}`}>
            <ChatBubble role="user" content={question} />
            <ChatBubble content={answers[i]} />
          </div>
        ))}
      </div>
      <div>
        <input
          type="text"
          onChange={(e) => handleChange(e)}
          value={newQuestion}
        />
        <input type="button" onClick={handleClick} value="Send" />
      </div>
    </div>
  );
};

export default ChatView;
