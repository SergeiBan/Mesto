<script setup>
import { onMounted, ref } from 'vue';
import Map from '../components/Map.vue'

const y = ref(0)
const x = ref(0)
const log = ref('')
const message = ref('')
const nearby = {}

const chatSocket = new WebSocket(`ws://${window.location.host}/ws/chat/${y.value}/`)

chatSocket.onmessage = function(e) {
  const data = JSON.parse(e.data)
  if ('guest' in data.message) {
    nearby[data.message.guest] = {y: data.message.y, x: data.message.x}
    console.log(nearby)
  }
  log.value += (`${data.message}\n`)
}

chatSocket.onclose = function(e) {
  console.error('Chat socket closed unexpectedly')
}

const submitMessage = function() {
  chatSocket.send(JSON.stringify({'message': message.value}))
  message.value = null
}

const sendCoords = (y, x) => {
  console.log(y, x)
  message.value = {travel: {y: y, x: x}}
  submitMessage()
}

</script>

<template>
  <main>
    <input type="number" class="form-control mb-2" v-model="y">
    <input type="number" class="form-control mb-2" v-model="x">
    <textarea class="form-control mb-2" v-model="log"></textarea>
    <input class="form-control mb-2" type="text" v-model="message">
    <input class="form-button btn mb-2 btn-info" type="button" value="Отправить" @click="submitMessage">

    <!-- <div id="map" style="width: 600px; height: 400px"></div> -->
    <Map @travel="sendCoords" />
  </main>
</template>
