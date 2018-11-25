<template>
  <div id="app">
    <div class="md-layout">
      <div class="left md-layout-item">
        <google-map />
      </div>
      <div class="right md-layout-item">
        <result-table />
      </div>
    </div>
  </div>
</template>

<script>
import GoogleMap from "./components/GoogleMap";
import ResultTable from "./components/ResultTable";
export default {
  name: 'app',
  components: {
    GoogleMap,
    ResultTable
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  color: #2c3e50;
}

h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

.left {
  width: 50%;
  height: 100%;
  float: left;
  border-collapse: collapse;
  padding:1em;
}

.right{
  width: 50%;
  height: 100%;
  float: right;
  border-collapse: collapse;
  padding:1em;
}

a {
  color: #42b983;
}

</style>
