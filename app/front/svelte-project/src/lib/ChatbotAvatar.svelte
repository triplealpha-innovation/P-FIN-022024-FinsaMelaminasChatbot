<script lang="ts">
  export let size: 'large' | 'small' = 'large';
</script>

<div class="avatar {size}">
  <img 
    src="/img/robot (4).png" 
    alt="Robot animated icon"
    class="robot-gif"
  />
</div>

<!-- Attribution comment for the icon -->
<!--
  Robot animated icons created by Freepik - Flaticon
  https://www.flaticon.com/free-animated-icons/robot
-->

<style>
  .avatar {
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    border-radius: 50%;
    box-shadow: 0 4px 20px rgba(206, 14, 45, 0.2);
    transition: transform 0.3s ease;
    overflow: hidden;
  }

  .avatar:hover {
    transform: scale(1.05);
  }

  .large {
    width: 64px;
    height: 64px;
    padding: 0;
  }

  .small {
    width: 20px;
    height: 20px;
    margin-right: 0.25rem;
  }

  .robot-gif {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
</style>