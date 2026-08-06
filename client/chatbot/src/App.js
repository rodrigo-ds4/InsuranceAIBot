import { useCallback, useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";
import ChatView from "./components/ChatView/ChatView";

const ENDPOINT = "http://127.0.0.1:5000";

const INSURANCE_OPTIONS = [
  { name: "Accidentes Personales / Reembolso Gastos Médicos", code: "POL120190177" },
  { name: "Seguro Colectivo Complementario de Salud", code: "POL320130223" },
  { name: "Prestaciones por Accidente y Enfermedad", code: "POL320150503" },
  { name: "Hospitalización Quirúrgica de Emergencia", code: "POL320180100" },
  { name: "Prestaciones Médicas de Alto Costo", code: "POL320190074" },
  { name: "Seguro Catastrófico por Evento Individual", code: "POL320200071" },
  { name: "Seguro Obligatorio Covid-19", code: "POL320210063" },
];

let socket = null;

const App = () => {
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [choosingPolicy, setChoosingPolicy] = useState(true);
  const [typing, setTyping] = useState(false);
  const socketRef = useRef(null);

  const addMessage = useCallback((role, content) => {
    setMessages((prev) => [...prev, { id: crypto.randomUUID(), role, content }]);
  }, []);

  useEffect(() => {
    if (!socket) {
      socket = io(ENDPOINT);
      socketRef.current = socket;
      socket.on("connect", () => {
        addMessage(
          "bot",
          "¡Hola! Soy Nicolle, tu asistente de seguros. Elegí una póliza para empezar:"
        );
      });
      socket.on("message", (msg) => {
        setTyping(false);
        addMessage("bot", msg);
      });
      socket.on("disconnect", () => {
        addMessage("bot", "Se perdió la conexión con el servidor.");
      });
    } else {
      socketRef.current = socket;
    }
    return () => {
      // socket lives for the app lifetime; no-op cleanup keeps StrictMode safe.
    };
  }, [addMessage]);

  const selectPolicy = (code) => {
    setChoosingPolicy(false);
    addMessage("user", `Póliza ${code.slice(3)}`);
    socket.emit("action", code);
  };

  const sendQuestion = () => {
    const text = draft.trim();
    if (!text) return;
    addMessage("user", text);
    setDraft("");
    setTyping(true);
    socket.emit("message", text);
  };

  const restart = () => {
    setMessages([]);
    setChoosingPolicy(true);
    setTyping(false);
    addMessage(
      "bot",
      "Elegí una póliza para empezar de nuevo:"
    );
  };

  return (
    <ChatView
      options={INSURANCE_OPTIONS}
      messages={messages}
      draft={draft}
      choosingPolicy={choosingPolicy}
      typing={typing}
      onDraftChange={setDraft}
      onSend={sendQuestion}
      onSelectPolicy={selectPolicy}
      onRestart={restart}
    />
  );
};

export default App;
