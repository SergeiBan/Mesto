<script setup>
import { RouterLink, RouterView } from 'vue-router'

</script>

<template>
  <div class="row">

  <div class="col-12">
  <header>
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">About</RouterLink>
      </nav>
  </header>
  </div>

  <div class="col-12">
    <RouterView />
  </div>

  </div>
</template>
