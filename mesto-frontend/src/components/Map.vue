<script setup>

import { onMounted, ref, watch } from 'vue'

const emit = defineEmits(['travel'])
const props = defineProps({
  nearby: Object
})
let prev_nearby = {}

const y = ref(0)
const x = ref(0)
let m = ref(null)
let m_html = ref(null)
let theMap = null

const mHTML = ref({})
const markers = ref({})


const copy_nearby = () => {
  prev_nearby = {}
  for (const [k, v] of Object.entries(props.nearby)) {
    prev_nearby[k] = v
  }
}

const placeMarker = (map, y, x, guest) => {
    const content = document.createElement('button');
        content.innerHTML = 'я'
        const marker = new ymaps3.YMapMarker({
                coordinates: [y, x],
                draggable: false
                }, content)
        theMap.addChild(marker)

        markers.value[guest] = marker
        mHTML.value[guest] = content
}

onMounted(() => {
  ymaps3.ready.then(init);
  function init() {

    navigator.geolocation.getCurrentPosition(success)
    function success(position) {
      y.value = position.coords.latitude
      x.value = position.coords.longitude
    }

    const map = new ymaps3.YMap(document.getElementById('map'), {
      location: {
        // center: [37.64, 55.76],
        center: [y.values, x.value],
        zoom: 7
      },
    })


    const layer1 = new ymaps3.YMapDefaultSchemeLayer({zIndex: -1});
    map.addChild(layer1);
    const layer2 = new ymaps3.YMapDefaultFeaturesLayer({zIndex: 1800})
    map.addChild(layer2)


    const mouseClickCallback = (obj, event) => {
        y.value = event.coordinates[0]
        x.value = event.coordinates[1]
        emit('travel', y.value, x.value)
    }
    theMap = map

    const mapListener = new ymaps3.YMapListener({
        layer: 'any',
        onClick: mouseClickCallback,
    });
    map.addChild(mapListener);
    
  }

})

watch(props.nearby, (new_nearby) => {
  for (const [k, v] of Object.entries(props.nearby)) {
    if (!(k in prev_nearby)) {
      placeMarker(theMap, v.y, v.x, k)
    } else if (v.y != prev_nearby[k].y || v.x != prev_nearby[k].x) {
        theMap.removeChild(markers.value[k])
        mHTML.value[k].remove()
        placeMarker(theMap, v.y, v.x, k)
    }
    
  }
  for (const [k, v] of Object.entries(prev_nearby)) {
    if (!(k in props.nearby)) {
      theMap.removeChild(markers.value[k])
      mHTML.value[k].remove()
    }
  }
  copy_nearby()

})
</script>

<template>
    <div id="map" style="width: 600px; height: 400px"></div>
</template>