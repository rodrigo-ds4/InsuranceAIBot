import { useState } from "react";
import io from "socket.io-client";
import ChatView from "./components/ChatView/ChatView";
let endpoint = "http://localhost:5000";
let socket = io.connect(endpoint);

const App = () => {
  const [newQuestion, sendNewQuestion] = useState("");
  const [chatAnswers, saveChatAnswer] = useState([]);
  const [userQuestions, saveUserQuestions] = useState([]);
  const [showOptions, setShowOptions] = useState(true);
  
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

  const selectedOption = (name, code) => {
    console.log("selected option", code);
    setShowOptions(false);
    saveUserQuestions([...userQuestions, name]);
    socket.emit("action", code[0]);
  };

  const insuranceOptions = [
    {
      name: "Accidentes Personales / Reembolso Gastos Médicos ",
      code: ["POL120190177"],
    },
    {
      name: "Seguro Colectivo Complementario de Salud ",
      code: ["POL320130223"],
    },
    {
      name: "Seguro para Prestaciones Médicas Derivadas de Accidente y Enfermedad",
      code: ["POL320150503"],
    },
    {
      name: "Seguro para Prestaciones Médicas Derivadas de Hospitalización Quirúrgica de Emergencia",
      code: ["POL320180100"],
    },
    {
      name: "Seguro para Prestaciones Médicas de Alto Costo",
      code: ["POL320190074", "POL320200214", "POL320210210"],
    },
    {
      name: "Seguro Individual Catastrófico por Evento",
      code: ["POL320200071"],
    },
    {
      name: "Seguro Individual Obligatorio de Salud Asociado a Covid 19",
      code: ["POL320210063"],
    },
  ];

  return (
    <div>
      <ChatView
        options={insuranceOptions}
        questions={userQuestions}
        answers={chatAnswers}
        newQuestion={newQuestion}
        handleChange={(e) => inputQuestion(e)}
        handleClick={() => sendQuestion()}
        handleOption={(name, code) => selectedOption(name, code)}
        disabled={showOptions}
      />
    </div>
  );
};

export default App;
