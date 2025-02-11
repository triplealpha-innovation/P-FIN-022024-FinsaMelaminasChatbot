<script lang="ts">
</script>

<div class="typing-indicator">
  <span></span>
  <span></span>
  <span></span>
</div>

<style>
  .typing-indicator {
    display: flex;
    gap: 0.25rem;
    padding: 0.75rem;
    width: fit-content;
    background: #f0f0f0;
    border-radius: 16px;
    border-bottom-left-radius: 4px;
    margin: 0.75rem 0;
  }

  .typing-indicator span {
    width: 0.5rem;
    height: 0.5rem;
    background: #a0a0a0;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out;
  }

  .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
  .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

  @keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-0.5rem); }
  }
</style>