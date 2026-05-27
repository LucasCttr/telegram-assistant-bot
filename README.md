telegram-bot/
│
├── .env                    # API keys y tokens (nunca subir a GitHub)
├── .gitignore              # Excluye .env y venv del repo
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Descripción del proyecto (importante para portafolio)
│
├── main.py                 # Punto de entrada — arranca el bot
│
├── bot/
│   ├── __init__.py
│   ├── handlers.py         # Maneja los mensajes que llegan por Telegram
│   └── keyboards.py        # Botones y menús del bot (opcional)
│
├── agent/
│   ├── __init__.py
│   ├── agent.py            # Lógica del agente LangChain
│   └── memory.py           # Memoria por usuario
│
└── tools/
    ├── __init__.py
    ├── search.py           # Tool de búsqueda web (DuckDuckGo)
    └── pdf.py              # Tool para analizar PDFs



Flujo de datos
Usuario escribe en Telegram
        ↓
    handlers.py          ← recibe el mensaje
        ↓
     agent.py            ← decide qué tool usar
        ↓
  search.py / pdf.py     ← ejecuta la tool
        ↓
    handlers.py          ← manda la respuesta de vuelta
        ↓
Usuario recibe respuesta en Telegram



Los archivos más importantes
main.py — solo arranca el bot, no tiene lógica
handlers.py — es el corazón del bot, conecta Telegram con el agente
agent.py — es donde vive la inteligencia, el LLM y las tools
memory.py — guarda conversación separada por cada usuario (para que no se mezclen los chats)