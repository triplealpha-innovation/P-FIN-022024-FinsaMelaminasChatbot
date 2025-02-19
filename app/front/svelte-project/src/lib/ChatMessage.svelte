<script lang="ts">
  import ChatbotAvatar from './ChatbotAvatar.svelte';
  export let text: string;
  export let isUser: boolean;

  function formatText(text: string): string {
    // Decodificar el texto primero para manejar caracteres escapados
    const decodedText = text.replace(/\\n/g, '\n');
    
    // Reemplazar los saltos de línea con <br>
    const formattedText = decodedText
      .split('\n')
      .map(line => line.trim())
      .join('<br>');

    // Reemplazar el texto en negrita
    return formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  }
</script>

<div class="message {isUser ? 'user' : 'bot'}">
  {#if !isUser}
    <ChatbotAvatar size="small" />
  {/if}
  <div class="bubble">
    {@html formatText(text)}
  </div>
</div>

<style>
  .message {
    display: flex;
    align-items: flex-start;
    margin: 1rem 0;
    gap: 0.75rem;
    animation: slideIn 0.3s ease-out;
  }

  .user {
    justify-content: flex-end;
  }

  .bot {
    justify-content: flex-start;
  }

  .bubble {
    max-width: 75%;
    padding: 0.875rem 1.125rem;
    border-radius: 18px;
    word-wrap: break-word;
    font-size: 0.8375rem;
    line-height: 1.5;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }

  .user .bubble {
    background-color: #ce0e2d;
    color: white;
    border-bottom-right-radius: 4px;
  }

  .bot .bubble {
    background-color: white;
    color: #1a1a1a;
    border-bottom-left-radius: 4px;
  }

  .bubble :global(strong) {
    font-weight: 600;
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
</style>