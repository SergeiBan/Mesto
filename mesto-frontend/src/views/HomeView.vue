<script setup>
import { onMounted, ref } from 'vue';
import Map from '../components/Map.vue'

const y = ref(0)
const x = ref(0)
const log = ref('')
const message = ref('')
const nearby = ref({})

const chatSocket = new WebSocket(`ws://${window.location.host}/ws/chat/`)

chatSocket.onmessage = function(e) {
  const data = JSON.parse(e.data)
  if ('gone' in data.message) {
    const gone_guest = data.message.gone
    delete nearby.value[`${gone_guest}`]
  } else if ('new_message' in data.message) {
      log.value += (`${Object.values(data.message)}\n`)
  } else if ('around_me' in data.message) {

    data.message.around_me.forEach(element => {
      nearby.value[element[0]] = {y: element[1][0], x: element[1][1]}
    });
  }
}

chatSocket.onclose = function(e) {
  console.error('Chat socket closed unexpectedly')
}

const submitMessage = function() {
  chatSocket.send(JSON.stringify({'message': message.value}))
  message.value = null
}

const sendCoords = (y, x) => {
  message.value = {travel: {y: y, x: x}}
  submitMessage()
}

</script>

<template>
  <main>
    <textarea class="form-control mb-2" v-model="log"></textarea>
    <input class="form-control mb-2" type="text" v-model="message">
    <input class="form-button btn mb-2 btn-info" type="button" value="Отправить" @click="submitMessage">

    <Map @travel="sendCoords" :nearby="nearby" />
  </main>
</template>
