import { useState } from "react";
import io from "socket.io-client";
import ChatView from "./components/ChatView/ChatView";
let endpoint = "http://localhost:5000";
let socket = io.connect(endpoint);


const App = () => {
  const [newQuestion, sendNewQuestion] = useState("");
  const [chatAnswers, saveChatAnswer] = useState([]);
  const [userQuestions, saveUserQuestions] = useState([]);

  socket.on("message", (msg) => {
    saveChatAnswer([...chatAnswers, msg]);
  });

  const inputQuestion = (event) => {
    sendNewQuestion(event.target.value);
  };

  const sendQuestion = () => {
    if (newQuestion !== "") {
      socket.emit("message", newQuestion);
    sendNewQuestion("");
    saveUserQuestions([...userQuestions, newQuestion]);

    }
  };

  return (
    <div>
      <ChatView
        questions={userQuestions}
        answers={chatAnswers}
        newQuestion={newQuestion}
        handleChange={(e) => inputQuestion(e)}
        handleClick={() => sendQuestion()}
      />
    </div>
  );
};

export default App;
