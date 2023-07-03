import LoadingChat from "../LoadingChat/LoadingChat";
import styles from "./styles.module.scss";

const ChatBubble = ({ content , role = "chatbot" }) => {
  return (
    <div className={role === "chatbot" ? styles.bubble_chatbot : styles.bubble_user}>
      <div
        className={
          role === "chatbot"
            ? styles.bubble_chatbot_wrap
            : styles.bubble_user_wrap
        }
      >
        {content ? <p>{content}</p> : <LoadingChat />}
      </div>
    </div>
  );
};

export default ChatBubble;
