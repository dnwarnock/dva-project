'use strict';
const fs = require('fs');
var MongoClient = require('mongodb').MongoClient;


var properties = JSON.parse(fs.readFileSync('application_data.json', 'utf8'));

async function up() {
    var client = await MongoClient.connect('mongodb://mongo:27017/dvaproject');
    var db = client.db("dvaproject");
    await db.createCollection("properties");
    await db.collection('properties').createIndex({address: "text"});
    await db.collection('properties').insertMany(properties);
}


up().then(function(res){
  console.log(properties.length);
  console.log('done');
  process.exit(0);
})