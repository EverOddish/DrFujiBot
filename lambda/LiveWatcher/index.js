const request = require('request-promise');

//export const handler = async(event) => {

exports.handler = async event => {
  const getAppToken = () => {
    const options = {
      url: `https://id.twitch.tv/oauth2/token?client_id=${process.env.client_id}&client_secret=${process.env.client_secret}&grant_type=client_credentials`,
      method: 'POST',
      json: true,
    };

    return request(options);
  };

  // The single webhook we're subscribing to in this tutorial
  const webhook = {
    channel: '111971097',
    type: 'stream.online',
  };

  // Twitch request to return current subscriptions associated with our app token
  let appToken = null;
  const checkSubscriptions = res => {
    appToken = 'Bearer ' + res.access_token;

    const options = {
      url: 'https://api.twitch.tv/helix/eventsub/subscriptions',
      headers: {
        Authorization: appToken,
        'Client-Id': process.env.client_id
      },
      json: true
    };

    return request(options);
  };

  const createSubscription = res => {
    // Check if subscription both exists and has at least 24 hours remaining on the lease
    const callback = `${process.env.domain}?channel=${webhook.channel}&type=${webhook.type}`; 

    // Remove failed subscriptions
    var XMLHttpRequest = require('xhr2');
    res.data.forEach(function (item, index) {
        if (item["status"] === "webhook_callback_verification_failed") {
            var xhr1 = new XMLHttpRequest();
            xhr1.open('DELETE', `https://api.twitch.tv/helix/eventsub/subscriptions?id=${item["id"]}`, true);
            xhr1.send();
        }
    });

    const sub = res.data.find(item => item["transport"]["callback"] === callback && item["status"] === "enabled");
    if (sub && (new Date() - new Date(sub.created_at)) / 3600000 < 24) {
        console.warn("stream.online callback already exists");
    }
    else {
        console.warn("stream.online callback did not exist. Registering...");

        const options = {
          url: 'https://api.twitch.tv/helix/eventsub/subscriptions',
          method: 'POST',
          headers: {
            Authorization: appToken,
            'Content-Type': 'application/json',
            'Client-Id': process.env.client_id
          },
          body: JSON.stringify({
            'type': webhook.type,
            'version': '1',
            'condition': {'broadcaster_user_id': webhook.channel},
            'transport': {'method': 'webhook', 'callback': callback, 'secret': process.env.webhook_secret}
          })
        };
        request(options);
    }

    // Check if subscription both exists and has at least 24 hours remaining on the lease
    const offlineCallback = `${process.env.domain}?channel=${webhook.channel}&type=stream.offline`; 

    const sub2 = res.data.find(item => item["transport"]["callback"] === offlineCallback && item["status"] === "enabled");
    if (sub2 && (new Date() - new Date(sub2.created_at)) / 3600000 < 24) {
        console.warn("stream.offline callback already exists");
        return;
    }

    console.warn("stream.offline callback did not exist. Registering...");

    const options2 = {
      url: 'https://api.twitch.tv/helix/eventsub/subscriptions',
      method: 'POST',
      headers: {
        Authorization: appToken,
        'Content-Type': 'application/json',
        'Client-Id': process.env.client_id
      },
      body: JSON.stringify({
        'type': 'stream.offline',
        'version': '1',
        'condition': {'broadcaster_user_id': webhook.channel},
        'transport': {'method': 'webhook', 'callback': offlineCallback, 'secret': process.env.webhook_secret}
      })
    };

    return request(options2);
  };

  return getAppToken()
    .then(checkSubscriptions)
    .then(createSubscription)
    .then(res => ({ statusCode: 200 }))
    .catch(err => {
      console.warn(err);
      return { statusCode: 500 };
    });
};
