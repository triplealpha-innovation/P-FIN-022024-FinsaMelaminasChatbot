<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  let message = '';
  
  function handleSubmit() {
    if (message.trim()) {
      dispatch('send', message);
      message = '';
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="input-form">
  <input
    type="text"
    bind:value={message}
    placeholder="Escribe una pregunta..."
    class="chat-input"
  />
  <button type="submit" class="send-button" disabled={!message.trim()}>
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
    </svg>
  </button>
</form>

<style>
  .input-form {
    display: flex;
    gap: 0.75rem;
    padding: 1.25rem;
    background: white;
    border-top: 1px solid rgba(0, 0, 0, 0.06);
  }

  .chat-input {
    flex: 1;
    padding: 0.875rem 1.25rem;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 16px;
    font-size: 0.9375rem;
    background: white;
    color: #1a1a1a;
    transition: all 0.2s ease;
  }

  .chat-input::placeholder {
    color: #9ca3af;
  }

  .chat-input:focus {
    outline: none;
    border-color: #ce0e2d;
    box-shadow: 0 0 0 3px rgba(206, 14, 45, 0.1);
  }

  .send-button {
    width: 46px;
    height: 46px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #ce0e2d;
    color: white;
    border: none;
    border-radius: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .send-button:hover:not(:disabled) {
    background-color: #b50d27;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(206, 14, 45, 0.2);
  }

  .send-button:active:not(:disabled) {
    transform: translateY(0);
    box-shadow: none;
  }

  .send-button:disabled {
    background-color: #e5e7eb;
    cursor: not-allowed;
    transform: none;
  }
</style>