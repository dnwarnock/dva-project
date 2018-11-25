import Vue from 'vue'
import App from './App.vue'

import Vuex from 'vuex';
import VueMaterial from 'vue-material';
import * as VueGoogleMaps from "vue2-google-maps";


import 'vue-material/dist/vue-material.min.css';

Vue.use(VueGoogleMaps, {
  load: {
    key: "",
    libraries: "places" // necessary for places input
  }
});
Vue.use(VueMaterial);
Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    properties: []
  },
  mutations: {
    setProperties (state, properties) {
      state.properties = properties
    }
  }
})

new Vue({
  el: '#app',
  store,
  components: { App },
  render: h => h(App)
})
