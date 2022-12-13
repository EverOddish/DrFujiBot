const AWS = require('aws-sdk');

exports.handler = event => {

    let isServiceRunning = function () {
        return new Promise(
            (resolve, reject) => {
                    var ecs = new AWS.ECS();
                    var params = {
                        cluster: "DrFujiBotCluster"
                    };

                    console.warn("Calling listServices()");
                   
                    ecs.listServices(params, function(err, data) {
                       if (err) {
                           console.warn(err, err.stack); // an error occurred
                           reject(err);
                       }
                       else {
                           console.warn("Service count: " + data["serviceArns"].length);
                           console.warn(data);           // successful response
                           resolve(data);
                       }
                    });
            }
        );
    };

    let startIRC = function (data) {
        return new Promise(
            (resolve, reject) => {
                    var ecs = new AWS.ECS();
                    var params = {
                     desiredCount: 1,
                     serviceName: "DrFujiBot-IRC-Service",
                     cluster: "DrFujiBotCluster",
                     taskDefinition: "DrFujiBotWithLogs",
                     launchType: "FARGATE",
                     deploymentController: {
                         type: "ECS"
                     },
                     networkConfiguration: {
                        awsvpcConfiguration: {
                            subnets: ["subnet-0f67ebc4b023e53a7",
                                      "subnet-0f25125597dca55d0",
                                      "subnet-015c333d5f2b0db81"],
                            assignPublicIp: "ENABLED"
                        }
                     }
                    };

                    if (data["serviceArns"].length == 0) {
                        console.warn("Calling createService()");
                    
                        ecs.createService(params, function(err, data) {
                        if (err) {
                            console.warn(err, err.stack); // an error occurred
                            reject(err);
                        }
                        else {
                            console.warn("Successfully created DrFujiBot IRC Service");
                            console.warn(data);           // successful response
                            resolve(data);
                        }
                        });
                    }
                    else {
                        console.warn("Serice already running");
                    }
            }
        );
    };

    let stopIRC = function () {
        return new Promise(
            (resolve, reject) => {
                    var ecs = new AWS.ECS();
                    var params = {
                     service: "DrFujiBot-IRC-Service",
                     cluster: "DrFujiBotCluster",
                     force: true
                    };

                    console.warn("Calling deleteService()");
                   
                    ecs.deleteService(params, function(err, data) {
                       if (err) {
                           console.warn(err, err.stack); // an error occurred
                           reject(err);
                       }
                       else {
                           console.warn("Successfully deleted DrFujiBot IRC Service");
                           console.warn(data);           // successful response
                           resolve(data);
                       }
                    });
            }
        );
    };

   if (event["type"] == "start") {
       isServiceRunning()
       .then((data) => startIRC(data)
            .then(res => ({ statusCode: 200 }))
            .catch(err => {
                console.warn(err);
                return { statusCode: 500 };
            })
        );
   }
   else if (event["type"] == "stop") {
       stopIRC()
       .then(res => ({ statusCode: 200 }))
       .catch(err => {
           console.warn(err);
           return { statusCode: 500 };
       });
   }
};

