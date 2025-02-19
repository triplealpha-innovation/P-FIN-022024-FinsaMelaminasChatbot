<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import * as SpeechSDK from 'microsoft-cognitiveservices-speech-sdk';
  
  const dispatch = createEventDispatcher();
  export let disabled = false;
  
  let message = '';
  let isRecording = false;
  let recognizer: SpeechSDK.SpeechRecognizer;
  let speechConfig: SpeechSDK.SpeechConfig;
  let audioConfig: SpeechSDK.AudioConfig;
  
  const AZURE_KEY = '4vcs1XLAre8wu6iSZ7gykuiGtjbCCs9qsKld6RZFxUhXemOrp34nJQQJ99BBAC5RqLJXJ3w3AAAYACOG3IJw';
  const AZURE_REGION = 'westeurope';
  
  onMount(() => {
    initializeSpeechRecognition();
    return () => {
      if (recognizer) {
        recognizer.close();
      }
    };
  });

  function initializeSpeechRecognition() {
    speechConfig = SpeechSDK.SpeechConfig.fromSubscription(AZURE_KEY, AZURE_REGION);
    speechConfig.speechRecognitionLanguage = 'es-ES';
    audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
    
    recognizer = new SpeechSDK.SpeechRecognizer(speechConfig, audioConfig);
    
    recognizer.recognized = (s, e) => {
      if (e.result.reason === SpeechSDK.ResultReason.RecognizedSpeech) {
        const newText = e.result.text.trim();
        if (newText) {
          message = newText;
          stopRecording();
        }
      }
    };

    recognizer.recognizing = (s, e) => {
      if (e.result.text) {
        message = e.result.text;
      }
    };

    recognizer.sessionStopped = () => {
      stopRecording();
    };
  }
  
  function handleSubmit() {
    if (message.trim() && !disabled) {
      dispatch('send', message);
      message = '';
    }
  }

  function stopRecording() {
    if (isRecording) {
      recognizer.stopContinuousRecognitionAsync(
        () => {
          isRecording = false;
          recognizer.close();
          initializeSpeechRecognition();
        },
        (error) => {
          console.error('Error stopping recognition:', error);
          isRecording = false;
        }
      );
    }
  }
  
  async function toggleRecording() {
    if (disabled) return;
    
    if (isRecording) {
      stopRecording();
    } else {
      isRecording = true;
      try {
        await recognizer.startContinuousRecognitionAsync();
      } catch (error) {
        console.error('Error starting voice recognition:', error);
        isRecording = false;
      }
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="input-form">
  <button 
    type="button" 
    class="voice-button" 
    class:recording={isRecording}
    class:disabled={disabled}
    on:click={toggleRecording}
    {disabled}
    title={disabled ? "Complete las preguntas iniciales" : isRecording ? "Detener grabación" : "Iniciar reconocimiento de voz"}
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
      <line x1="12" y1="19" x2="12" y2="23"/>
      <line x1="8" y1="23" x2="16" y2="23"/>
    </svg>
  </button>
  <input
    type="text"
    bind:value={message}
    placeholder={disabled ? "Complete las preguntas iniciales" : "Escribe tu mensaje..."}
    class="chat-input"
    class:disabled={disabled}
    {disabled}
  />
  <button 
    type="submit" 
    class="send-button" 
    disabled={!message.trim() || disabled}
    class:disabled={disabled}
  >
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

  .chat-input.disabled {
    background: #f3f4f6;
    color: #9ca3af;
    cursor: not-allowed;
  }

  .chat-input::placeholder {
    color: #9ca3af;
  }

  .chat-input:not(.disabled):focus {
    outline: none;
    border-color: #ce0e2d;
    box-shadow: 0 0 0 3px rgba(206, 14, 45, 0.1);
  }

  .voice-button {
    width: 46px;
    height: 46px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f8f9fa;
    color: #6b7280;
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .voice-button:not(.disabled):hover {
    background-color: #f3f4f6;
    color: #374151;
    transform: translateY(-1px);
    box-shadow: 
      0 4px 12px rgba(0, 0, 0, 0.05),
      0 0 0 1px rgba(206, 14, 45, 0.1);
  }

  .voice-button.disabled {
    background-color: #f3f4f6;
    color: #9ca3af;
    cursor: not-allowed;
  }

  .voice-button.recording {
    background-color: #ce0e2d;
    color: white;
    border-color: #ce0e2d;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0% {
      box-shadow: 0 0 0 0 rgba(206, 14, 45, 0.4);
    }
    70% {
      box-shadow: 0 0 0 10px rgba(206, 14, 45, 0);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(206, 14, 45, 0);
    }
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

  .send-button:not(.disabled):hover:not(:disabled) {
    background-color: #b50d27;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(206, 14, 45, 0.2);
  }

  .send-button:not(.disabled):active:not(:disabled) {
    transform: translateY(0);
    box-shadow: none;
  }

  .send-button:disabled, .send-button.disabled {
    background-color: #e5e7eb;
    cursor: not-allowed;
    transform: none;
  }
</style>