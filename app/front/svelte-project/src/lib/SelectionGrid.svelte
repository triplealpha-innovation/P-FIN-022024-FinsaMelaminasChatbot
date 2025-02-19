<script lang="ts">
  export let options: string[];
  export let onSelect: (option: string) => void;
  export let itemsPerPage = 4;

  let currentPage = 0;
  
  $: totalPages = Math.ceil(options.length / itemsPerPage);
  $: visibleOptions = options.slice(
    currentPage * itemsPerPage,
    (currentPage + 1) * itemsPerPage
  );

  function nextPage() {
    if (currentPage < totalPages - 1) {
      currentPage++;
    }
  }

  function previousPage() {
    if (currentPage > 0) {
      currentPage--;
    }
  }
</script>

<div class="selection-container">
  <div class="grid">
    {#each visibleOptions as option}
      <button
        class="option-button"
        on:click={() => onSelect(option)}
      >
        <div class="option-content">
          <span class="option-icon">
            {#if option.toLowerCase().includes('plastificados')}
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                <line x1="12" y1="22.08" x2="12" y2="12"/>
              </svg>
            {:else if option === 'Todos' || option === 'Todas'}
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 11 12 14 22 4"/>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
              </svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
            {/if}
            
          </span>
          <span class="option-text">{option}</span>
        </div>
      </button>
    {/each}
    
  </div>
  
  {#if totalPages > 1}
    <div class="pagination">
      <button
        class="pagination-button"
        on:click={previousPage}
        disabled={currentPage === 0}
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>
      <span class="page-info">
        <span class="current-page">{currentPage + 1}</span>
        <span class="total-pages">/ {totalPages}</span>
      </span>
      <button
        class="pagination-button"
        on:click={nextPage}
        disabled={currentPage === totalPages - 1}
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      </button>
    </div>
  {/if}
  
</div>

<style>
  .selection-container {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 0.75rem 2.125rem;
    margin-top: 0.5rem;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  .option-button {
    min-height: 4rem;
    width: 100%;
    padding: 0.75rem;
    background: white;
    border: 1px solid rgba(206, 14, 45, 0.12);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
  }

  .option-content {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    position: relative;
    z-index: 1;
  }

  .option-button::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(206, 14, 45, 0.08) 0%, rgba(206, 14, 45, 0) 100%);
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .option-button:hover {
    transform: translateY(-1px);
    border-color: rgba(206, 14, 45, 0.3);
    box-shadow: 
      0 4px 12px rgba(206, 14, 45, 0.08),
      0 2px 4px rgba(206, 14, 45, 0.04);
  }

  .option-button:hover::before {
    opacity: 1;
  }

  .option-icon {
    color: #ce0e2d;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s ease;
  }

  .option-button:hover .option-icon {
    transform: scale(1.1);
  }

  .option-text {
    font-size: 0.75rem;
    font-weight: 500;
    color: #374151;
    transition: color 0.2s ease;
    text-align: center;
    line-height: 1.2;
    width: 100%;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    word-break: break-word;
  }

  .option-button:hover .option-text {
    color: #ce0e2d;
  }

  .pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    margin-top: 0.5rem;
  }

  .pagination-button {
    width: 2.25rem;
    height: 2.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    border: 1px solid rgba(206, 14, 45, 0.12);
    border-radius: 8px;
    color: #374151;
    cursor: pointer;
    transition: all 0.2s ease;
    padding: 0;
  }

  .pagination-button:hover:not(:disabled) {
    background: #ce0e2d;
    color: white;
    transform: translateY(-1px);
    box-shadow: 
      0 4px 12px rgba(206, 14, 45, 0.15),
      0 2px 4px rgba(206, 14, 45, 0.1);
  }

  .pagination-button:disabled {
    background: #f3f4f6;
    color: #9ca3af;
    cursor: not-allowed;
    border-color: transparent;
  }

  .page-info {
    display: flex;
    align-items: baseline;
    gap: 0.25rem;
    font-size: 0.875rem;
  }

  .current-page {
    font-weight: 600;
    color: #ce0e2d;
  }

  .total-pages {
    color: #6b7280;
  }
</style>