<script lang="ts">
  import { onMount } from 'svelte';
  import ChatMessage from './lib/ChatMessage.svelte';
  import ChatInput from './lib/ChatInput.svelte';
  import LoadingSpinner from './lib/LoadingSpinner.svelte';
  import ChatbotAvatar from './lib/ChatbotAvatar.svelte';
  import { v4 as uuidv4 } from 'uuid';

  interface Message {
    text: string;
    isUser: boolean;
  }

  interface ChatResponse {
    result: {
      query_result: {
        content: string;
      };
    };
  }

  const API_URL = 'https://app-dev-api-chatbot-finsa-b0d0e5gfhugyemfe.westeurope-01.azurewebsites.net';
  let showWelcomeIcon = true;

  onMount(() => {
    setTimeout(() => {
      showWelcomeIcon = false;
    }, 3000);
  });

  // Inicializa el historial de mensajes
  let messages: Message[] = [
    {
      text: "¡Hola! Estoy aquí para ayudarte, hazme una pregunta",
      isUser: false
    }
  ];
  
  let isLoading = false;
  let errorMessage = '';
  let requestCount = 0;
  let lastRequestTime = 0;
  let uuid_sesion: string;

  onMount(() => {
    // Siempre que se recargue la pestaña, eliminamos el uuid_sesion anterior y generamos uno nuevo.
    sessionStorage.removeItem('uuid_sesion');
  
    // Generamos un nuevo uuid_sesion
    uuid_sesion = uuidv4();
  
    // Guardamos el nuevo uuid_sesion en sessionStorage
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

      // Solicita una respuesta usando el uuid_sesion
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
      <ChatbotAvatar size="small" />
      <div class="header-info">
        <span class="header-title">Asistente AI</span>
        <span class="header-status">Online</span>
      </div>
      <img 
        src="https://static.construible.es/media/2020/09/Logo-Finsa.png" 
        alt="Finsa Logo" 
        class="finsa-logo"
      />
    </div>
  </header>

  {#if showWelcomeIcon}
    <div class="welcome-icon" class:fade-out={!showWelcomeIcon}>
      <ChatbotAvatar size="large" />
    </div>
  {/if}

  <div class="messages">
    {#each messages as message}
      <ChatMessage text={message.text} isUser={message.isUser} />
    {/each}
    
    {#if isLoading}
      <LoadingSpinner />
    {/if}
    
    {#if errorMessage}
      <div class="error-message">
        {errorMessage}
      </div>
    {/if}
  </div>
  
  <ChatInput on:send={handleMessage} />
</main>

<style>
  .chat-container {
    width: 100%;
    max-width: 420px;
    height: 90vh;
    margin: 2rem auto;
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
  }

  .header-content {
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
    margin-left: auto;
    object-fit: contain;
  }

  .welcome-icon {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) scale(2);
    z-index: 10;
    opacity: 1;
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .welcome-icon.fade-out {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0);
    pointer-events: none;
  }

  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 1.25rem;
    background: #fafafa;
    scroll-behavior: smooth;
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

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>