<script lang="ts">
  export let message: string;
  export let isUser: boolean;
</script>

<div class="message {isUser ? 'user' : 'bot'}">
  <div class="bubble">
    {message}
  </div>
</div>

<style>
  .message {
    display: flex;
    margin: 1rem 0;
  }

  .user {
    justify-content: flex-end;
  }

  .bot {
    justify-content: flex-start;
  }

  .bubble {
    max-width: 80%;
    padding: 1rem;
    border-radius: 1rem;
    word-wrap: break-word;
  }

  .user .bubble {
    background-color: #646cff;
    color: white;
    border-bottom-right-radius: 0.25rem;
  }

  .bot .bubble {
    background-color: #f1f1f1;
    color: #213547;
    border-bottom-left-radius: 0.25rem;
  }
</style>