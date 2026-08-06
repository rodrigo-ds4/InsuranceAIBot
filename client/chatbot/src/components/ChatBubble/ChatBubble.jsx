import styles from "./styles.module.scss";

const ChatBubble = ({ content, role = "bot" }) => {
  const isUser = role === "user";
  return (
    <div className={isUser ? styles.user : styles.bot}>
      <div className={isUser ? styles.userWrap : styles.botWrap}>
        {content ? <p>{content}</p> : null}
      </div>
    </div>
  );
};

export default ChatBubble;