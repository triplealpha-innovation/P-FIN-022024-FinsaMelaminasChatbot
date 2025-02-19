<script lang="ts">
  import { onMount } from 'svelte';
  import ChatMessage from './lib/ChatMessage.svelte';
  import ChatInput from './lib/ChatInput.svelte';
  import LoadingSpinner from './lib/LoadingSpinner.svelte';
  import ChatbotAvatar from './lib/ChatbotAvatar.svelte';
  import SelectionGrid from './lib/SelectionGrid.svelte';
  import { v4 as uuidv4 } from 'uuid';

  interface Message {
    text: string;
    isUser: boolean;
    showOptions?: boolean;
    options?: string[];
    onSelect?: (option: string) => void;
  }

  interface ChatResponse {
    result: {
      query_result: {
        content: string;
      };
    };
  }

  const API_URL = 'https://app-dev-api-chatbot-finsa-b0d0e5gfhugyemfe.westeurope-01.azurewebsites.net';
  let selectedCenter: string | null = null;
  let selectedLine: string | null = null;
  let inputEnabled = false;

  const centers = ['Todos', 'Santiago', 'Fibranor', 'Cella'];
  const productionLines = [
    'Todas',
    'Plastificados',
    'Plastificados I',
    'Plastificados II',
    'Plastificados III',
    'Plastificados IV',
    'Plastificados V',
    'Plastificados VI',
    'Plastificados VII',
    'Plastificados VIII',
    'Plastificados IX',
    'Plastificados X',
    'Plastificados elementos comunes',
    'Plastificados (VII-IX) elementos comunes'
  ];

  let messages: Message[] = [
    {
      text: "¿En qué centro estás?",
      isUser: false,
      showOptions: true,
      options: centers,
      onSelect: handleCenterSelection
    }
  ];
  
  let isLoading = false;
  let errorMessage = '';
  let requestCount = 0;
  let lastRequestTime = 0;
  let uuid_sesion: string;

  async function saveContext(context: string) {
    try {
      const response = await fetch(`${API_URL}/save_context/?context=${encodeURIComponent(context)}&uuid_sesion=${uuid_sesion}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'X-API-KEY': 'QjRfzpjYFAzBQxsJkhnk6j3zgbZlkw7KqYAfKu5aAE6c5BheuWt4XzPcOX6YGLJzeejlAVUld1jwBHEbjBm8Y9g7Oy4E7kuDeVAqdz2JODyNovylpyYtNfC5oEGCg5Jw'
        }
      });

      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error guardando el contexto:', error);
      throw error;
    }
  }

  async function handleCenterSelection(center: string) {
    try {
      selectedCenter = center;
      await saveContext(`Centro seleccionado: ${center}`);
      
      messages = [
        ...messages.slice(0, -1),
        { text: `Centro seleccionado: ${center}`, isUser: false },
        {
          text: "¿Quieres seleccionar alguna línea de producción?",
          isUser: false,
          showOptions: true,
          options: productionLines,
          onSelect: handleLineSelection
        }
      ];
    } catch (error) {
      errorMessage = getErrorMessage(error);
    }
  }

  async function handleLineSelection(line: string) {
    try {
      selectedLine = line;
      await saveContext(`Línea de producción seleccionada: ${line}`);
      
      messages = [
        ...messages.slice(0, -1),
        { text: `Línea seleccionada: ${line}`, isUser: false },
        {
          text: "¡Hola! Estoy aquí para ayudarte, hazme una pregunta",
          isUser: false
        }
      ];
      inputEnabled = true;
    } catch (error) {
      errorMessage = getErrorMessage(error);
    }
  }

  onMount(() => {
    sessionStorage.removeItem('uuid_sesion');
    uuid_sesion = uuidv4();
    sessionStorage.setItem('uuid_sesion', uuid_sesion);
  });

  function getErrorMessage(error: unknown): string {
    if (error instanceof Error) {
      if (error.message.includes('Failed to fetch')) {
        return 'No se pudo conectar con el servidor. Por favor, verifica tu conexión.';
      }
      if (error.message.includes('Error HTTP: 429')) {
        return 'Has excedido el límite de peticiones. Por favor, espera un momento.';
      }
      if (error.message.includes('Error HTTP')) {
        return 'Error de conexión con el servidor. Por favor, inténtalo de nuevo.';
      }
      if (error.message === 'Respuesta inválida del servidor') {
        return 'La respuesta del servidor no tiene el formato esperado.';
      }
      return error.message;
    }
    return 'Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo.';
  }

  async function handleMessage(event: CustomEvent<string>) {
    try {
      if (!event.detail) {
        throw new Error("Por favor, escribe una pregunta.");
      }

      const question = event.detail.trim();
      
      if (!question) {
        throw new Error("Por favor, escribe una pregunta.");
      }

      const currentTime = Date.now();
      if (currentTime - lastRequestTime < 60000) {
        requestCount++;
        if (requestCount > 5) {
          throw new Error("Lo siento, has alcanzado el límite de preguntas por minuto. Por favor, espera un momento y vuelve a intentarlo.");
        }
      } else {
        requestCount = 1;
        lastRequestTime = currentTime;
      }

      messages = [...messages, { text: question, isUser: true }];
      isLoading = true;
      errorMessage = '';

      const response = await fetch(`${API_URL}/process_question/?question=${encodeURIComponent(question)}&uuid_sesion=${uuid_sesion}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'X-API-KEY': 'QjRfzpjYFAzBQxsJkhnk6j3zgbZlkw7KqYAfKu5aAE6c5BheuWt4XzPcOX6YGLJzeejlAVUld1jwBHEbjBm8Y9g7Oy4E7kuDeVAqdz2JODyNovylpyYtNfC5oEGCg5Jw'
        }
      });

      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }
      
      const data = await response.json() as ChatResponse;
      
      if (!data?.result?.query_result?.content) {
        throw new Error('Respuesta inválida del servidor');
      }
      
      const botResponse = data.result.query_result.content.trim();
      if (!botResponse) {
        throw new Error('La respuesta del servidor está vacía');
      }
      
      messages = [...messages, { 
        text: botResponse,
        isUser: false
      }];
    } catch (error) {
      errorMessage = getErrorMessage(error);
      console.error('Error en el chatbot:', error);
    } finally {
      isLoading = false;
    }
  }
</script>

<main class="chat-container">
  <header class="chat-header">
    <div class="header-content">
      <div class="header-left">
        <ChatbotAvatar size="small" />
        <div class="header-info">
          <span class="header-title">Asistente AI</span>
          <span class="header-status">Online</span>
        </div>
      </div>
      <img 
        src="https://static.construible.es/media/2020/09/Logo-Finsa.png" 
        alt="Finsa Logo" 
        class="finsa-logo"
      />
    </div>
  </header>

  <div class="messages-container">
    <div class="messages">
      {#each messages as message}
        <div class="message-wrapper">
          <ChatMessage text={message.text} isUser={message.isUser} />
          {#if message.showOptions && message.options && message.onSelect}
            <SelectionGrid 
              options={message.options}
              onSelect={message.onSelect}
            />
          {/if}
          
        </div>
      {/each}
      
      
      {#if isLoading}
        <div class="loading-wrapper">
          <LoadingSpinner />
        </div>
      {/if}
      
      
      {#if errorMessage}
        <div class="error-message">
          {errorMessage}
        </div>
      {/if}
      
    </div>
  </div>
  
  <footer class="chat-footer">
    <ChatInput on:send={handleMessage} disabled={!inputEnabled} />
  </footer>
</main>

<style>
  .chat-container {
    width: 100%;
    max-width: 96vw;
    height: 90vh;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    background: white;
    border-radius: 28px;
    box-shadow: 
      0 12px 40px rgba(0, 0, 0, 0.1),
      0 0 0 1px rgba(0, 0, 0, 0.05);
    overflow: hidden;
    position: relative;
  }

  .chat-header {
    background: white;
    padding: 1.25rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    position: relative;
    z-index: 10;
  }

  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .header-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .header-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1a1a1a;
    letter-spacing: -0.01em;
  }

  .header-status {
    font-size: 0.75rem;
    color: #22c55e;
    display: flex;
    align-items: center;
    gap: 0.375rem;
  }

  .header-status::before {
    content: '';
    display: inline-block;
    width: 6px;
    height: 6px;
    background: #22c55e;
    border-radius: 50%;
  }

  .finsa-logo {
    height: 24px;
    object-fit: contain;
  }

  .messages-container {
    flex: 1;
    overflow: hidden;
    position: relative;
    background: #fafafa;
  }

  .messages {
    height: 100%;
    overflow-y: auto;
    padding: 1.25rem;
    scroll-behavior: smooth;
  }

  .message-wrapper {
    margin-bottom: 1.25rem;
    animation: slideIn 0.3s ease-out;
  }

  .loading-wrapper {
    padding: 0.5rem 0;
  }

  .messages::-webkit-scrollbar {
    width: 6px;
  }

  .messages::-webkit-scrollbar-track {
    background: transparent;
  }

  .messages::-webkit-scrollbar-thumb {
    background: #e0e0e0;
    border-radius: 3px;
  }

  .error-message {
    text-align: center;
    color: #dc2626;
    padding: 0.75rem;
    margin: 0.75rem 0;
    background-color: #fef2f2;
    border-radius: 16px;
    font-size: 0.875rem;
    border: 1px solid #fee2e2;
    animation: fadeIn 0.3s ease-out;
  }

  .chat-footer {
    background: white;
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    position: relative;
    z-index: 10;
  }

  @keyframes slideIn {
    from { 
      opacity: 0;
      transform: translateY(10px);
    }
    to { 
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @media (max-width: 480px) {
    .chat-container {
      height: 100vh;
      max-width: none;
      border-radius: 0;
      margin: 0;
    }
  }

  @media (min-width: 1024px) {
    .chat-container {
      max-width: 80vw;
    }
  }

  @media (min-width: 1536px) {
    .chat-container {
      max-width: 70vw;
    }
  }
</style>