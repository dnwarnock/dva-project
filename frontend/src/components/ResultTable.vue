<template>
  <div><br/>
    <md-table v-model="properties" md-sort="name" md-sort-order="asc" md-card>
      <md-table-toolbar>
        <h1 class="md-title">Results</h1>
        <vue-json-to-csv 
        :json-data="properties"
        csv-title="search_results.csv">
          <md-button class="md-raised">download</md-button>
        </vue-json-to-csv>
      </md-table-toolbar>
      <md-table-row slot="md-table-row" slot-scope="{ item }">
        <md-table-cell md-label="id" md-sort-by="id">{{ item._id }}</md-table-cell>
        <md-table-cell md-label="address" md-sort-by="address">{{ item.address }}</md-table-cell>
        <md-table-cell md-label="sqft" md-sort-by="sqft" md-numeric>{{ item.sqft }}</md-table-cell>
        <md-table-cell md-label="appraisal" md-sort-by="appraisal" md-numeric>{{ item.appraisal }}</md-table-cell>
      </md-table-row>
    </md-table>
  </div>
</template>

<script>
import VueJsonToCsv from 'vue-json-to-csv';

export default {
  name: 'ResultTable',
  components: {
    VueJsonToCsv,
  },
  data() {
    return {
    }
  },
  computed: {
    properties () {
      return this.$store.state.properties
    }
  }
}
</script>
