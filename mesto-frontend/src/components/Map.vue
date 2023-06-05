<script setup>

import { onMounted, ref } from 'vue'

const emit = defineEmits(['travel'])

const y = ref(0)
const x = ref(0)
let m = ref(null)
let m_html = ref(null)


const placeMarker = (map) => {
    const content = document.createElement('button');
        content.innerHTML = 'я'
        m_html.value = content
        const marker = new ymaps3.YMapMarker({
                coordinates: [y.value, x.value],
                draggable: false
                }, content)
        m.value = marker
        map.addChild(marker)
}

onMounted(() => {
  ymaps3.ready.then(init);
  function init() {

    const map = new ymaps3.YMap(document.getElementById('map'), {
      location: {
        center: [37.64, 55.76],
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
        console.log(obj, y.value, x.value)
        
        map.removeChild(m.value)
        m_html.value.remove()

        placeMarker(map)
        emit('travel', y.value, x.value)
    }

    placeMarker(map)

    const mapListener = new ymaps3.YMapListener({
        layer: 'any',
        onClick: mouseClickCallback,
    });
    map.addChild(mapListener);
    
  }

})
</script>

<template>
    <div id="map" style="width: 600px; height: 400px"></div>
</template>