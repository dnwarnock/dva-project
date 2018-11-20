'use strict';
var MongoClient = require('mongodb').MongoClient;


var properties = [
  {
    _id: 1,
    address: "10607 PLUCHEA CV AUSTIN 78733",
    sqft: 3500,
    appraisal: 732000,
    similar: [5, 4],
    coordinates: {lat: 30.310850, lng: -97.898780}
  },
  {
    _id: 2,
    address: "7410 SHADYWOOD DR AUSTIN 78745",
    sqft: 2304,
    appraisal: 450333,
    similar: [6, 5],
    coordinates: {lat: 30.186410, lng: -97.788070}
  },
  {
    _id: 3,
    address: "7301 LUNAR DR AUSTIN 78745",
    sqft: 893,
    appraisal: 35000,
    similar: [2, 5],
    coordinates: {lat: 30.188320, lng: -97.786380}
  },
  {
    _id: 4,
    address: "2906 ZEKE BND AUSTIN 78745",
    sqft: 1100,
    appraisal: 2500,
    similar: [5],
    coordinates: {lat: 30.191330, lng: -97.831010}
  },
  {
    _id: 5,
    address: "8634 PINEY CREEK BND AUSTIN 78745",
    sqft: 3500,
    appraisal: 620000,
    similar: [1, 6],
    coordinates: {lat: 30.194710, lng: -97.834770}
  },
  {
    _id: 6,
    address: "8805 PEPPERGRASS CV AUSTIN 78745",
    sqft: 2400,
    appraisal: 550000,
    similar: [5, 6],
    coordinates: {lat: 30.192920, lng: -97.836460}
  },

]

async function up() {
    var client = await MongoClient.connect('mongodb://mongo:27017');
    var db = client.db("dvaproject");
    await db.collection("properties").drop()
    await db.createCollection("properties");
    await db.collection('properties').createIndex({address: "text"});
    await db.collection('properties').insertMany(properties);
}


up().then(function(res){
  console.log('done');
  process.exit(0);
})