<template>
  <div>
    <div>
      <div class="md-layout">
        <div class="md-layout-item">
          <md-field md-inline>
            <autocomplete
              :source="propertiesEndpoint"
              results-property="items"
              results-display="address"
              results-value="address"
              inputClass="md-input"
              placeholder="3114 CONGRESS AVE 201 TX 78704"
              @selected="handleSearch">
            </autocomplete>
          </md-field>
        </div>
      </div>
    <label>
      <input type="checkbox" name="outline" v-on:change="removeOutline">
        Outline County
      </label>
    </div>
    <br>
    <gmap-map
      :center="center"
      :zoom="zoom"
      style="width:100%;  height: 500px;"
    >
      <gmap-polyline 
        v-bind:path.sync="path" 
        v-bind:options="{ strokeColor:'#FF0000',  strokeOpacity: .5, strokeWeight: 2}">
      </gmap-polyline>
      <gmap-marker
        :key="index"
        v-for="(m, index) in markers"
        :position="m.position"
        :title="m.title"
        :label="m.label"
        @click="center=m.position"
      ></gmap-marker>
    </gmap-map>
  </div>
</template>

<script>
import Autocomplete from 'vuejs-auto-complete'
import axios from 'axios';
import queryString from 'query-string';

export default {
  name: "GoogleMap",
  components: {
    Autocomplete,
  },
  data() {
    return {
      center: {lat: 30.321806, lng: -97.769809},
      zoom: 10,
      outline: false,
      path: [],
      markers: [],
      properties: [],
      address: "",
      currentPlace: null,
      host: 'localhost:3000'
    };
  },

  mounted() {
    this.geolocate();
  },

  methods: {
    propertiesEndpoint (input) {
      return `http://${this.host}/properties/find/${input}`;
    },
    setPlace(place) {
      this.currentPlace = place;
    },
    handleSearch(result) {
      this.markers = [];
      let ids = result.selectedObject.similar.map(sim => sim._id)
      let query = queryString.stringify(
        {ids: ids.concat([result.selectedObject._id])}
      );
      axios.get(`http://${this.host}/properties?${query}`)
        .then(response => {
          console.log(result.selectedObject.similar);
          for(let i = 0; i < response.data.length; i++) {
            let label = result.selectedObject.similar.find(function(rank){
              return response.data[i]._id === rank._id;
            });
            if(!label){
              label = {rank: 0}
            }
            response.data[i]._id = label.rank;
            this.markers.push({
              position: {lat: parseFloat(response.data[i].Lat), lng: parseFloat(response.data[i].Long)},
              title: response.data[i].address,
              label: label.rank.toString()
            });
          }
          this.$store.commit('setProperties', response.data);
        })
    },
    removeOutline() {
      this.outline = !this.outline;
      if(this.outline) {
        this.path = [{lat: 30.3562174, lng: -98.173053}, {lat: 30.2966261, lng: -98.0887546}, {lat: 30.2800233, lng: -98.0663047}, {lat: 30.220914, lng: -97.9838297}, {lat: 30.2204746, lng: -97.9831318}, {lat: 30.1794678, lng: -97.9256814}, {lat: 30.1751607, lng: -97.9197662}, {lat: 30.1729398, lng: -97.9166266}, {lat: 30.1697973, lng: -97.912239}, {lat: 30.1689317, lng: -97.9111523}, {lat: 30.1688489, lng: -97.9109165}, {lat: 30.1683084, lng: -97.9101051}, {lat: 30.1575398, lng: -97.8951738}, {lat: 30.1303962, lng: -97.8574509}, {lat: 30.1274691, lng: -97.8534312}, {lat: 30.1265714, lng: -97.8520661}, {lat: 30.0988365, lng: -97.8133999}, {lat: 30.0986648, lng: -97.8131635}, {lat: 30.0984677, lng: -97.8128838}, {lat: 30.057542, lng: -97.7561037}, {lat: 30.0574693, lng: -97.755876}, {lat: 30.0232901, lng: -97.7087175}, {lat: 30.0287129, lng: -97.7018339}, {lat: 30.0713795, lng: -97.6533397}, {lat: 30.0677607, lng: -97.6490323}, {lat: 30.2101852, lng: -97.4924539}, {lat: 30.4195771, lng: -97.3695642}, {lat: 30.4177179, lng: -97.3735351}, {lat: 30.4191929, lng: -97.3767541}, {lat: 30.4223779, lng: -97.3777381}, {lat: 30.4241139, lng: -97.3794321}, {lat: 30.4243369, lng: -97.3833611}, {lat: 30.4267079, lng: -97.3832161}, {lat: 30.4296639, lng: -97.3847801}, {lat: 30.4306669, lng: -97.3868941}, {lat: 30.4341829, lng: -97.3875881}, {lat: 30.4351249, lng: -97.3925471}, {lat: 30.4376079, lng: -97.3914481}, {lat: 30.4394369, lng: -97.3930511}, {lat: 30.4379989, lng: -97.3954541}, {lat: 30.4407189, lng: -97.4045861}, {lat: 30.4423579, lng: -97.4061811}, {lat: 30.4400339, lng: -97.4076001}, {lat: 30.4383079, lng: -97.4085841}, {lat: 30.4383939, lng: -97.4152291}, {lat: 30.4453019, lng: -97.4227901}, {lat: 30.4522109, lng: -97.4271011}, {lat: 30.4524089, lng: -97.4292831}, {lat: 30.4529089, lng: -97.4332801}, {lat: 30.4594989, lng: -97.4339901}, {lat: 30.4598559, lng: -97.4357981}, {lat: 30.4604219, lng: -97.4371791}, {lat: 30.4600159, lng: -97.4394451}, {lat: 30.4583139, lng: -97.4404291}, {lat: 30.4552649, lng: -97.4417031}, {lat: 30.4560029, lng: -97.4447701}, {lat: 30.4613239, lng: -97.4455101}, {lat: 30.4613829, lng: -97.4531781}, {lat: 30.4583369, lng: -97.4593961}, {lat: 30.4608679, lng: -97.4638741}, {lat: 30.4654249, lng: -97.4668191}, {lat: 30.4660769, lng: -97.4692301}, {lat: 30.4667489, lng: -97.4711451}, {lat: 30.4673479, lng: -97.4760361}, {lat: 30.4691919, lng: -97.4760581}, {lat: 30.4696939, lng: -97.4779661}, {lat: 30.4703499, lng: -97.4800561}, {lat: 30.4695889, lng: -97.4863431}, {lat: 30.4732179, lng: -97.4886621}, {lat: 30.4751409, lng: -97.4937511}, {lat: 30.4776779, lng: -97.5012741}, {lat: 30.4805659, lng: -97.5025481}, {lat: 30.4810839, lng: -97.5048211}, {lat: 30.4850799, lng: -97.5108411}, {lat: 30.4805919, lng: -97.5167161}, {lat: 30.4763079, lng: -97.5221931}, {lat: 30.4737219, lng: -97.5234291}, {lat: 30.4726439, lng: -97.5238721}, {lat: 30.4752349, lng: -97.5271681}, {lat: 30.4786849, lng: -97.5404351}, {lat: 30.4793939, lng: -97.5429991}, {lat: 30.4758929, lng: -97.5457301}, {lat: 30.4754499, lng: -97.5462031}, {lat: 30.4764299, lng: -97.5497431}, {lat: 30.4765159, lng: -97.5499261}, {lat: 30.4801419, lng: -97.5491481}, {lat: 30.4808289, lng: -97.5490721}, {lat: 30.4845649, lng: -97.5509561}, {lat: 30.4862229, lng: -97.5516891}, {lat: 30.4902849, lng: -97.5527871}, {lat: 30.4918129, lng: -97.5632471}, {lat: 30.4923489, lng: -97.5634991}, {lat: 30.4955569, lng: -97.5637511}, {lat: 30.4961849, lng: -97.5689081}, {lat: 30.4993549, lng: -97.5689541}, {lat: 30.5002059, lng: -97.5710371}, {lat: 30.5003259, lng: -97.5723191}, {lat: 30.4999749, lng: -97.5745391}, {lat: 30.5002819, lng: -97.5750651}, {lat: 30.5010939, lng: -97.5768281}, {lat: 30.4998299, lng: -97.5789711}, {lat: 30.5008599, lng: -97.5809321}, {lat: 30.4992119, lng: -97.5850981}, {lat: 30.4971439, lng: -97.5908271}, {lat: 30.5009529, lng: -97.5912091}, {lat: 30.5004189, lng: -97.5931771}, {lat: 30.5014679, lng: -97.5962061}, {lat: 30.4993989, lng: -97.6001351}, {lat: 30.4991999, lng: -97.6006161}, {lat: 30.4985399, lng: -97.6018981}, {lat: 30.4972409, lng: -97.6034011}, {lat: 30.4951359, lng: -97.6060941}, {lat: 30.4903119, lng: -97.6068261}, {lat: 30.4895869, lng: -97.6152721}, {lat: 30.4893579, lng: -97.6174921}, {lat: 30.4903729, lng: -97.6187741}, {lat: 30.4894182, lng: -97.6204367}, {lat: 30.4893829, lng: -97.6204981}, {lat: 30.4855039, lng: -97.6275711}, {lat: 30.4821049, lng: -97.6412811}, {lat: 30.4798389, lng: -97.6431191}, {lat: 30.4781909, lng: -97.6434471}, {lat: 30.4776299, lng: -97.6449731}, {lat: 30.4770849, lng: -97.6461711}, {lat: 30.4749199, lng: -97.6514811}, {lat: 30.4773459, lng: -97.6562501}, {lat: 30.4790839, lng: -97.6591561}, {lat: 30.4802469, lng: -97.6613461}, {lat: 30.4818129, lng: -97.6641001}, {lat: 30.4784249, lng: -97.6699061}, {lat: 30.4798619, lng: -97.6730191}, {lat: 30.4805659, lng: -97.6743311}, {lat: 30.4803242, lng: -97.6762877}, {lat: 30.4799739, lng: -97.6791221}, {lat: 30.4795929, lng: -97.6833641}, {lat: 30.4713659, lng: -97.6856681}, {lat: 30.4631189, lng: -97.6883241}, {lat: 30.4615359, lng: -97.6888881}, {lat: 30.4614079, lng: -97.6962811}, {lat: 30.4585809, lng: -97.7041851}, {lat: 30.4589249, lng: -97.7151181}, {lat: 30.4588219, lng: -97.7154461}, {lat: 30.4499089, lng: -97.7340691}, {lat: 30.4498689, lng: -97.7465131}, {lat: 30.4493329, lng: -97.7467951}, {lat: 30.4478389, lng: -97.7494121}, {lat: 30.4432959, lng: -97.7527771}, {lat: 30.4401239, lng: -97.7546461}, {lat: 30.4333829, lng: -97.7536011}, {lat: 30.4332579, lng: -97.7586671}, {lat: 30.4327879, lng: -97.7656401}, {lat: 30.4327539, lng: -97.7675401}, {lat: 30.4326739, lng: -97.7682261}, {lat: 30.4314529, lng: -97.7715301}, {lat: 30.4298419, lng: -97.7762451}, {lat: 30.4317549, lng: -97.7773131}, {lat: 30.4345619, lng: -97.7779921}, {lat: 30.4382779, lng: -97.7792431}, {lat: 30.4392902, lng: -97.7816942}, {lat: 30.4401227, lng: -97.7834966}, {lat: 30.4407359, lng: -97.7851481}, {lat: 30.4442609, lng: -97.7887031}, {lat: 30.4448389, lng: -97.7943721}, {lat: 30.4472559, lng: -97.7997891}, {lat: 30.4472119, lng: -97.8095161}, {lat: 30.4470059, lng: -97.8118661}, {lat: 30.4476409, lng: -97.8130411}, {lat: 30.4481859, lng: -97.8139261}, {lat: 30.4508409, lng: -97.8175351}, {lat: 30.4551369, lng: -97.8260261}, {lat: 30.4562999, lng: -97.8263621}, {lat: 30.4577309, lng: -97.8269271}, {lat: 30.4630499, lng: -97.8336411}, {lat: 30.4641799, lng: -97.8350061}, {lat: 30.4657589, lng: -97.8367461}, {lat: 30.4671869, lng: -97.8387831}, {lat: 30.4685019, lng: -97.8404921}, {lat: 30.4735599, lng: -97.8465041}, {lat: 30.4758119, lng: -97.8457941}, {lat: 30.4974879, lng: -97.8622581}, {lat: 30.5003139, lng: -97.8590461}, {lat: 30.5030299, lng: -97.8561321}, {lat: 30.5075849, lng: -97.8558501}, {lat: 30.5125159, lng: -97.8597711}, {lat: 30.5154766, lng: -97.8641399}, {lat: 30.5175469, lng: -97.8671951}, {lat: 30.5186899, lng: -97.8682251}, {lat: 30.5204709, lng: -97.8696824}, {lat: 30.5228189, lng: -97.8716041}, {lat: 30.5293794, lng: -97.8705558}, {lat: 30.5297481, lng: -97.8704783}, {lat: 30.5361509, lng: -97.8694381}, {lat: 30.5464359, lng: -97.8678811}, {lat: 30.5485069, lng: -97.8720241}, {lat: 30.5538879, lng: -97.8822171}, {lat: 30.5529779, lng: -97.8832771}, {lat: 30.5566209, lng: -97.8875421}, {lat: 30.5648686, lng: -97.8886365}, {lat: 30.5652499, lng: -97.8886871}, {lat: 30.5664839, lng: -97.8914101}, {lat: 30.5651029, lng: -97.8928451}, {lat: 30.5648759, lng: -97.8963771}, {lat: 30.5689849, lng: -97.9001311}, {lat: 30.5712999, lng: -97.9023891}, {lat: 30.5705659, lng: -97.9042891}, {lat: 30.5704879, lng: -97.9057081}, {lat: 30.5642489, lng: -97.9218291}, {lat: 30.5675499, lng: -97.9268951}, {lat: 30.5740119, lng: -97.9215851}, {lat: 30.5764229, lng: -97.9194871}, {lat: 30.5805069, lng: -97.9151301}, {lat: 30.5854469, lng: -97.9192501}, {lat: 30.5868719, lng: -97.9205011}, {lat: 30.5908709, lng: -97.9219581}, {lat: 30.5964469, lng: -97.9196851}, {lat: 30.6048179, lng: -97.9166791}, {lat: 30.6072309, lng: -97.9255521}, {lat: 30.6100959, lng: -97.9347531}, {lat: 30.6250739, lng: -97.9518351}, {lat: 30.6279179, lng: -97.9570461}, {lat: 30.6235879, lng: -97.9665061}, {lat: 30.6219419, lng: -97.9779281}, {lat: 30.6184709, lng: -97.9817421}, {lat: 30.6095559, lng: -97.9911111}, {lat: 30.6092579, lng: -97.9923171}, {lat: 30.6126969, lng: -97.9979551}, {lat: 30.6179599, lng: -98.0001751}, {lat: 30.6214419, lng: -98.0018461}, {lat: 30.6275499, lng: -98.0063171}, {lat: 30.6173929, lng: -98.0124431}, {lat: 30.6147169, lng: -98.0295481}, {lat: 30.6117469, lng: -98.0363541}, {lat: 30.6119273, lng: -98.0364331}, {lat: 30.6131056, lng: -98.0369425}, {lat: 30.6185354, lng: -98.0394504}, {lat: 30.6181999, lng: -98.0401531}, {lat: 30.6240406, lng: -98.0499428}, {lat: 30.485369, lng: -98.122787}, {lat: 30.4869169, lng: -98.1120831}, {lat: 30.4914969, lng: -98.1073231}, {lat: 30.4949229, lng: -98.1032491}, {lat: 30.496532, lng: -98.095871}, {lat: 30.467363, lng: -98.097176}, {lat: 30.42572, lng: -98.125565}, {lat: 30.3562174, lng: -98.173053}];
      } else {
        this.path = [];
      }
    },
    geolocate: function() {
      navigator.geolocation.getCurrentPosition(position => {
        this.center = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
      });
    }
  }
};
</script>
<style>
.border {
  border-style: solid
}
.md-button {
    margin: 36px;
  }

.md-input {
  margin: 36px;
}

.autocomplete__box {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 0 5px;
}
</style>
