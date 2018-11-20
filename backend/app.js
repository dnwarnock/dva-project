'use strict';
const Hapi = require('hapi');
const Boom = require('boom');
const Joi = require('joi');


const init = async () => {
  const server = Hapi.server({
    port: 3000,
    host: "0.0.0.0",
    routes: {
      cors: true
  }
  });

  const dbOpts = {
    url: 'mongodb://mongo:27017/dvaproject',
    settings: {
        poolSize: 10
    },
    decorate: true
  }

  await server.register({
    plugin: require('hapi-mongodb'),
    options: dbOpts
  });

  server.route({
    method: 'GET',
    path: '/',
    handler: (request, h) => {

        return 'Hello, world!';
    }
  });

  server.route( {
    method: 'GET',
    path: '/property/{address}',
    async handler(request, reply) {

        const db = request.mongo.db;
        const ObjectID = request.mongo.ObjectID;

        try {
            const result = await db.collection('properties').findOne({  address: request.params.address });
            return result;
        }
        catch (err) {
            throw Boom.internal('Internal MongoDB error', err);
        }
    }
  });

  server.route( {
    method: 'GET',
    path: '/properties/find/{address}',
    async handler(request) {

        const db = request.mongo.db;

        try {
            let findResult = await db.collection('properties').find({ address: new RegExp(request.params.address)});
            let result = await findResult.toArray();
            return {items: result};
        }
        catch (err) {
            throw Boom.internal('Internal MongoDB error', err);
        }
    }
  });

  server.route( {
    method: 'GET',
    path: '/properties',
    async handler(request) {

        const db = request.mongo.db;

        try {
            let findResult = await db.collection('properties').find({ "_id": { $in: request.query.ids } });
            let result = await findResult.toArray();
            return result;
        }
        catch (err) {
            throw Boom.internal('Internal MongoDB error', err);
        }
    },
    options: {
      validate: {
        query: {
            ids: Joi.array().items(Joi.number().integer().options({convert: true}))
        }
      }
    }
  });

  await server.start();
  console.log(`Server running at: ${server.info.uri}`);
};

process.on('unhandledRejection', (err) => {

    console.log(err);
    process.exit(1);
});

init();