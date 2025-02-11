<script lang="ts">
  import ChatMessage from './lib/ChatMessage.svelte';
  import ChatInput from './lib/ChatInput.svelte';
  import LoadingSpinner from './lib/LoadingSpinner.svelte';

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

  // URL base del servidor - ajusta esto según tu configuración
  const API_URL = 'http://localhost:8910'; // Ajusta este valor según tu servidor

  let messages: Message[] = [
    {
      text: "¡Hola! Soy tu chatbot. ¿En qué puedo ayudarte hoy?",
      isUser: false
    }
  ];
  
  let isLoading = false;
  let errorMessage = '';
  let requestCount = 0;
  let lastRequestTime = 0;

  function getErrorMessage(error: unknown): string {
    // Log the complete error object for debugging
    console.error('Error details:', {
      name: error instanceof Error ? error.name : 'Unknown',
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : 'No stack trace'
    });

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
      return `Error: ${error.message}`;
    }
    if (error && typeof error === 'object') {
      return `Error: ${JSON.stringify(error)}`;
    }
    return 'Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo.';
  }

  async function handleMessage(event: CustomEvent<string>) {
    try {
      const question = event.detail?.trim();
      
      if (!question) {
        throw new Error("Por favor, escribe una pregunta.");
      }

      const currentTime = Date.now();
      
      // Rate limiting check
      if (currentTime - lastRequestTime < 60000) { // 1 minute
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

      const response = await fetch(`${API_URL}/process_question/?question=${encodeURIComponent(question)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }
      
      const data: ChatResponse = await response.json();
      
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
      setTimeout(() => {
        errorMessage = '';
      }, 5000);
    } finally {
      isLoading = false;
    }
  }
</script>

<main class="chat-container">
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
    max-width: 800px;
    height: 80vh;
    margin: 2rem auto;
    display: flex;
    flex-direction: column;
    background: white;
    border-radius: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
  }

  .error-message {
    text-align: center;
    color: #ff3e00;
    padding: 0.5rem;
    margin: 0.5rem 0;
    background-color: #fff1f0;
    border-radius: 0.5rem;
  }

  :global(body) {
    background-color: #f5f5f5;
  }
</style>