<template>
  <div><br/>
    <md-table v-model="properties" md-sort="name" md-sort-order="asc" md-card>
      <md-table-toolbar>
        <h2 class="md-title">Results</h2>
        <vue-json-to-csv :json-data="properties" csv-title="search_results.csv">
          <md-button class="md-raised">download</md-button>
        </vue-json-to-csv>
      </md-table-toolbar>
      <md-table-row slot="md-table-row" slot-scope="{ item }">
        <md-table-cell md-label="rank" md-sort-by="_id" md-numeric>{{ item._id }}</md-table-cell>
        <md-table-cell md-label="address" md-sort-by="address">{{ item.address }}</md-table-cell>
        <md-table-cell md-label="2018" md-sort-by="appraised_val" md-numeric>{{ item.appraised_val }}</md-table-cell>
        <md-table-cell md-label="2017" md-sort-by="appraisal_2017" md-numeric>{{ item.appraisal_2017 }}</md-table-cell>
        <md-table-cell md-label="2016" md-sort-by="appraisal_2016" md-numeric>{{ item.appraisal_2016 }}</md-table-cell>
        <md-table-cell md-label="2015" md-sort-by="appraisal_2015" md-numeric>{{ item.appraisal_2016 }}</md-table-cell>
        <md-table-cell md-label="building sqft" md-sort-by="building_sqft" md-numeric>{{ item.building_sqft }}</md-table-cell>
        <md-table-cell md-label="land sqft" md-sort-by="land_sqft" md-numeric>{{ item.land_sqft }}</md-table-cell>
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
