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
    placeholder="Escribe tu pregunta aquí..."
    class="chat-input"
  />
  <button type="submit" class="send-button">Enviar</button>
</form>

<style>
  .input-form {
    display: flex;
    gap: 0.5rem;
    padding: 1rem;
    background: white;
    border-top: 1px solid #eee;
  }

  .chat-input {
    flex: 1;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 0.5rem;
    font-size: 1rem;
  }

  .send-button {
    padding: 0.75rem 1.5rem;
    background-color: #646cff;
    color: white;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .send-button:hover {
    background-color: #535bf2;
  }
</style>