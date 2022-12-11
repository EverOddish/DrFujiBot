const crypto = require('crypto');
const AWS = require('aws-sdk');

exports.handler = async event => {
  console.warn(JSON.stringify(event));

  const MESSAGE_TYPE = 'Twitch-Eventsub-Message-Type';
  const MESSAGE_TYPE_VERIFICATION = 'webhook_callback_verification';

  let notification = JSON.parse(event.body);

  if (MESSAGE_TYPE_VERIFICATION === event.headers[MESSAGE_TYPE.toLowerCase()]) {
      console.warn(notification.challenge)
      console.warn(notification.challenge.length)
      return { statusCode: 200,
               body: notification.challenge,
             };
  }

  const verify = () => {
    const expected = event.headers['twitch-eventsub-message-signature'];
    const value = event.headers['twitch-eventsub-message-id'] + event.headers['twitch-eventsub-message-timestamp'] + event.body;
    const calculated = 'sha256=' + crypto.createHmac('sha256', process.env.webhook_secret).update(value).digest('hex');
    return expected === calculated;
  };

  // If verification fails we log the failure and return a response to the request
  if (!verify()) {
    console.warn('Verification failed', event);
    return { statusCode: 200 };
  }

  if (notification["subscription"]["type"] == "stream.online") {
      if (notification["event"]["broadcaster_user_login"] == "pokemonchallenges") {
          // Start DrFujiBotIRC
          console.warn("Detected PokemonChallenges is live")
      }
  }

  return { statusCode: 200 };
};
